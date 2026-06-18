-- query4.sql
-- Lists title, rating, and budget of movie(s) with the highest rating
-- We select title , rating , and budget from movies which have the maximum rating among all movies and then order them by budget in ascending order. 


SELECT title, rating, budget
FROM Movies
WHERE rating = (SELECT MAX(rating) FROM Movies)
ORDER BY budget ASC;