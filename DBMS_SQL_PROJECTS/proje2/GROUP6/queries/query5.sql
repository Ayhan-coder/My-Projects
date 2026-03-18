-- query5.sql
-- Calculates the average rating across all movies
-- We calculate an average rating which is rounded to 3 digits and it is named as average_rating.

SELECT ROUND(AVG(rating), 3) AS average_rating
FROM Movies;