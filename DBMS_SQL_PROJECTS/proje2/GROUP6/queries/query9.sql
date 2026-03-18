-- query9.sql
-- Lists actors born in the same year as Amy Adams
-- We select names, surnames from actors and actresses table that have the same birth as amy adams by first calculating the birth year of actress named “Amy Adams” then filtering only the rows with the same birth year as her.

SELECT name, surname
FROM Actors_and_Actresses
WHERE YEAR(STR_TO_DATE(birth_date, '%d.%m.%Y')) = (
    SELECT YEAR(STR_TO_DATE(birth_date, '%d.%m.%Y'))
    FROM Actors_and_Actresses
    WHERE name = 'Amy' AND surname = 'Adams'
)
ORDER BY surname ASC;