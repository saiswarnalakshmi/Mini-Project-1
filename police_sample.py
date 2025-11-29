import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
file_path = r"D:\Datascience\traffic_stops_cleaned (1).xlsx"
df = pd.read_excel(file_path)
df.head()
df = df.bfill().ffill()
data=df
filtered_data = pd.DataFrame()

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Saiswarna@28599",
        database="Police_10_db"
    )
def run_query(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

st.title("🚓 Police Traffic Stop Analytics Dashboard")
st.write("Analyze vehicle stops, searches, and arrest trends using MySQL database")

with st.form("new_log_form"):
    stop_date = st.date_input("Stop Date")
    stop_time = st.time_input("Stop Time")
    county_name = st.text_input("County Name")
    driver_gender = st.selectbox("Driver Gender", ["male", "female"])
    driver_age = st.number_input("Driver Age", min_value=16, max_value=100, value=27)
    driver_race = st.text_input("Driver Race")
    search_conducted = st.selectbox("Search Conducted?", [0, 1])
    search_type = st.text_input("Search Type")
    stop_duration = st.selectbox("Stop Duration", data['stop_duration'].dropna().unique())
    drugs_related_stop = st.selectbox("Drugs Related Stop?", [0, 1])
    vehicle_number = st.text_input("Vehicle Number")
    timestamp = pd.Timestamp.now()

    submitted = st.form_submit_button("🔍 Predict Stop Outcome & Violation")

    if submitted:
      # Filter data for prediction
      filtered_data = data[
        (data['driver_gender'] == driver_gender) &
        (data['driver_age'] == driver_age) &
        (data['search_conducted'] == int(search_conducted)) &
        (data['stop_duration'] == stop_duration) &
        (data['drugs_related_stop'] == int(drugs_related_stop))
    ]

    # Predict stop_outcome
    if not filtered_data.empty:
        predicted_outcome = filtered_data['stop_outcome'].mode()[0]
        predicted_violation = filtered_data['violation'].mode()[0]
    else:
        predicted_outcome = "warning"  # Default fallback
        predicted_violation = "speeding"  # Default fallback


#Natural language summary
search_text = "A search was conducted" if int(search_conducted) else "No search was conducted"
drug_text = "was drug-related" if int(drugs_related_stop) else "was not drug-related"

st.markdown(f"""
🚔 **Prediction Summary**

- **Predicted Violation:** {predicted_violation}
- **Predicted Stop Outcome:** {predicted_outcome}

A {driver_age}-year-old {driver_gender} driver in {county_name} was stopped at {stop_time.strftime('%I:%M %p')} on {stop_date}.
{search_text}, and the stop {drug_text}.
Stop duration: **{stop_duration}**
Vehicle Number: **{vehicle_number}**
""")


#Queries
st.header("Advanced Insights")
selected_query=st.selectbox(
    "📊Select A Query To Run",
        [
        "Top 10 Drug-Related Vehicles",
        "Most Frequently Searched Vehicles",
        "Age Group with Highest Arrest Rate",
        "Gender Distribution by Country",
        "Race + Gender Highest Search Rate",
        "Time of Day – Most Traffic Stops",
        "Avg Stop Duration per Violation",
        "Night vs Day Arrest Rate",
        "Top Violations for Arrests & Searches",
        "Violations for Drivers Below 25",
        "Least Arrested Violations",
        "Drug-Related Stops by Country",
        "Arrest Rate by Country & Violation",
        "Country Search Analysis",
        "Yearly Stops & Arrest Trends",
        "Violation Trends | Age & Race",
        "Time Period Analysis (Year/Month/Hour)",
        "Violation Search & Arrest Ranking",
        "Driver Demographic Stats",
        "Top 5 Highest Arrest Violations"
    ]
)

# ---------------- QUERY MAPPER ----------------
queries = {
"Top 10 Drug-Related Vehicles": """
SELECT Vehicle_Number, COUNT(*) AS Drug_Stop_Count
FROM Police_10
WHERE Drug_Related_Stop = TRUE
GROUP BY Vehicle_Number
ORDER BY Drug_Stop_Count DESC
LIMIT 10;
""",
"Most Frequently Searched Vehicles": """
SELECT Vehicle_Number, COUNT(*) AS Search_Count
FROM Police_10
WHERE Search_Conducted = TRUE
GROUP BY Vehicle_Number
ORDER BY Search_Count DESC;
""",
"Age Group with Highest Arrest Rate": """
SELECT 
    CASE 
        WHEN Driver_Age < 18 THEN 'Under 18'
        WHEN Driver_Age BETWEEN 18 AND 25 THEN '18-25'
        WHEN Driver_Age BETWEEN 26 AND 40 THEN '26-40'
        WHEN Driver_Age BETWEEN 41 AND 60 THEN '41-60'
        ELSE '60+'
    END AS Age_Group,
    ROUND(AVG(Is_Arrested = TRUE) * 100, 2) AS Arrest_Rate_Percent
FROM Police_10
GROUP BY Age_Group
ORDER BY Arrest_Rate_Percent DESC;
""",
"Gender Distribution by Country": """
SELECT 
    Country_Name,
    Driver_Gender,
    COUNT(*) AS Total_Stops
FROM Police_10
GROUP BY Country_Name, Driver_Gender
ORDER BY Country_Name, Total_Stops DESC;
""",
"Race + Gender Highest Search Rate": """
SELECT 
    Driver_Race,
    Driver_Gender,
    COUNT(*) AS Total_Stops,
    SUM(Search_Conducted = TRUE) AS Searches_Conducted,
    ROUND((SUM(Search_Conducted = TRUE) / COUNT(*)) * 100, 2) AS Search_Rate_Percent
FROM Police_10
GROUP BY Driver_Race, Driver_Gender
ORDER BY Search_Rate_Percent DESC;
""",
"Time of Day – Most Traffic Stops": """
SELECT 
    HOUR(Stop_Time) AS Hour_Of_Day,
    COUNT(*) AS Total_Stops
FROM Police_10
GROUP BY Hour_Of_Day
ORDER BY Total_Stops DESC;
""",
"Avg Stop Duration per Violation": """
SELECT 
    Violation,
    ROUND(AVG(Stop_Duration), 2) AS Avg_Stop_Duration
FROM Police_10
GROUP BY Violation
ORDER BY Avg_Stop_Duration DESC;
""",
"Night vs Day Arrest Rate": """
SELECT 
    CASE 
        WHEN Stop_Time >= '20:00:00' OR Stop_Time < '06:00:00' THEN 'Night'
        ELSE 'Day'
    END AS Time_of_Day,
    COUNT(*) AS Total_Stops,
    SUM(CASE WHEN Is_Arrested = TRUE THEN 1 ELSE 0 END) AS Total_Arrests,
    ROUND(100.0 * SUM(CASE WHEN Is_Arrested = TRUE THEN 1 ELSE 0 END) / COUNT(*), 2) AS Arrest_Rate_Percent
FROM Police_10
GROUP BY Time_of_Day;
""",
"Top Violations for Arrests & Searches": """
SELECT Violation, COUNT(*) AS Search_Count
FROM Police_10
WHERE Search_Conducted = TRUE
GROUP BY Violation
ORDER BY Search_Count DESC
LIMIT 10;
""",
"Violations for Drivers Below 25": """
SELECT Violation, COUNT(*) AS Violation_Count
FROM Police_10
WHERE Driver_Age < 25
GROUP BY Violation
ORDER BY Violation_Count DESC
LIMIT 10;
""",
"Least Arrested Violations": """
SELECT Violation,
       COUNT(*) AS Total_Stops,
       SUM(CASE WHEN Is_Arrested= TRUE THEN 1 ELSE 0 END) AS Arrests,
       ROUND(SUM(CASE WHEN Is_Arrested= TRUE THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS Arrest_Percentage
FROM Police_10
GROUP BY Violation
ORDER BY Arrest_Percentage ASC
LIMIT 10;
""",
"Drug-Related Stops by Country": """
SELECT Country_Name, 
       COUNT(*) AS Total_Stops,
       SUM(CASE WHEN Drug_Related_Stop = TRUE THEN 1 ELSE 0 END) AS Drug_Related_Stops,
       ROUND(SUM(CASE WHEN Drug_Related_Stop = TRUE THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS Drug_Related_Percentage
FROM Police_10
GROUP BY Country_Name
ORDER BY Drug_Related_Percentage DESC
LIMIT 10;
""",
"Arrest Rate by Country & Violation": """
SELECT 
    Country_Name,
    Violation,
    COUNT(*) AS Total_Stops,
    SUM(CASE WHEN Is_Arrested = TRUE THEN 1 ELSE 0 END) AS Arrests,
    ROUND(SUM(CASE WHEN Is_Arrested = TRUE THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS Arrest_Rate_Percentage
FROM Police_10
GROUP BY Country_Name, Violation
ORDER BY Arrest_Rate_Percentage DESC, Total_Stops DESC;
""",
"Time Period Analysis (Year/Month/Hour)": """
SELECT
    YEAR(Stop_date) AS Year,
    MONTH(Stop_date) AS Month,
    HOUR(Stop_Time) AS Hour,
    COUNT(*) AS Number_of_Stops
FROM Police_10
GROUP BY Year, Month, Hour
ORDER BY Year, Month, Hour;
"""
}

# ---------------- EXECUTE SELECTED QUERY ----------------
df = pd.DataFrame()  # Initialize an empty DataFrame

if st.button("Run Query"):
    df = run_query(queries[selected_query])
    st.dataframe(df)

    # Show chart automatically (if suitable)
    if df.shape[1] == 2:  # 2 columns → bar chart
        fig = px.bar(df, x=df.columns[0], y=df.columns[1])
        st.plotly_chart(fig)

# Only call download button AFTER df is defined
if not df.empty:
    st.sidebar.download_button(
        label="Download Result as CSV",
        data=df.to_csv(index=False),
        file_name="query_result.csv",
        mime="text/csv"
    )