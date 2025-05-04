CREATE OR REPLACE VIEW all_burglaries_from_2022 AS
SELECT *
FROM `2025_02_city_of_london_street`
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
FROM `2022_03_city_of_london_street`
UNION
SELECT *
FROM `2025_02_metropolitan_street`
UNION
SELECT *
FROM `2025_01_metropolitan_street`
UNION
SELECT *
FROM `2024_12_metropolitan_street`
UNION
SELECT *
FROM `2024_11_metropolitan_street`
UNION
SELECT *
FROM `2024_10_metropolitan_street`
UNION
SELECT *
FROM `2024_09_metropolitan_street`
UNION
SELECT *
FROM `2024_08_metropolitan_street`
UNION
SELECT *
FROM `2024_07_metropolitan_street`
UNION
SELECT *
FROM `2024_06_metropolitan_street`
UNION
SELECT *
FROM `2024_05_metropolitan_street`
UNION
SELECT *
FROM `2024_04_metropolitan_street`
UNION
SELECT *
FROM `2024_03_metropolitan_street`
UNION
SELECT *
FROM `2024_02_metropolitan_street`
UNION
SELECT *
FROM `2024_01_metropolitan_street`
UNION
SELECT *
FROM `2023_12_metropolitan_street`
UNION
SELECT *
FROM `2023_11_metropolitan_street`
UNION
SELECT *
FROM `2023_10_metropolitan_street`
UNION
SELECT *
FROM `2023_09_metropolitan_street`
UNION
SELECT *
FROM `2023_08_metropolitan_street`
UNION
SELECT *
FROM `2023_07_metropolitan_street`
UNION
SELECT *
FROM `2023_06_metropolitan_street`
UNION
SELECT *
FROM `2023_05_metropolitan_street`
UNION
SELECT *
FROM `2023_04_metropolitan_street`
UNION
SELECT *
FROM `2023_03_metropolitan_street`
UNION
SELECT *
FROM `2023_02_metropolitan_street`
UNION
SELECT *
FROM `2023_01_metropolitan_street`
UNION
SELECT *
FROM `2022_12_metropolitan_street`
UNION
SELECT *
FROM `2022_11_metropolitan_street`
UNION
SELECT *
FROM `2022_10_metropolitan_street`
UNION
SELECT *
FROM `2022_09_metropolitan_street`
UNION
SELECT *
FROM `2022_08_metropolitan_street`
UNION
SELECT *
FROM `2022_07_metropolitan_street`
UNION
SELECT *
FROM `2022_06_metropolitan_street`
UNION
SELECT *
FROM `2022_05_metropolitan_street`
UNION
SELECT *
FROM `2022_04_metropolitan_street`
UNION
SELECT *
FROM `2022_03_metropolitan_street`;

DROP VIEW all_burglaries_from_2022;


CREATE OR REPLACE VIEW top_burglaries_locations AS
SELECT Location, COUNT(*)
FROM all_burglaries_from_2022
WHERE `Crime type` = 'Burglary' AND NOT Location = 'On or near ' AND NOT Location = 'No Location'
GROUP BY Location
ORDER BY COUNT(*) DESC