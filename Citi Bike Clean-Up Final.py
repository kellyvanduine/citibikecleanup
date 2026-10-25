#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 24 13:56:47 2026

@author: kellyvanduine
"""

import pandas as pd

# 1. Load dataset
df = pd.read_csv("202609-citibike-tripdata_5.csv", low_memory=False)

# Display actual column names
print(df.columns.tolist())

# Standardize column names
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)
# Rename coordinate columns to match the Python script
df.rename(columns={
    "start_latitude": "start_lat",
    "start_longitude": "start_lng",
    "end_latitude": "end_lat",
    "end_longitude": "end_lng"
}, inplace=True)

df.drop(columns=["unnamed:_0", "unnamed:_0.1"], errors="ignore", inplace=True)

print(df.info())

# 2. Convert to DateTime
df["started_at"] = pd.to_datetime(df["started_at"], errors="coerce")
df["ended_at"] = pd.to_datetime(df["ended_at"], errors="coerce")

# 3. Floor timestamps to seconds
df["started_at"] = df["started_at"].dt.floor("s")
df["ended_at"] = df["ended_at"].dt.floor("s")

# Identify NULL values
print("Initial NULL values:\n", df.isnull().sum())

# 4. Recover missing data using non-missing data as reference
station_lookup = df.dropna(subset=['end_station_id']).groupby('end_station_name').first()

df['end_station_id'] = df['end_station_id'].fillna(df['end_station_name'].map(station_lookup['end_station_id']))
df['end_lat'] = df['end_lat'].fillna(df['end_station_name'].map(station_lookup['end_lat']))
df['end_lng'] = df['end_lng'].fillna(df['end_station_name'].map(station_lookup['end_lng']))

# 5. Master reference dataframe
startRef = df.dropna(subset=['start_station_id'])[['start_station_name', 'start_station_id', 'start_lat', 'start_lng']].drop_duplicates('start_station_name')
startRef.columns = ['station_name', 'station_id', 'lat', 'lng']

endRef = df.dropna(subset=['end_station_id'])[['end_station_name', 'end_station_id', 'end_lat', 'end_lng']].drop_duplicates('end_station_name')
endRef.columns = ['station_name', 'station_id', 'lat', 'lng']

masterRef = pd.concat([startRef, endRef]).drop_duplicates('station_name').set_index('station_name')

# Fill missing end/start station details using master lookup
df['end_station_id'] = df['end_station_id'].fillna(df['end_station_name'].map(masterRef['station_id']))
df['end_lat'] = df['end_lat'].fillna(df['end_station_name'].map(masterRef['lat']))
df['end_lng'] = df['end_lng'].fillna(df['end_station_name'].map(masterRef['lng']))

df['start_station_id'] = df['start_station_id'].fillna(df['start_station_name'].map(masterRef['station_id']))
df['start_lat'] = df['start_lat'].fillna(df['start_station_name'].map(masterRef['lat']))
df['start_lng'] = df['start_lng'].fillna(df['start_station_name'].map(masterRef['lng']))

# Drop remaining rows without station IDs
df.dropna(subset=['start_station_id'], inplace=True)

# Check duplicates
print("Duplicates:", df.duplicated().sum())

# 6. Check coordinate limits
limits = {
    "start_lat": (-90, 90),
    "end_lat": (-90, 90),
    "start_lng": (-180, 180),
    "end_lng": (-180, 180)
}

for column, (minimum, maximum) in limits.items():
    missing = df[column].isna().sum()
    invalid = (df[column].notna() & ~df[column].between(minimum, maximum)).sum()
    print(f"{column} -> Missing: {missing}, Invalid: {invalid}")

# 7. Validate categorical fields
valid_types = ["electric_bike", "classic_bike", "electric bike", "classic bike"]
invalid_types = df[~df["rideable_type"].isin(valid_types)]
print("Invalid Rideable Types:", len(invalid_types))

valid_members = ["member", "casual"]
invalid_members = df[~df["member_casual"].isin(valid_members)]
print("Invalid Member Categories:", len(invalid_members))

# 8. Clean text fields (strip whitespace and format rideable_type)
text_cols = df.select_dtypes(include=['object', 'string']).columns
for col in text_cols:
    mask = df[col].notna() & df[col].ne(df[col].str.strip())
    print(f"{col}: {mask.sum()} values with leading/trailing whitespace")
    df[col] = df[col].str.strip()

# Format rideable_type values cleanly
df['rideable_type'] = (
    df['rideable_type']
    .str.replace('_', ' ', regex=False)
    .str.replace(r'(?i)electricbike', 'electric bike', regex=True)
    .str.replace(r'(?i)classicbike', 'classic bike', regex=True)
    .str.strip()
)

# 9. Calculate trip duration IN MINUTES (before changing column headers)
df["trip_minutes"] = (df["ended_at"] - df["started_at"]).dt.total_seconds() / 60

# Check invalid trip durations
bad_duration = df["trip_minutes"].isna() | (df["trip_minutes"] <= 0)
print("Invalid trips (<=0 mins or NaN):", bad_duration.sum())
print(df["trip_minutes"].describe())

# 10. Rename column headers at the end
df.columns = (
    df.columns
    .str.replace("_", " ", regex=False)
    .str.title()
)

df.rename(columns={
    "Start Lat": "Start Latitude",
    "Start Lng": "Start Longitude",
    "End Lat": "End Latitude",
    "End Lng": "End Longitude",
    "Trip Minutes": "Trip Duration (Mins)"
}, inplace=True)

df = df.loc[:, ~df.columns.duplicated()].copy()

# 11. Round Numeric Columns

df["Start Latitude"] = df["Start Latitude"].round(4)
df["End Latitude"] = df["End Latitude"].round(4)
df["Start Longitude"] = df["Start Longitude"].round(4)
df["End Longitude"] = df["End Longitude"].round(4)
df["Trip Duration (Mins)"] = df["Trip Duration (Mins)"].round(2)

# Verify updated columns
print("Final Columns:\n", df.columns)
print("Dataset shape:", df.shape)
print(df[["Started At", "Ended At", "Trip Duration (Mins)"]].head())

# Final Data Quality Summary
print("\n Final Data Quality Summary")
print("Total Records:", len(df))
print("Total Columns:", len(df.columns))
print("Remaining Missing Values:", df.isnull().sum().sum())
print("Total Duplicate Ride Ids:", df["Ride Id"].duplicated().sum())

# Export Cleaned Data
df.to_csv("citiebike_cleaned_final.csv", index=False)

#GRAPH CODE
import pandas as pd
import matplotlib.pyplot as plt

# 1. Prepare Data for Visualization

# Convert start and end times to datetime
df['Started At'] = pd.to_datetime(df['Started At'])
df['Ended At'] = pd.to_datetime(df['Ended At'])

# Extract starting hour for visualizations
df['start_hour'] = df['Started At'].dt.hour

# Create a figure with 4 subplots (2x2 grid)
plt.figure(figsize=(14, 10))


# GRAPH 1: Member vs. Casual Riders (Pie Chart)

plt.subplot(2, 2, 1)
user_counts = df['Member Casual'].value_counts()
colors = ['#1f77b4', '#ff7f0e']

plt.pie(
    user_counts, 
    labels=user_counts.index.str.capitalize(), 
    autopct='%1.1f%%', 
    startangle=140, 
    colors=colors,
    explode=(0.05, 0)
)
plt.title("1. Rider Breakdown: Members vs. Casual Users", fontsize=12, fontweight='bold')

# GRAPH 2: Hourly Demand & Rush Hours (Line Chart)
plt.subplot(2, 2, 2)
hourly_counts = df.groupby('start_hour').size()

plt.plot(hourly_counts.index, hourly_counts.values, marker='o', color='#2ca02c', linewidth=2)
plt.title("2. Daily Demand Curve (Peak Rush Hours)", fontsize=12, fontweight='bold')
plt.xlabel("Hour of Day (0 - 23)")
plt.ylabel("Total Trips Started")
plt.xticks(range(0, 24, 2))
plt.grid(True, linestyle='--', alpha=0.6)

# GRAPH 3: Top 10 Busiest Start Stations (Horizontal Bar Chart)

plt.subplot(2, 2, 3)
top_stations = df['Start Station Name'].value_counts().head(10).sort_values(ascending=True)

plt.barh(top_stations.index, top_stations.values, color='#1f77b4')
plt.title("3. Top 10 Busiest Start Stations", fontsize=12, fontweight='bold')
plt.xlabel("Total Trips Started")
plt.grid(axis='x', linestyle='--', alpha=0.6)

# GRAPH 4: Average Trip Duration by User Type (Bar Chart)

plt.subplot(2, 2, 4)

# Calculate average trip duration for each membership type
avg_duration = df.groupby('Member Casual')['Trip Duration (Mins)'].mean()

# Convert values into standard Python lists
labels = avg_duration.index.astype(str).str.capitalize().tolist()
values = avg_duration.astype(float).tolist()

# Create bar chart
bars = plt.bar(labels, values, color=['#1f77b4', '#ff7f0e'], width=0.5)

plt.title("4. Average Trip Duration (Minutes)", fontsize=12, fontweight='bold')
plt.ylabel("Minutes")

plt.tight_layout()
plt.show()
