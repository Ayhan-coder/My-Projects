-- query10.sql
-- Lists directors who directed Sci-Fi movies between 2020 and 2025
-- First, we create genres table which genre name sci fiction and release date is between 2020/01/01 and 2025/12/31 then we order by director nationality in increasing order.  
-- Then, we join the movies and genres table on the same genre id with genres table.
-- After that, we join the movies table and directors table on the same director ids.
-- Finally we select different director names, surnames, and nationality from the latest directors table after joining operations.

SELECT DISTINCT d.name, d.surname, d.nationality
FROM Directors d
JOIN Movies m ON d.director_id = m.director_id
JOIN Genres g ON m.genre_id = g.genre_id
WHERE g.genre_name = 'Sci-Fi'
  AND STR_TO_DATE(m.release_date, '%d.%m.%Y') BETWEEN '2020-01-01' AND '2025-12-31'
ORDER BY d.nationality ASC;