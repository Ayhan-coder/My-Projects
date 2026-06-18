-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS cmpe_321;

-- Switch to this database
USE cmpe_321;

-- Tables that are not dependent on others
-- Table for chess titles like Grandmaster or FIDE Master
CREATE TABLE TITLE (
    title_id INT AUTO_INCREMENT PRIMARY KEY,
    title_name VARCHAR(255) NOT NULL UNIQUE
);

-- Table for sponsors
CREATE TABLE SPONSOR (
    sponsor_id INT AUTO_INCREMENT PRIMARY KEY,
    sponsor_name VARCHAR(255) NOT NULL UNIQUE
);

-- Main user table (used by all user types)
CREATE TABLE USER (
    username VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    user_type ENUM('PLAYER', 'COACH', 'ARBITER', 'DATABASE_MANAGER') NOT NULL
);

CREATE TABLE DATABASE_MANAGER (
    username VARCHAR(255) PRIMARY KEY,
    FOREIGN KEY (username) REFERENCES USER(username) ON DELETE CASCADE
);

-- Table for coaches (subtype of USER)
CREATE TABLE COACH (
    username VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    surname VARCHAR(255) NOT NULL,
    nationality VARCHAR(100) NOT NULL,
    FOREIGN KEY (username) REFERENCES USER(username) ON DELETE CASCADE
);

-- Table for arbiters (subtype of USER)
CREATE TABLE ARBITER (
    username VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    surname VARCHAR(255) NOT NULL,
    nationality VARCHAR(100) NOT NULL,
    experience_level ENUM('Beginner', 'Intermediate', 'Advanced','Expert') NOT NULL,
    FOREIGN KEY (username) REFERENCES USER(username) ON DELETE CASCADE
);


-- Table for players (subtype of USER)
CREATE TABLE PLAYER (
    username VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    surname VARCHAR(255) NOT NULL,
    nationality VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    elo_rating INT CHECK (elo_rating > 1000),
    fide_id VARCHAR(255),
    title_id INT,
    FOREIGN KEY (username) REFERENCES USER(username) ON DELETE CASCADE,
    FOREIGN KEY (title_id) REFERENCES TITLE(title_id)
);

-- Table linking coaches to certificates (many-to-many)
CREATE TABLE COACH_CERTIFICATE (
    username VARCHAR(255),
    certificate_name VARCHAR(255),
    PRIMARY KEY (username, certificate_name),
    FOREIGN KEY (username) REFERENCES COACH(username) ON DELETE CASCADE
);

-- Table linking arbiters to certificates (many-to-many)
CREATE TABLE ARBITER_CERTIFICATE (
    username VARCHAR(255),
    certificate_name VARCHAR(255),
    PRIMARY KEY (username, certificate_name),
    FOREIGN KEY (username) REFERENCES ARBITER(username) ON DELETE CASCADE
);

-- Table for chess teams
CREATE TABLE TEAM (
    team_id INT AUTO_INCREMENT PRIMARY KEY,
    team_name VARCHAR(255) NOT NULL,
    coach_username VARCHAR(255) UNIQUE NOT NULL,
    contract_start DATE NOT NULL,
    contract_finish DATE NOT NULL,
    sponsor_id INT,
    FOREIGN KEY (coach_username) REFERENCES COACH(username) ON DELETE CASCADE,
    FOREIGN KEY (sponsor_id) REFERENCES SPONSOR(sponsor_id)
);

-- Many-to-many relationship between players and teams
CREATE TABLE PLAYER_TEAM (
    player_username VARCHAR(255),
    team_id INT,
    PRIMARY KEY (player_username, team_id),
    FOREIGN KEY (player_username) REFERENCES PLAYER(username) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES TEAM(team_id) ON DELETE CASCADE
);

-- Table for physical halls where matches happen
CREATE TABLE HALL (
    hall_id INT AUTO_INCREMENT PRIMARY KEY,
    hall_name VARCHAR(255) NOT NULL,
    hall_country VARCHAR(255),
    hall_capacity INT
);

-- Table for chess tables in each hall
CREATE TABLE CHESS_TABLE (
    table_id INT AUTO_INCREMENT PRIMARY KEY,
    hall_id INT NOT NULL,
    FOREIGN KEY (hall_id) REFERENCES HALL(hall_id) ON DELETE CASCADE
);


-- Table for matches played in tournaments
CREATE TABLE MATCH_ (
    match_id INT AUTO_INCREMENT PRIMARY KEY,
    hall_id INT NOT NULL,
    table_id INT NOT NULL,
    time_slot INT NOT NULL CHECK (time_slot BETWEEN 1 AND 4),
    match_date DATE NOT NULL,
    white_player_team INT NOT NULL,
    white_player VARCHAR(255),
    black_player_team INT NOT NULL,
    black_player VARCHAR(255),
    result ENUM('white wins', 'black wins', 'draw'),
    assigned_arbiter VARCHAR(255) NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 10) NULL,
    UNIQUE (hall_id, table_id, match_date, time_slot),
    UNIQUE (match_date, time_slot, white_player),
    UNIQUE (match_date, time_slot, black_player),
    UNIQUE (match_date, time_slot, assigned_arbiter),
    FOREIGN KEY (hall_id) REFERENCES HALL(hall_id),
    FOREIGN KEY (table_id) REFERENCES CHESS_TABLE(table_id),
    FOREIGN KEY (white_player_team) REFERENCES TEAM(team_id),
    FOREIGN KEY (white_player) REFERENCES PLAYER(username),
    FOREIGN KEY (black_player_team) REFERENCES TEAM(team_id),
    FOREIGN KEY (black_player) REFERENCES PLAYER(username),
    FOREIGN KEY (assigned_arbiter) REFERENCES ARBITER(username) ON DELETE CASCADE,
    CHECK (white_player != black_player),
    CHECK (white_player_team != black_player_team)
);




