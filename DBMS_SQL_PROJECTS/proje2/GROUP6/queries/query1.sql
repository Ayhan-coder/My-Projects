-- query1.sql
-- Returns the total number of movies in the database.
-- We calculate the total number of all movies in the database by using the COUNT statement after selecting all movies from the movies table.

SELECT COUNT(*) AS movie_count
FROM Movies;