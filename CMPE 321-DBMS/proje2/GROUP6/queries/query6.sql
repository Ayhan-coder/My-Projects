-- query6.sql
-- Shows how many movies each actor/actress has appeared in (including those with 0).
--  We create actors and actresses table with left join of actors table after group by actor id (we used left join so that we keep the rows with actors that have 0 movie appearances) and cast table after ordered by movie count descending order which have the same actor ids , 
-- We select actor name, actor surname , and movie count of distinct movie ids (to make sure that we don’t count duplicate movie ids) from actors and actresses table.

SELECT 
  a.name AS `actor name`,
  a.surname AS `actor surname`,
  COUNT(DISTINCT c.movie_id) AS `movie count`
FROM Actors_and_Actresses a
LEFT JOIN Cast c ON a.actor_id = c.actor_id
GROUP BY a.actor_id
ORDER BY `movie count` DESC;