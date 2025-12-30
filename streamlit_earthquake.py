import streamlit as st
import mysql.connector
import pandas as pd

st.title("🔵 Earthquake Insights Using SQL")
st.header("DASHBOARD")
st.subheader("Select any problem statement (1–30) to run the SQL queries")

# ----- FIXED: OPTIONS AS DICTIONARY -----
OPTIONS = {
    "1. Top 10 Strongest Earthquakes (Mag)": "top_10_magnitude",
    "2. Top 10 Deepest Earthquakes (depth_km)": "top_10_depth",
    "3. Shallow earthquakes < 50 km and mag > 7.5": "shallow_quakes",
    "5. Average magnitude per magnitude type (magType)": "avg_magtype",
    "6. Year with most earthquakes": "year_most_quakes",
    "7. Month with highest number of earthquakes": "month_most_quakes",
    "8. Day of week with most earthquakes": "weekday_most_quakes",
    "9. Count of earthquakes per hour of day": "quakes_per_hour",
    "10. Most active reporting network (net)": "active_network",
    "11. Top 5 places with highest casualties": "top_casualties",
    "13. Average economic loss by alert level": "avg_loss_alert",
    "14. Reviewed vs automatic earthquakes (status)": "status_count",
    "15. Count by earthquake type (type)": "quake_type_count",
    "16. Number of earthquakes by data type (types)": "data_type_count",
    "18. Events with high station coverage (nst > threshold)": "high_station_nst",
    "19. Number of tsunamis triggered per year": "tsunami_per_year",
    "20. Earthquakes by alert levels": "alert_level_count",
    "21. Top 5 countries with highest avg magnitude (last 10 years)": "top_avg_mag_countries",
    "22. Countries with both shallow & deep earthquakes (same month)": "countries_shallow_deep",
    "23. Year-over-year growth rate of earthquakes": "yoy_growth",
    "24. 3 most seismically active regions (freq + avg magnitude)": "top_active_regions",
    "25. Avg depth within ±5° latitude per country": "avg_depth_lat_band",
    "26. Countries with highest shallow/deep ratio": "shallow_deep_ratio",
    "27. Avg magnitude difference (tsunami vs non-tsunami)": "tsunami_mag_diff",
    "28. Low reliability events (high rms + gap)": "low_reliability",
    "29. Consecutive earthquakes within 1 hour and 50 km": "close_consecutive",
    "30. Regions with most deep-focus earthquakes (depth > 300 km)": "deep_focus_300"

    
    }

choice = st.selectbox("Choose SQL analysis:", list(OPTIONS.keys()))

# MySQL connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="earthquake_project"
)
mycursor = mydb.cursor(dictionary=True)

