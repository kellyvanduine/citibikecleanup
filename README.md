# NYC Citi Bike Data Cleaning & Exploratory Data Analysis

## Project Overview

This project analyzes Citi Bike trip data from New York City for September 2026. The objective was to clean and prepare a large dataset for analysis, identify data-quality issues, and explore bicycle-sharing usage patterns through Python visualizations.

The project demonstrates practical experience with data cleaning, missing-value handling, data validation, feature engineering, and exploratory data analysis.

## Tools & Technologies

- **Python** — Data cleaning, transformation, and analysis
- **Pandas** — Data manipulation, missing-value recovery, and validation
- **Matplotlib** — Data visualization
- **Spyder IDE** — Python development and execution
- **CSV** — Data storage and export

## Dataset

**Source:** NYC Citi Bike trip data

**Period:** September 2026

**Original dataset:**
- 982,855 trip records
- 13 original variables
- Information on bicycle types, trip timestamps, station locations, geographic coordinates, and rider membership categories

The dataset contains two rider categories: annual members and casual riders.

## Data Cleaning Process

The following procedures were performed to improve data consistency and prepare the dataset for analysis.

### 1. Column Standardization
- Standardized column names using consistent naming conventions.
- Removed unnecessary whitespace from column headers.
- Renamed geographic coordinate variables for consistency.

### 2. Date and Time Formatting
- Converted trip start and end times into datetime objects.
- Removed fractional seconds to standardize timestamp precision.

### 3. Missing-Value Recovery
- Identified missing values across the dataset.
- Recovered missing station IDs and geographic information using matching station names.
- Created a combined station reference table using both starting and ending station information.
- Removed records with unresolved starting station IDs.

### 4. Data Validation
- Checked for duplicate records.
- Validated latitude and longitude against geographic coordinate ranges.
- Checked categorical variables for unexpected values.

### 5. Text Standardization
- Removed leading and trailing whitespace.
- Standardized bicycle-type labels.

### 6. Feature Engineering
- Created a new variable, `Trip Duration (Mins)`, by calculating the difference between trip start and end times.
- Checked for
