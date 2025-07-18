-- query17.sql
-- Lists long, highly-rated movies and their directors
-- First, we join the movie table with directors again to find which director directed which movie. Then, we only filter the rows with duration greater than 150 rating greater than 8. Also, we used a CONCAT statement to merge the name and the surname of a director into one variable and the result is sorted by this variable in descending order.


SELECT m.movie_id, m.title AS movie_name, m.duration, m.rating, CONCAT(d.name, ' ', d.surname) AS director_name
FROM Movies m
JOIN Directors d ON m.director_id = d.director_id
WHERE m.duration > 150 AND m.rating > 8
ORDER BY d.name DESC;