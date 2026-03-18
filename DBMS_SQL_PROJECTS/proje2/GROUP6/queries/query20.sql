-- query20.sql
-- Lists each 'actor/actress' with the number of distinct genres they appeared in,
-- and a 'TRUE/FALSE' flag indicating if they appeared in more than one genre.
-- First of all, we use Left join specifically on actors, cast, movies tables so that we can have rows with 0 genre_counts in our last result. If we had used normal join, we wouldn't be able to keep the rows with actors that hadn't played in any movies. Then, we group these by actor ids to calculate the count of genres each actor played in. Lastly, we used a CASE statement to output TRUE for those who played in more than one genre and FALSE for who hadn't.

SELECT 
  a.name,
  a.surname,
  COUNT(DISTINCT m.genre_id) AS genre_count,
  CASE 
    WHEN COUNT(DISTINCT m.genre_id) > 1 THEN 'TRUE'
    ELSE 'FALSE' 
  END AS multiple_appearance
FROM Actors_and_Actresses a
LEFT JOIN Cast c ON a.actor_id = c.actor_id
LEFT JOIN Movies m ON c.movie_id = m.movie_id
GROUP BY a.actor_id, a.name, a.surname
ORDER BY a.surname DESC;