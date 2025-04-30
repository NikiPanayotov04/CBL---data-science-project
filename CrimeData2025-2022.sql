CREATE VIEW all_burglaries_from_2022 AS
SELECT *
FROM `2025_02_crimes`
UNION
SELECT *
FROM `2025_01_city_of_london_street`
UNION
SELECT *
FROM `2024_12_city_of_london_street`
UNION
SELECT *
FROM `2024_11_city_of_london_street`
UNION
SELECT *
FROM `2024_10_city_of_london_street`
UNION
SELECT *
FROM `2024_09_city_of_london_street`
UNION
SELECT *
FROM `2024_08_city_of_london_street`
UNION
SELECT *
FROM `2024_07_city_of_london_street`
UNION
SELECT *
FROM `2024_06_city_of_london_street`
UNION
SELECT *
FROM `2024_05_city_of_london_street`
UNION
SELECT *
FROM `2024_04_city_of_london_street`
UNION
SELECT *
FROM `2024_03_city_of_london_street`
UNION
SELECT *
FROM `2024_02_city_of_london_street`
UNION
SELECT *
FROM `2024_01_city_of_london_street`
UNION
SELECT *
FROM `2023_12_city_of_london_street`
UNION
SELECT *
FROM `2023_11_city_of_london_street`
UNION
SELECT *
FROM `2023_10_city_of_london_street`
UNION
SELECT *
FROM `2023_09_city_of_london_street`
UNION
SELECT *
FROM `2023_08_city_of_london_street`
UNION
SELECT *
FROM `2023_07_city_of_london_street`
UNION
SELECT *
FROM `2023_06_city_of_london_street`
UNION
SELECT *
FROM `2023_05_city_of_london_street`
UNION
SELECT *
FROM `2023_04_city_of_london_street`
UNION
SELECT *
FROM `2023_03_city_of_london_street`
UNION
SELECT *
FROM `2023_02_city_of_london_street`
UNION
SELECT *
FROM `2023_01_city_of_london_street`
UNION
SELECT *
FROM `2022_12_city_of_london_street`
UNION
SELECT *
FROM `2022_11_city_of_london_street`
UNION
SELECT *
FROM `2022_10_city_of_london_street`
UNION
SELECT *
FROM `2022_09_city_of_london_street`
UNION
SELECT *
FROM `2022_08_city_of_london_street`
UNION
SELECT *
FROM `2022_07_city_of_london_street`
UNION
SELECT *
FROM `2022_06_city_of_london_street`
UNION
SELECT *
FROM `2022_05_city_of_london_street`
UNION
SELECT *
FROM `2022_04_city_of_london_street`
UNION
SELECT *
FROM `2022_03_city_of_london_street`;

DROP VIEW all_burglaries_from_2022;

SELECT Location
FROM (
         SELECT Location, COUNT(*)
         FROM all_burglaries_from_2022
         WHERE `Crime type` = 'Burglary' AND NOT Location = 'On or near '
         GROUP BY Location
         ORDER BY COUNT(*) DESC
         LIMIT 20
     ) AS top2022

INTERSECT

-- Top 20 locations from 2024
SELECT Location
FROM (
         SELECT Location, COUNT(*)
         FROM all_burglaries_from_2024
         WHERE `Crime type` = 'Burglary'
         GROUP BY Location
         ORDER BY COUNT(*) DESC
         LIMIT 20
     ) AS top2024;