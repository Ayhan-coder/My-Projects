-- query13.sql
-- Finds directors with the most movies per genre
-- First, prepare a table with directors and their movie count on each genre. then, another query to find out the max number of movies directed for each director,genre pair. Lastly, use this max count to only filter rows with max number of movies directed for each genre,director pair.

SELECT g.genre_name, d.name, d.surname, t.cnt AS directed_count
FROM (
    SELECT m.genre_id, m.director_id, COUNT(*) AS cnt
    FROM Movies m
    GROUP BY m.genre_id, m.director_id
) t
JOIN Genres g ON t.genre_id = g.genre_id
JOIN Directors d ON t.director_id = d.director_id
WHERE (t.genre_id, t.cnt) IN (
    SELECT genre_id, MAX(cnt)
    FROM (
        SELECT genre_id, director_id, COUNT(*) AS cnt
        FROM Movies
        GROUP BY genre_id, director_id
    ) x
    GROUP BY genre_id
)
ORDER BY g.genre_name, d.surname;