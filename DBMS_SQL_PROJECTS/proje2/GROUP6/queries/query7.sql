-- query7.sql
-- Finds all actors/actresses whose surname starts with 'P'
-- We select actor id , name , surname, birth date from the actors table with only actors that have surnames starting with ‘P’.

SELECT actor_id, name, surname, birth_date
FROM Actors_and_Actresses
WHERE surname LIKE 'P%';