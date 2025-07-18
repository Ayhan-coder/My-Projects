from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
import hashlib
import pandas as pd
from datetime import datetime
from datetime import date
import re

app = Flask(__name__)
app.secret_key = '321'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="cmpe_321"
)
cursor = db.cursor(dictionary=True)

# -------- Password hashing --------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

import re

def is_valid_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character."
    return True, ""


# -------- Home and login --------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])

        cursor.execute("SELECT * FROM USER WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()

        if user:
            session['username'] = user['username']
            session['role'] = user['user_type']
            return redirect('/dashboard')
        else:
            flash('Invalid credentials')
            return redirect('/')
    
    return render_template('login.html')

# -------- Role-based dashboard --------
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')
    
    role = session['role']
    return render_template('dashboard.html', role=role, username=session['username'])
@app.route('/create_match', methods=['GET', 'POST'])
def create_match():
    if 'username' not in session or session['role'] != 'COACH':
        return redirect('/')

    coach_username = session['username']

    cursor.execute("SELECT team_id FROM TEAM WHERE coach_username = %s", (coach_username,))
    row = cursor.fetchone()
    if not row:
        flash("You don't manage any team.")
        return redirect('/dashboard')

    coach_team_id = row['team_id']

    if request.method == 'POST':
        match_date = request.form['match_date']
        time_slot = request.form['time_slot']
        hall_id = request.form['hall_id']
        table_id = request.form['table_id']
        opponent_team_id = request.form['black_team']
        arbiter_username = request.form['arbiter']

        data = (
            match_date,
            time_slot,
            hall_id,
            table_id,
            None,  # white_player 
            None,  # black_player 
            coach_team_id,
            opponent_team_id,
            arbiter_username,
            None,  # 
            None  # rating 
        )

        try:
            query = """
            INSERT INTO MATCH_ (
                match_date, time_slot, hall_id, table_id,
                white_player, black_player, white_player_team, black_player_team,
                assigned_arbiter, result, rating
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, data)
            db.commit()
            flash("Match created successfully.")
            return redirect('/dashboard')
        except mysql.connector.Error as err:
            flash(f"Match creation failed: {err.msg}")
            return redirect('/create_match')

    cursor.execute("SELECT team_id, team_name FROM TEAM WHERE coach_username != %s", (coach_username,))
    opponent_teams = cursor.fetchall()

    cursor.execute("SELECT username FROM ARBITER")
    arbiters = cursor.fetchall()

    return render_template('match_form.html', opponent_teams=opponent_teams, arbiters=arbiters)



# -------- Logout --------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')



@app.route('/assign_players', methods=['GET', 'POST'])
def assign_players():
    if 'username' not in session or session['role'] != 'COACH':
        return redirect('/')

    coach_username = session['username']

    if request.method == 'POST':
        match_id = request.form['match_id']
        player = request.form['player']

        
        cursor.execute("SELECT team_id FROM TEAM WHERE coach_username = %s", (coach_username,))
        team = cursor.fetchone()
        if not team:
            flash("Coach has no assigned team.")
            return redirect('/assign_players')
        coach_team_id = team['team_id']

        # Get match info
        cursor.execute("SELECT white_player_team, black_player_team, white_player, black_player FROM MATCH_ WHERE match_id = %s", (match_id,))
        match = cursor.fetchone()
        if not match:
            flash("Match not found.")
            return redirect('/assign_players')

        white_team = match['white_player_team']
        black_team = match['black_player_team']

        # coach has to be part of a team in the match
        if coach_team_id not in (white_team, black_team):
            flash("You are not authorized to assign a player to this match.")
            return redirect('/assign_players')

        # Check that player belongs to coach's team
        cursor.execute("SELECT * FROM PLAYER_TEAM WHERE player_username = %s AND team_id = %s", (player, coach_team_id))
        if not cursor.fetchone():
            flash("Player is not in your team.")
            return redirect('/assign_players')

        # Assign the player to the correct side
        try:
            if coach_team_id == white_team:
                if match['white_player']:
                    flash("White player already assigned.")
                else:
                    cursor.execute("UPDATE MATCH_ SET white_player = %s WHERE match_id = %s", (player, match_id))
                    db.commit()
                    flash("Player assigned as White.")
            elif coach_team_id == black_team:
                if match['black_player']:
                    flash("Black player already assigned.")
                else:
                    cursor.execute("UPDATE MATCH_ SET black_player = %s WHERE match_id = %s", (player, match_id))
                    db.commit()
                    flash("Player assigned as Black.")
        except Exception as e:
            flash(f"Error: {str(e)}")

        return redirect('/dashboard')

    # fetch matches coach is part of and needs assignment
    cursor.execute("""
        SELECT m.match_id, DATE_FORMAT(m.match_date, '%d.%m.%Y') AS formatted_date, t1.team_name AS white_team_name,
               t2.team_name AS black_team_name, m.white_player, m.black_player
        FROM MATCH_ m
        JOIN TEAM t1 ON m.white_player_team = t1.team_id
        JOIN TEAM t2 ON m.black_player_team = t2.team_id
        WHERE (t1.coach_username = %s OR t2.coach_username = %s)
          AND (m.white_player IS NULL OR m.black_player IS NULL)
    """, (coach_username, coach_username))
    matches = cursor.fetchall()

    # Get list of players from coach’s team
    cursor.execute("""
        SELECT p.player_username
        FROM PLAYER_TEAM p
        JOIN TEAM t ON p.team_id = t.team_id
        WHERE t.coach_username = %s
    """, (coach_username,))
    players = cursor.fetchall()

    return render_template('assign_players.html', matches=matches, players=players)







@app.route('/delete_match', methods=['GET', 'POST'])
def delete_match():
    if 'username' not in session or session['role'] != 'COACH':
        return redirect('/')

    coach_username = session['username']

    if request.method == 'POST':
        match_id = request.form['match_id']

        
        cursor.execute("""
            SELECT m.match_id
            FROM MATCH_ m
            JOIN TEAM t1 ON m.white_player_team = t1.team_id
            JOIN TEAM t2 ON m.black_player_team = t2.team_id
            WHERE m.match_id = %s AND (t1.coach_username = %s OR t2.coach_username = %s)
        """, (match_id, coach_username, coach_username))
        match = cursor.fetchone()

        if not match:
            flash("You do not have permission to delete this match.")
            return redirect('/delete_match')

        try:
            cursor.execute("DELETE FROM MATCH_ WHERE match_id = %s", (match_id,))
            db.commit()
            flash("Match deleted successfully.")
        except Exception as e:
            flash(f"Error deleting match: {str(e)}")

        return redirect('/dashboard')


    cursor.execute("""
        SELECT m.match_id, m.match_date, m.time_slot,
               t1.team_name AS white_team_name, t2.team_name AS black_team_name
        FROM MATCH_ m
        JOIN TEAM t1 ON m.white_player_team = t1.team_id
        JOIN TEAM t2 ON m.black_player_team = t2.team_id
        WHERE t1.coach_username = %s OR t2.coach_username = %s
    """, (coach_username, coach_username))
    matches = cursor.fetchall()

    return render_template('delete_match.html', matches=matches)


@app.route('/rename_hall', methods=['GET', 'POST'])
def rename_hall():
    if 'username' not in session or session['role'] != 'DATABASE_MANAGER':
        return redirect('/')

    # get the list of halls
    if request.method == 'GET':
        cursor.execute("SELECT hall_id, hall_name FROM HALL")
        halls = cursor.fetchall()
        return render_template('rename_hall.html', halls=halls)

    # rename hall name
    old_hall_id = request.form['hall_id']
    new_name = request.form['new_name'].strip()

    if not new_name:
        flash("New name cannot be empty.")
        return redirect('/rename_hall')

    try:
        cursor.execute("UPDATE HALL SET hall_name = %s WHERE hall_id = %s", (new_name, old_hall_id))
        db.commit()
        flash("Hall name updated successfully.")
    except Exception as e:
        flash(f"Error updating hall name: {str(e)}")

    return redirect('/dashboard')


@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if 'username' not in session or session['role'] != 'DATABASE_MANAGER':
        return redirect('/')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role'].upper()

        name = request.form['name']
        surname = request.form['surname']
        nationality = request.form['nationality']

        # check if password is valid or not
        valid, msg = is_valid_password(password)
        if not valid:
            flash(f"User creation failed: {msg}")
            return redirect('/create_user')

        try:
            # create a new user
            cursor.execute("INSERT INTO USER (username, password, role) VALUES (%s, %s, %s)", (username, password, role))

            # create an entry on specific user role
            if role == 'COACH':
                cursor.execute("INSERT INTO COACH (username, name, surname, nationality) VALUES (%s, %s, %s, %s)",
                               (username, name, surname, nationality))

            elif role == 'ARBITER':
                experience = request.form['experience_level']
                cursor.execute("INSERT INTO ARBITER (username, name, surname, nationality, experience_level) VALUES (%s, %s, %s, %s, %s)",
                               (username, name, surname, nationality, experience))

            elif role == 'PLAYER':
                dob = request.form['date_of_birth']
                elo = request.form['elo_rating']
                fide = request.form.get('fide_id') or None
                title_id = request.form.get('title_id') or None
                cursor.execute("""
                    INSERT INTO PLAYER (username, name, surname, nationality, date_of_birth, elo_rating, fide_id, title_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (username, name, surname, nationality, dob, elo, fide, title_id))

            else:
                flash("Invalid role specified.")
                return redirect('/create_user')

            db.commit()
            flash("User created successfully.")
        except mysql.connector.Error as err:
            db.rollback()
            flash(f"User creation failed: {err.msg}")

        return redirect('/create_user')

    return render_template('create_user.html')


@app.route('/view_halls')
def view_halls():
    if 'username' not in session or session['role'] != 'COACH':
        return redirect('/')

    cursor.execute("SELECT hall_id, hall_name, hall_country, hall_capacity FROM HALL")
    halls = cursor.fetchall()

    return render_template('view_halls.html', halls=halls)




@app.route('/submit_ratings', methods=['GET', 'POST'])
def submit_ratings():
    if 'username' not in session or session['role'] != 'ARBITER':
        return redirect('/')

    if request.method == 'POST':
        match_id = request.form['match_id']
        rating = request.form['rating']

        # Check validity
        cursor.execute("""
            SELECT * FROM MATCH_
            WHERE match_id = %s AND assigned_arbiter = %s
        """, (match_id, session['username']))
        match = cursor.fetchone()

        if not match:
            flash("You are not assigned to this match.")
            return redirect('/submit_ratings')

        if match['rating'] is not None:
            flash("This match has already been rated.")
            return redirect('/submit_ratings')

        if match['match_date'] > date.today():
            flash("You cannot rate a future match.")
            return redirect('/submit_ratings')

        try:
            cursor.execute("UPDATE MATCH_ SET rating = %s WHERE match_id = %s", (rating, match_id))
            db.commit()
            flash("Rating submitted successfully.")
        except Exception as e:
            flash(f"Failed to submit rating: {str(e)}")

        return redirect('/dashboard')

    # show unrated past matches assigned to this arbiter
    cursor.execute("""
        SELECT match_id, match_date, white_player, black_player
        FROM MATCH_
        WHERE assigned_arbiter = %s AND rating IS NULL AND match_date <= CURDATE()
    """, (session['username'],))
    matches = cursor.fetchall()

    return render_template('submit_ratings.html', matches=matches)


@app.route('/arbiter_stats')
def arbiter_stats():
    if 'username' not in session or session['role'] != 'ARBITER':
        return redirect('/')

    cursor.execute("""
        SELECT COUNT(*) AS match_count, AVG(rating) AS avg_rating
        FROM MATCH_
        WHERE assigned_arbiter = %s AND rating IS NOT NULL
    """, (session['username'],))
    stats = cursor.fetchone()

    return render_template('arbiter_stats.html', stats=stats)

@app.route('/assigned_matches')
def assigned_matches():
    if 'username' not in session or session['role'] != 'ARBITER':
        return redirect('/')

    cursor.execute("""
        SELECT m.match_id, DATE_FORMAT(m.match_date, '%d.%m.%Y') AS match_date, m.time_slot, h.hall_name, t1.team_name AS white_team,
               t2.team_name AS black_team, m.white_player, m.black_player, m.result, m.rating
        FROM MATCH_ m
        JOIN HALL h ON m.hall_id = h.hall_id
        JOIN TEAM t1 ON m.white_player_team = t1.team_id
        JOIN TEAM t2 ON m.black_player_team = t2.team_id
        WHERE m.assigned_arbiter = %s
        ORDER BY m.match_date, m.time_slot
    """, (session['username'],))
    
    matches = cursor.fetchall()
    return render_template('assigned_matches.html', matches=matches)




@app.route('/player_stats')
def player_stats():
    if 'username' not in session or session['role'] != 'PLAYER':
        return redirect('/')

    username = session['username']

    # Opponents played against
    cursor.execute("""
        SELECT DISTINCT
            CASE
                WHEN white_player = %s THEN black_player
                WHEN black_player = %s THEN white_player
            END AS opponent
        FROM MATCH_
        WHERE white_player = %s OR black_player = %s
    """, (username, username, username, username))
    opponents = cursor.fetchall()


    cursor.execute("""
        SELECT opponent, COUNT(*) AS games_played
        FROM (
            SELECT CASE
                    WHEN white_player = %s THEN black_player
                    WHEN black_player = %s THEN white_player
                   END AS opponent
            FROM MATCH_
            WHERE white_player = %s OR black_player = %s
        ) AS sub
        GROUP BY opponent
        HAVING opponent IS NOT NULL
        ORDER BY games_played DESC
    """, (username, username, username, username))
    co_players = cursor.fetchall()

    most_freq = []
    if co_players:
        top_count = co_players[0]['games_played']
        most_freq = [cp['opponent'] for cp in co_players if cp['games_played'] == top_count]

    # Get ELO of most frequent co-player
    if most_freq:
        placeholders = ','.join(['%s'] * len(most_freq))
        cursor.execute(f"""
            SELECT AVG(elo_rating) AS avg_elo
            FROM PLAYER
            WHERE username IN ({placeholders})
        """, tuple(most_freq))
        avg_elo = cursor.fetchone()['avg_elo']
    else:
        avg_elo = None
    return render_template('player_stats.html', opponents=opponents, most_freq=most_freq, avg_elo=avg_elo)


#FOR DB MANAGERS
df = pd.read_excel('ChessDB_updated.xlsx', sheet_name='DBManagers')  # change 'users' if needed

for index, row in df.iterrows():
    username = row['username']
    password = row['password']
    password_hash = hash_password(str(password))
    user_type = 'DATABASE_MANAGER'
    
    cursor.execute("""
        INSERT IGNORE INTO USER (username, password, user_type)
        VALUES (%s, %s, %s)
    """, (username, password_hash, user_type))

    cursor.execute("INSERT IGNORE INTO DATABASE_MANAGER (username) VALUES (%s)", (username,))

#for titles----------
df = pd.read_excel('ChessDB_updated.xlsx', sheet_name='Titles')  # change 'users' if needed

for index, row in df.iterrows():
    title_id = int(row['title_id'])
    title_name = row['title_name']
    cursor.execute("""
        INSERT IGNORE INTO Title (title_id, title_name)
        VALUES (%s, %s)
    """, (title_id, title_name))

#FOR PLAYERS----
df = pd.read_excel('ChessDB_updated.xlsx', sheet_name='Players')  # change 'users' if needed

for index, row in df.iterrows():
    username = row['username']
    password = row['password']
    name = row['name']
    surname = row['surname']
    nationality = row['nationality']
    password_hash = hash_password(str(password))
    user_type = "PLAYER"
    # Insert into USER
    cursor.execute("""
        INSERT IGNORE INTO USER (username, password, user_type)
        VALUES (%s, %s, %s)
    """, (username, password_hash, user_type))

   
    dob_raw = row['date_of_birth']
    if isinstance(dob_raw, str):
        dob = datetime.strptime(dob_raw, "%d-%m-%Y").date()
    else:
        dob = dob_raw.date()
    fide_id = row['fide_id'] if not pd.isna(row['fide_id']) else None
    elo_rating = int(row['elo_rating'])
    title_id = int(row['title_id']) if not pd.isna(row['title_id']) else None

    cursor.execute("""
        INSERT IGNORE INTO PLAYER (username,name,surname,nationality, date_of_birth, elo_rating, fide_id, title_id)
        VALUES (%s, %s, %s, %s, %s,%s,%s,%s)
    """, (username, name,surname,nationality, dob, elo_rating, fide_id, title_id))

 

#for coaches-------------
df = pd.read_excel('ChessDB_updated.xlsx', sheet_name='Coaches')  

for index, row in df.iterrows():
    username = row['username']
    password = row['password']
    name = row['name']
    surname = row['surname']
    nationality = row['nationality']
    password_hash = hash_password(str(password))
    user_type = "Coach"
    # Insert into USER
    cursor.execute("""
        INSERT IGNORE INTO USER (username, password, user_type)
        VALUES (%s, %s, %s)
    """, (username, password_hash, user_type))

   
    cursor.execute("INSERT IGNORE INTO COACH (username,name, surname, nationality) VALUES (%s,%s,%s,%s)", (username, name, surname, nationality))


#for arbiters-------------
df = pd.read_excel('ChessDB_updated.xlsx', sheet_name='Arbiters')  

for index, row in df.iterrows():
    username = row['username']
    password = row['password']
    name = row['name']
    surname = row['surname']
    nationality = row['nationality']
    password_hash = hash_password(str(password))
    user_type = "Arbiter"
    # Insert into USER
    cursor.execute("""
        INSERT IGNORE INTO USER (username, password, user_type)
        VALUES (%s, %s, %s)
    """, (username, password_hash, user_type))

    exp = row['experience_level']
    cursor.execute("""
        INSERT IGNORE INTO ARBITER (username, name, surname, nationality,  experience_level)
        VALUES (%s, %s,%s,%s,%s)
    """, (username, name, surname, nationality, exp))


#for sponsors---------------
df = pd.read_excel('ChessDB_updated.xlsx', sheet_name='Sponsors') 

for index, row in df.iterrows():
    sponsor_name = row['sponsor_name']
    sponsor_id = row['sponsor_id']

    cursor.execute("""
        INSERT IGNORE INTO Sponsor (sponsor_id,sponsor_name)
        VALUES (%s, %s)
    """, (sponsor_id,sponsor_name))



#for teams---------------
df = pd.read_excel('ChessDB_updated.xlsx', sheet_name='Teams')  
df2 = pd.read_excel('ChessDB_updated.xlsx', sheet_name='Coaches')  
for index, row in df.iterrows():
    row2 = df2.iloc[index]
    contract_start = row2['contract_start']
    contract_finish = row2['contract_finish']

    if isinstance(contract_start, str):
        contract_start = datetime.strptime(contract_start, "%d-%m-%Y").date()
    else:
        contract_start = contract_start.date()
    
    if isinstance(contract_finish, str):
        contract_finish = datetime.strptime(contract_finish, "%d-%m-%Y").date()
    else:
        contract_finish = contract_finish.date()
    team_id = row['team_id']
    team_name = row['team_name']
    sponsor_id = row['sponsor_id']
    # Insert into USER
    cursor.execute("""
        INSERT IGNORE INTO Team (team_id, team_name, coach_username, contract_start, contract_finish,sponsor_id)
        VALUES (%s, %s, %s,%s,%s,%s)
    """, (team_id, team_name, row2['username'],contract_start,contract_finish,sponsor_id))


#for coach_certificates---------------
df = pd.read_excel('ChessDB_updated.xlsx', sheet_name='CoachCertifications') 

for index, row in df.iterrows():
    coach_username = row['coach_username']
    certification = row['certification']

    cursor.execute("""
        INSERT IGNORE INTO COACH_CERTIFICATE (username,certificate_name)
        VALUES (%s, %s)
    """, (coach_username,certification))

#for player-teams--------------
df = pd.read_excel('ChessDB_updated.xlsx', sheet_name='PlayerTeams') 

for index, row in df.iterrows():
    username = row['username']
    team_id = row['team_id']

    cursor.execute("""
        INSERT IGNORE INTO PLAYER_TEAM (player_username,team_id)
        VALUES (%s, %s)
    """, (username,team_id))

#for arbiter certifications---------------
df = pd.read_excel('ChessDB_updated.xlsx', sheet_name='ArbiterCertifications')  

for index, row in df.iterrows():
    arbiter_username = row['username']
    certification = row['certification']

    cursor.execute("""
        INSERT IGNORE INTO ARBITER_CERTIFICATE (username,certificate_name)
        VALUES (%s, %s)
    """, (arbiter_username,certification))

#for HALLS---------------
df = pd.read_excel('ChessDB_updated.xlsx', sheet_name='Halls')  

for index, row in df.iterrows():
    hall_id = row['hall_id']
    hall_name = row['hall_name']
    country = row['country']
    capacity = row['capacity']
    cursor.execute("""
        INSERT IGNORE INTO Hall (hall_id,hall_name,hall_country,hall_capacity)
        VALUES (%s, %s,%s,%s)
    """, (hall_id,hall_name,country,capacity))

#for tables---------------
df = pd.read_excel('ChessDB_updated.xlsx', sheet_name='Tables') 

for index, row in df.iterrows():
    table_id = int(row['table_id'])
    hall_id = int(row['hall_id'])

    cursor.execute("""
        INSERT IGNORE  INTO CHESS_TABLE (table_id,hall_id)
        VALUES (%s, %s)
    """, (table_id,hall_id))

#for matches---------------
df = pd.read_excel('ChessDB_updated.xlsx', sheet_name='Matches')  
df2 = pd.read_excel('ChessDB_updated.xlsx', sheet_name='MatchAssignments') 
for index, row in df.iterrows():
    row2 = df2.iloc[index]
    match_id = row['match_id']
    match_date = row['date']
    if isinstance(match_date, str):
        match_date = datetime.strptime(match_date, "%d-%m-%Y").date()
    else:
        match_date = match_date.date()
    time_slot = row['time_slot']
    hall_id = row['hall_id']
    table_id = row['table_id']
    team1_id = row['team1_id']
    team2_id = row['team2_id']
    arbiter_username = row['arbiter_username']
    ratings = None if pd.isna(row['ratings']) else row['ratings']
    white_player = row2['white_player']
    black_player = row2['black_player']
    result = row2['result']
    cursor.execute("""
        INSERT IGNORE INTO MATCH_ (match_id,hall_id, table_id, time_slot,match_date, white_player_team,white_player,black_player_team,black_player,result,assigned_arbiter,rating)
        VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (match_id,hall_id,table_id,time_slot,match_date,team1_id,white_player,team2_id,black_player,result,arbiter_username,ratings))


db.commit()


# -------- Run server --------
if __name__ == '__main__':
    app.run(debug=True)

