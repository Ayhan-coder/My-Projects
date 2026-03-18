-- query12.sql
-- Finds the highest-rated movie for each year, with director info
-- First group the movies by year and find the max rating for every year, then use this information to join other tables on rating and year to only select movies from each year with max ratings. Lastly, sort it by year ascending order.
SELECT d.name, d.surname, m.title AS movie_name,
       YEAR(STR_TO_DATE(m.release_date, '%d.%m.%Y')) AS year,
       m.rating
FROM Movies m
JOIN Directors d ON m.director_id = d.director_id
JOIN (
    SELECT YEAR(STR_TO_DATE(release_date, '%d.%m.%Y')) AS y, MAX(rating) AS max_rating
    FROM Movies
    GROUP BY YEAR(STR_TO_DATE(release_date, '%d.%m.%Y'))
) sub ON YEAR(STR_TO_DATE(m.release_date, '%d.%m.%Y')) = sub.y
     AND m.rating = sub.max_rating
ORDER BY year ASC;