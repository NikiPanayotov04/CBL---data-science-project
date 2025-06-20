# CBL-data-science-project
Project - Reducing residential burglary by developing an automated, data-driven forecasting model to inform the most efficient and effective resource allocation strategies.

To reproduce the full pipeline from raw data to models, officer allocation, and dashboards — run the following files in this order:

This in order to create the datasets:
merge_city_of_london.py
process_additional_datasets.py
process_all_crime_data.py

To run the Models:
Sarima.ipynb
xgboost_pipeline_FINAL.ipynb

To run the allocation:
allocation.ipynb

After these steps:
dashboard_dash.py


File Descriptions:

merge_city_of_london.py
Merges City of London wards and outputs the final 2024 ward shapefile.

process_additional_datasets.py
Processes and cleans all census, accommodation, household, and deprivation datasets.

process_all_crime_data.py
Loads raw burglary incident records (2022–2025), performs spatial joins to assign them to wards, and saves the result as a processed file for use in modeling.

Sarima.ipynb
Fits a SARIMA time series model to historical burglary counts per ward, capturing seasonal patterns.

xgboost_pipeline_FINAL.ipynb
Trains an XGBoost model using demographic and deprivation features to forecast burglary counts across wards.

allocation.ipynb
Solves a linear programming problem to assign limited officer-hours to each ward based on predicted crime demand and constraints.

dashboard.py

dashboard_dash.py
The dashboard, with interactive views for crime trends, forecasts, summaries, maps, and data exploration.

Archive Files
Notebooks and scripts that are no longer used. While they are not executed anymore, they were helpful during experimentation and development.






