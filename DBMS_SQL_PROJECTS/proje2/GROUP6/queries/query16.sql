-- query16.sql
-- Lists each actor with their average movie rating, sorted descending
-- First join cast and movie tables to have the information of both actors ids and ratings. We also used the "DISTINCT" keyword since there were duplicate actor id,movie id pairs in the data. Then, we group these by actor ids to Average the ratings of each movie an actor played in. Also, it is sorted by average rating in descending order.


SELECT a.name, a.surname, ROUND(AVG(sub.rating), 2) AS average_rating
FROM Actors_and_Actresses a
JOIN (
    SELECT DISTINCT c.actor_id, c.movie_id, m.rating
    FROM Cast c
    JOIN Movies m ON c.movie_id = m.movie_id
) AS sub ON a.actor_id = sub.actor_id
GROUP BY a.actor_id, a.name, a.surname
ORDER BY average_rating DESC;