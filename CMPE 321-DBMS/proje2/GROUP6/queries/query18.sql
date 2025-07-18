-- query18.sql
-- Finds directors who have worked across multiple genres
-- First, we join directors tables with movies table on director id to find which director directed which movies. Then, we group these results by director id with the condition of containing more than one genre. Lastly, it is sorted by genre_count in descending order.


SELECT d.name, d.surname, COUNT(DISTINCT m.genre_id) AS genre_count
FROM Directors d
JOIN Movies m ON d.director_id = m.director_id
GROUP BY d.director_id, d.name, d.surname
HAVING genre_count > 1
ORDER BY genre_count DESC;