DELIMITER $$

CREATE TRIGGER check_match_constraints
BEFORE INSERT ON MATCH_
FOR EACH ROW
BEGIN
    DECLARE slot1 INT;
    DECLARE slot2 INT;

    SET slot1 = NEW.time_slot;
    SET slot2 = slot1 + 1;

    -- Validate time_slot range
    IF slot1 < 1 OR slot1 > 3 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid time_slot. Matches must start in slots 1 to 3.';
    END IF;

    -- Check if the table belongs to the specified hall
    IF NOT EXISTS (
        SELECT 1 FROM CHESS_TABLE
        WHERE table_id = NEW.table_id AND hall_id = NEW.hall_id
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid table: This table does not belong to the specified hall.';
    END IF;

    -- Check hall + table availability
    IF EXISTS (
        SELECT 1 FROM MATCH_
        WHERE match_date = NEW.match_date
          AND hall_id = NEW.hall_id
          AND table_id = NEW.table_id
          AND time_slot IN (slot1, slot2)
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Conflict: Hall/table already occupied in one of the time slots.';
    END IF;
    -- Check arbiter availability
    IF EXISTS (
        SELECT 1 FROM MATCH_
        WHERE match_date = NEW.match_date
          AND assigned_arbiter = NEW.assigned_arbiter
          AND time_slot IN (slot1, slot2)
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Conflict: Arbiter is already assigned.';
    END IF;

END$$

DELIMITER ;



DELIMITER //

CREATE TRIGGER check_player_assignment_conflicts
BEFORE UPDATE ON MATCH_
FOR EACH ROW
BEGIN
    -- Check: white_player must belong to white_player_team
    IF NEW.white_player IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1
            FROM PLAYER_TEAM
            WHERE player_username = NEW.white_player
              AND team_id = NEW.white_player_team
        ) THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'White player is not a member of the assigned white team';
        END IF;
        
        -- Check: white_player must not have another match at same date and time
        IF EXISTS (
            SELECT 1
            FROM MATCH_
            WHERE match_id != NEW.match_id
              AND match_date = NEW.match_date
              AND (
                    time_slot = NEW.time_slot OR
                    time_slot = NEW.time_slot + 1 OR
                    time_slot + 1 = NEW.time_slot
                  )
              AND (white_player = NEW.white_player OR black_player = NEW.white_player)
        ) THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'White player has another match that overlaps with this time slot';
        END IF;
    END IF;

    -- Check: black_player must belong to black_player_team
    IF NEW.black_player IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1
            FROM PLAYER_TEAM
            WHERE player_username = NEW.black_player
              AND team_id = NEW.black_player_team
        ) THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Black player is not a member of the assigned black team';
        END IF;

        -- Check: black_player must not have another match at same date and time
        IF EXISTS (
            SELECT 1
            FROM MATCH_
            WHERE match_id != NEW.match_id
              AND match_date = NEW.match_date
              AND (
                    time_slot = NEW.time_slot OR
                    time_slot = NEW.time_slot + 1 OR
                    time_slot + 1 = NEW.time_slot
                  )
              AND (white_player = NEW.black_player OR black_player = NEW.black_player)
        ) THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Black player has another match that overlaps with this time slot';
        END IF;
    END IF;

    -- Check: white and black players must be different
    IF NEW.white_player IS NOT NULL AND NEW.black_player IS NOT NULL THEN
        IF NEW.white_player = NEW.black_player THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'A player cannot play as both white and black';
        END IF;
    END IF;
END;
//

DELIMITER ;



DELIMITER $$

CREATE TRIGGER prevent_same_team_match
BEFORE INSERT ON MATCH_
FOR EACH ROW
BEGIN
    IF NEW.white_player_team = NEW.black_player_team THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid Match: Players are on the same team.';
    END IF;
END$$

DELIMITER ;



DELIMITER $$

CREATE TRIGGER prevent_invalid_rating
BEFORE UPDATE ON MATCH_
FOR EACH ROW
BEGIN
    IF NEW.rating IS NOT NULL AND OLD.rating IS NOT NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'This match has already been rated.';
    END IF;

    IF NEW.rating IS NOT NULL AND NEW.match_date > CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Match cannot be rated before it occurs.';
    END IF;
END$$

DELIMITER ;

DELIMITER $$

CREATE TRIGGER prevent_overlapping_coach_contracts
BEFORE INSERT ON TEAM
FOR EACH ROW
BEGIN
    DECLARE overlap_count INT;

    SELECT COUNT(*) INTO overlap_count
    FROM TEAM
    WHERE coach_username = NEW.coach_username
      AND (
          NEW.contract_start <= contract_finish AND
          NEW.contract_finish >= contract_start
      );

    IF overlap_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Coach already has a contract that overlaps with this period.';
    END IF;
END$$

DELIMITER ;




