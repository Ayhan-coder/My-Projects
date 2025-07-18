-- query14.sql
-- Lists 'post-2010' movies not directed by Christopher Nolan
-- Directors and movies tables are joined on director id to find the movies directed by each director. Then, we filter the rows to only select those with years later than 2010 and not directed by Christopher nolan. Lastly, sort it by movie_id in ascending order.

SELECT m.movie_id, m.title, d.name AS director_name, d.surname AS director_surname
FROM Movies m
JOIN Directors d ON m.director_id = d.director_id
WHERE STR_TO_DATE(m.release_date, '%d.%m.%Y') >= '2010-01-01'
  AND NOT (d.name = 'Christopher' AND d.surname = 'Nolan')
ORDER BY m.movie_id ASC;