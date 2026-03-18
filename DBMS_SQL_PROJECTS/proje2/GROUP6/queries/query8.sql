-- query8.sql
-- Finds directors who have directed 3 or more movies
-- We select director name and surname from directors table after we join movies table based on equal director ids and we group by director name , id,and surname with the condition that there are 3 or more movies in the groups.

SELECT d.name, d.surname
FROM Directors d
JOIN Movies m ON d.director_id = m.director_id
GROUP BY d.director_id, d.name, d.surname
HAVING COUNT(*) >= 3;
