# CBL-data-science-project
Project - Addressing real-world crime and security problems with data science.

🐍 Python Scripts
HeatMapDeprivationIndex.py
Generates a choropleth map of London wards based on the Index of Multiple Deprivation (IMD) scores. It merges ward shapefiles with IMD data and visualizes relative deprivation across the city.

HeatMapLondonBurglaries.py
Loads, filters, and processes burglary data (2022–2025) from multiple CSV files, performs spatial joins with ward boundaries, and visualizes the burglary count per ward in a choropleth map. It also groups the multiple wards of the City of London into a single entity for accurate display.

GraphChartAnalyzation.py
Creates a time-series line chart showing burglary trends in the City of London from 2010 to 2025, using historical crime records to highlight year-over-year changes.

🧠 SQL File
CrimeData2025-2022.sql
Contains SQL queries written to analyze burglary data between 2022 and 2025.

⚠️ Data Notice
📦 The data files are not included in this repository because of their large size.

Before running any script, you must manually download and install the required datasets (ward shapefiles, crime CSVs, IMD Excel file, etc.).

Important:
The paths to these files are currently hardcoded in the .py files. You will need to update the file paths in each script to match your local folder structure before running them.


in order: 
run merge_city_of_london.py. 
run process_all_crime_data.py
run process_additional_datasets.py

