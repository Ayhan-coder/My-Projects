-- query15.sql
-- Finds the director who has directed the most movies in the database
-- First, join directors and movies tables to find which director directed which movies. Then we group them by director id to calculate the count of movies directed for each director.  Lastly, it is sorted by these counts in descending order and limited to only 1 row to show only the director with the maximum number of movies.


SELECT d.name, d.surname, COUNT(m.movie_id) AS number_of_movies
FROM Directors d
JOIN Movies m ON d.director_id = m.director_id
GROUP BY d.director_id, d.name, d.surname
ORDER BY number_of_movies DESC
LIMIT 1;