-- query2.sql
-- Lists all movies released before 2024, formatted and sorted by date descending
--  We select movie_id,title,duration,rating,director_id of movies which have a release date of before 2024/01/01 in date format as date and we order by release date in descending order.

SELECT   movie_id,title,duration,rating,director_id,
  DATE_FORMAT(STR_TO_DATE(release_date, '%d.%m.%Y'), '%d/%m/%Y') AS date
FROM Movies
WHERE STR_TO_DATE(release_date, '%d.%m.%Y') < '2024-01-01'
ORDER BY STR_TO_DATE(release_date, '%d.%m.%Y') DESC;