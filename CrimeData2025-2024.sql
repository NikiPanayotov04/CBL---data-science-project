CREATE VIEW all_burglaries_from_2024 AS
SELECT *
FROM `2025_02_crimes`
WHERE `Crime type` = 'Burglary'
UNION
SELECT *
FROM `2025_01_city_of_london_street`
WHERE `Crime type` = 'Burglary'
UNION
SELECT *
FROM `2024_12_city_of_london_street`
WHERE `Crime type` = 'Burglary'
UNION
SELECT *
FROM `2024_11_city_of_london_street`
WHERE `Crime type` = 'Burglary'
UNION
SELECT *
FROM `2024_10_city_of_london_street`
WHERE `Crime type` = 'Burglary'
UNION
SELECT *
FROM `2024_09_city_of_london_street`
WHERE `Crime type` = 'Burglary'
UNION
SELECT *
FROM `2024_08_city_of_london_street`
WHERE `Crime type` = 'Burglary'
UNION
SELECT *
FROM `2024_07_city_of_london_street`
WHERE `Crime type` = 'Burglary'
UNION
SELECT *
FROM `2024_06_city_of_london_street`
WHERE `Crime type` = 'Burglary'
UNION
SELECT *
FROM `2024_05_city_of_london_street`
WHERE `Crime type` = 'Burglary'
UNION
SELECT *
FROM `2024_04_city_of_london_street`
WHERE `Crime type` = 'Burglary'
UNION
SELECT *
FROM `2024_03_city_of_london_street`
WHERE `Crime type` = 'Burglary'
UNION
SELECT *
FROM `2024_02_city_of_london_street`
WHERE `Crime type` = 'Burglary'
UNION
SELECT *
FROM `2024_01_city_of_london_street`
WHERE `Crime type` = 'Burglary';

SELECT Location, Count(*)
FROM all_burglaries_from_2024
GROUP BY Location
ORDER BY COUNT(*) DESC;