# ----- FIXED: SQL QUERIES -----
SQL_QUERIES = {
    "top_10_magnitude": """
        SELECT *
        FROM earthquake_data
        WHERE mag IS NOT NULL
        ORDER BY mag DESC
        LIMIT 10;
    """,
    "top_10_depth": """
        SELECT *
        FROM earthquake_data
        WHERE depth_km IS NOT NULL
        ORDER BY depth_km DESC
        LIMIT 10;
    """,
    "shallow_quakes": """
        SELECT *
        FROM earthquake_data
        WHERE depth_km < 50 AND mag > 7.5;
    """,
    "avg_depth_continent": """
        SELECT continent, AVG(depth_km) AS avg_depth
        FROM earthquake_data
        WHERE depth_km IS NOT NULL
        GROUP BY continent;

    """,
    "avg_magtype": """
        SELECT magType, AVG(mag) AS avg_magnitude
        FROM earthquake_data
        WHERE mag IS NOT NULL
        GROUP BY magType
        ORDER BY avg_magnitude DESC;
    """,
    "year_most_quakes": """
          SELECT YEAR(time) AS earthquake_year, COUNT(*) AS num_earthquakes
          FROM earthquake_data
          GROUP BY YEAR(time)
          ORDER BY num_earthquakes DESC;
    """,
    "month_most_quakes":"""
         SELECT month(time) AS earthquake_month, COUNT(*) AS num_earthquakes
          FROM earthquake_data
          GROUP BY month(time)
          ORDER BY num_earthquakes DESC
          limit 1;
    """,
    "weekday_most_quakes":"""
         SELECT day(time) AS earthquake_day, COUNT(*) AS num_earthquakes
          FROM earthquake_data
          GROUP BY day(time)
          ORDER BY num_earthquakes DESC
          limit 5;
""",
"quakes_per_hour":"""
        SELECT hour(time) AS earthquake_hour, COUNT(*) AS num_earthquakes
          FROM earthquake_data
          GROUP BY hour(time)
          ORDER BY num_earthquakes DESC
          limit 5;
""",
"active_network":"""
SELECT net, COUNT(*) AS num_earthquakes
FROM earthquake_data
GROUP BY net
ORDER BY num_earthquakes DESC
LIMIT 1;
""",
"top_casualties":"""
SELECT place, sum(sig) AS high_casualties
FROM earthquake_data
where sig is not null
GROUP BY place
ORDER BY high_casualties DESC
LIMIT 10;
""",
"avg_loss_alert":"""
SELECT 
    place,
    AVG(mag * sig) AS avg_economic_loss
FROM earthquake_data
WHERE sig IS NOT NULL AND mag IS NOT NULL
GROUP BY place
ORDER BY avg_economic_loss DESC;
""",
"status_count":"""
SELECT 
    status,
    COUNT(*) AS total_earthquakes
FROM earthquake_data
WHERE status IS NOT NULL
GROUP BY status
ORDER BY total_earthquakes DESC;
""",
"quake_type_count":"""
SELECT 
    type,
    COUNT(*) AS total_earthquakes
FROM earthquake_data
WHERE type IS NOT NULL
GROUP BY type
ORDER BY total_earthquakes DESC;
""",
"data_type_count":"""

select types ,count(*)as data_type
 from earthquake_data
 GROUP BY types
 ORDER BY data_type DESC
 """,
 "high_station_nst":"""
select nst,time,updated,place,net from earthquake_data
 where nst > 50
 ORDER BY nst ASC;
""",
"tsunami_per_year":"""
SELECT 
    YEAR(time) AS year,
    COUNT(*) AS tsunami_count
FROM earthquake_data
WHERE tsunami=1
GROUP BY YEAR(time)
ORDER BY tsunami_count DESC;
""",
"alert_level_count":"""
SELECT 
    tsunami,
    COUNT(*) AS earthquake_count
FROM earthquake_data
WHERE tsunami IS NOT NULL
GROUP BY tsunami
ORDER BY earthquake_count DESC;
""",
"top_avg_mag_countries":"""
SELECT 
    SUBSTRING_INDEX(place, ',', -1) AS country,
    AVG(mag) AS avg_magnitude
FROM earthquake_data
WHERE mag IS NOT NULL
  AND time >= DATE_SUB(CURDATE(), INTERVAL 5 YEAR)
GROUP BY country
""",
"countries_shallow_deep":"""
SELECT DISTINCT country, year_month
FROM (
    SELECT 
        SUBSTRING_INDEX(place, ',', -1) AS country,
        DATE_FORMAT(time, '%Y-%m') AS year_month,
        MAX(CASE WHEN depth_km < 70 THEN 1 ELSE 0 END) AS shallow,
        MAX(CASE WHEN depth_km > 300 THEN 1 ELSE 0 END) AS deep
    FROM earthquake_data
    GROUP BY country, year_month
) t
WHERE shallow = 1 AND deep = 1;
""",
"yoy_growth":"""
SELECT 
    year,
    total_quakes,
    LAG(total_quakes) OVER (ORDER BY year) AS prev_year,
    ROUND(
        (total_quakes - LAG(total_quakes) OVER (ORDER BY year)) 
        / LAG(total_quakes) OVER (ORDER BY year) * 100, 2
    ) AS yoy_growth_percent
FROM (
    SELECT YEAR(time) AS year, COUNT(*) AS total_quakes
    FROM earthquake_data
    GROUP BY year
) t;
""",
"top_active_regions":"""
SELECT 
    SUBSTRING_INDEX(place, ',', -1) AS region,
    COUNT(*) AS frequency,
    AVG(mag) AS avg_magnitude
FROM earthquake_data
WHERE mag IS NOT NULL
GROUP BY region
ORDER BY frequency DESC, avg_magnitude DESC
LIMIT 3;
""",
"avg_depth_lat_band":"""
SELECT 
    SUBSTRING_INDEX(place, ',', -1) AS country,
    AVG(depth_km) AS avg_depth
FROM earthquake_data
WHERE latitude BETWEEN -5 AND 5
GROUP BY country;
""",
"shallow_deep_ratio":"""
SELECT 
    country,
    shallow_count / deep_count AS shallow_deep_ratio
FROM (
    SELECT 
        SUBSTRING_INDEX(place, ',', -1) AS country,
        SUM(CASE WHEN depth_km < 70 THEN 1 ELSE 0 END) AS shallow_count,
        SUM(CASE WHEN depth_km > 300 THEN 1 ELSE 0 END) AS deep_count
    FROM earthquake_data
    GROUP BY country
) t
WHERE deep_count > 0
ORDER BY shallow_deep_ratio DESC;
""",
"tsunami_mag_diff":"""
SELECT 
    AVG(CASE WHEN tsunami = 1 THEN mag END) -
    AVG(CASE WHEN tsunami = 0 THEN mag END) 
    AS avg_magnitude_difference
FROM earthquake_data;
""",
"low_reliability":""""
SELECT 
    id, time, place,
    AVG(gap + rms) AS error_score
FROM earthquake_data
WHERE gap IS NOT NULL AND rms IS NOT NULL
GROUP BY id
ORDER BY error_score DESC
LIMIT 10;
""",
"close_consecutive":"""
SELECT 
    a.id AS quake1,
    b.id AS quake2,
    TIMESTAMPDIFF(MINUTE, a.time, b.time) AS time_diff
FROM earthquake_data a
JOIN earthquake_data b
ON a.id <> b.id
AND ABS(TIMESTAMPDIFF(MINUTE, a.time, b.time)) <= 60
AND (
    6371 * ACOS(
        COS(RADIANS(a.latitude)) * COS(RADIANS(b.latitude)) *
        COS(RADIANS(b.longitude) - RADIANS(a.longitude)) +
        SIN(RADIANS(a.latitude)) * SIN(RADIANS(b.latitude))
    )
) <= 50;
""",
"deep_focus_300":"""
SELECT 
    SUBSTRING_INDEX(place, ',', -1) AS region,
    COUNT(*) AS deep_quakes
FROM earthquake_data
WHERE depth_km > 300
GROUP BY region
ORDER BY deep_quakes DESC;

"""   
}

if st.button("Run Query"):

    # Map selected text → SQL key
    sql_key = OPTIONS[choice]

    # Get SQL query
    query = SQL_QUERIES[sql_key]

    # Run SQL
    mycursor.execute(query)
    rows = mycursor.fetchall()

    # Convert to DataFrame
    df = pd.DataFrame(rows)

    # Show results
    st.dataframe(df)
