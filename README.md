# CBL-data-science-project
Project - Addressing real-world crime and security problems with data science.

CrimeData2025-2022.sql - The sql file executes a query to merge as view all the data in the period from February 2025 to March 2022. Then filters the data where the crime type is Burglary and then groups the data by locations and orders them in descending order.<br>
CrimeData2025-2024.sql - The sql file executes a query to merge as view all the data in the period from February 2025 to January 2024. Then filters the data where the crime type is Burglary and then groups the data by locations and orders them in descending order.<br>
GraphChartAnalyzation.py - This Python script reads monthly CSV crime data for the City of London from 2010 to 2025, filters for incidents where the crime type is Burglary, and then plots the monthly burglary counts to visualize trends over time.

⚠️ Note: The script uses a hardcoded absolute file path for the root data directory. To run this on another device, you will need to update the root_dir variable to reflect the correct path to the dataset on your local machine.
