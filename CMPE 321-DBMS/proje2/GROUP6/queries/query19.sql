-- query19.sql
-- Finds the genre with the highest average movie rating
-- first we join movies and genres tables on genre_id. Then, we group these rows by their genre ids so that we have groups of movies of each genre. Then, we calculate the avg rating of these groups using the AVG statement and sort it by these averages in the descending order and only limit it to 1 row so that we only have the row with the max avg rating.


SELECT g.genre_id, g.genre_name, ROUND(AVG(m.rating), 2) AS average_rating
FROM Movies m
JOIN Genres g ON m.genre_id = g.genre_id
GROUP BY g.genre_id, g.genre_name
ORDER BY average_rating DESC
LIMIT 1;
