-- query11.sql
-- Lists Nolan’s movies longer than 120 minutes
-- first join director table with movies to find which director directed which movies, then filter it to only select rows with director = christopher nolan and duration is longer than 120 minutes, lastly it is ordered by movie_id in descending order

SELECT 
  m.movie_id,m.title,
  m.release_date,m.duration,
  m.director_id,m.rating,
  m.genre_id,m.budget
FROM Movies m
JOIN Directors d ON m.director_id = d.director_id
WHERE d.name = 'Christopher' AND d.surname = 'Nolan'
  AND m.duration > 120
ORDER BY m.movie_id DESC;