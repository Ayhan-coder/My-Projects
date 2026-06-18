-- query3.sql
-- Shows all details of movies that have the lowest rating
-- We calculate the minimum rating of any movie in the movies table. Then, we filter the table to find the movies with the lowest rating and select their details.

SELECT 
  movie_id,title,
  DATE_FORMAT(STR_TO_DATE(release_date, '%d.%m.%Y'), '%d.%m.%Y') AS release_date,
  duration,director_id,rating,genre_id,budget
FROM Movies
WHERE rating = (SELECT MIN(rating) FROM Movies);