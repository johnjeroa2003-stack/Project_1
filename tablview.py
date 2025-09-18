import streamlit 

import pandas as pd
import streamlit as st
import pymysql

streamlit.title("GEORGE")


# Database connection
def create_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            user= 'root',
            password='jero@2003',
            database= 'securecheck',
            cursorclass=pymysql.cursors.DictCursor
           
        )
        return connection
    except Exception as e:
        st.error(f"Database connection Error: {e}")
        return None
    
# Fetch data from database
def fetch_data(query):
    connection = create_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                df = pd.DataFrame(result)
                return df
        finally:
            connection.close()
    else:
        return pd.DataFrame()
    #streamlit UI
st.set_page_config(page_title="securecheck police Dashboard", layout="wide")

st.title("🚨 securecheck: police check post Digital Ledger")
st.markdown("Real-time monitoring and insights for law enforcement")

# show full table
st.header("police logs overview")
query = "SELECT * FROM police_logs"
data = fetch_data(query)
st.dataframe(data, use_container_width=True)

# quick metrics
st.header("Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_stops = data.shape[0]
    st.metric("Total Police Stops", total_stops)

with col2:
    arrests = data[data['stop_outcome'].str.contains("arrest", case=False, na=False)].shape[0]
    st.metric("total Arrests", arrests)
    
with col3:
    warnings = data[data['stop_outcome'].str.contains("warning", case=False, na=False)].shape[0]
    st.metric("Total Warnings", warnings)

with col4:
    drug_related = data[data['drugs_related_stop'] == 1].shape[0]
    st.metric("Drug Related Stops", drug_related)

    # Advanced queries
    st.header("Advanced Insights")

    selected_query = st.selectbox("Select a Query to Run", [
        "Total Number of Police Stops",
        "count of stops by violation Type",
        "Number of Arrests vs. Warnings",
        "Average age of Drivers Stopped",
        "Top 5 Most Frequent Search Types",
        "Count of Stops by Gender",
        "Most Common Violation for Arrests"
    ])

query_map = {
    "Total Number of Police Stops": 
        "SELECT COUNT(*) AS total_stops FROM police_logs",

    "Count of Stops by Violation Type": 
        "SELECT violation, COUNT(*) AS count FROM police_logs GROUP BY violation ORDER BY count DESC",

    "Number of Arrests vs. Warnings": 
        "SELECT stop_outcome, COUNT(*) AS count FROM police_logs GROUP BY stop_outcome",

    "Average Age of Drivers Stopped": 
        "SELECT AVG(driver_age) AS average_age FROM police_logs",

    "Top 5 Most Frequent Search Types": 
        "SELECT search_type, COUNT(*) AS count FROM police_logs WHERE search_type != '' GROUP BY search_type ORDER BY count DESC LIMIT 5",

    "Count of Stops by Gender": 
        "SELECT driver_gender, COUNT(*) AS count FROM police_logs GROUP BY driver_gender",

    "Most Common Violation for Arrests": 
        "SELECT violation, COUNT(*) AS count FROM police_logs WHERE stop_outcome LIKE '%arrest%' GROUP BY violation ORDER BY count DESC LIMIT 1"
}

if st.button("Run Query"):
    result = fetch_data(query_map[selected_query])
    if not result.empty:
        st.write(result)
    else:
        st.warning("NO RESULTS for the selected query.")

st.markdown("---")
st.markdown("Built with 🩷 for law Enforcement by securecheck")
st.header("Custom Natural Language Filter")


st.markdown("Fill in the details below to get a natural language prediction of the stop outcome based an existing data.")



st.header("Add New Police Log & predict outcome and violation")

# Input from all fields (excluding output)
with st.form("new_log_form"):
    stop_date = st.date_input("Stop Date")
    stop_time = st.time_input("Stop Time")
    country_name = st.text_input("Country Name")
    driver_gender = st.selectbox("Driver Gender", ["male", "female"])
    driver_age = st.number_input("Driver Age", min_value=16, max_value=100, value=27)
    driver_race = st.text_input("Driver Race")
    search_conducted = st.selectbox("Was a Search Conducted?", ["0", "1"])
    search_type = st.text_input("Search Type")
    drugs_related_stop = st.selectbox("Was it Drug Related?", ["0", "1"])
    stop_duration = st.selectbox("Stop Duration", data['stop_duration'].dropna().unique())
    vehicle_number = st.text_input("Vehicle Number")
    timestamp = pd.Timestamp.now()

    submitted = st.form_submit_button("Predict Stop Outcome & Violation")

if submitted:
    filtered_data = data[
        (data['driver_gender'] == driver_gender) &
        (data['driver_age'] == driver_age) &
        (data['search_conducted'] == int(search_conducted)) &
        (data['stop_duration'] == stop_duration) &
        (data["drugs_related_stop"] == int(drugs_related_stop))
    ]

    if not filtered_data.empty:
        predicted_outcome = filtered_data['stop_outcome'].mode()[0]
        predicted_violation = filtered_data['violation'].mode()[0]
    else:
        predicted_outcome = "Warning"
        predicted_violation = "Speeding"

    search_text = "A search was conducted." if int(search_conducted) else "No search was conducted."
    drug_text = "This was drug-related." if int(drugs_related_stop) else "This was not drug-related."

    st.markdown(f"""
    ### Prediction Summary

    - **Predicted Violation:** {predicted_violation}  
    - **Predicted Stop Outcome:** {predicted_outcome}

    A {driver_age}-year-old {driver_gender} driver in {country_name} was stopped at {stop_time.strftime('%I:%M %p')} on {stop_date.strftime('%B %d, %Y')}.  
    {search_text} {drug_text}  
    Stop duration: **{stop_duration}**  
    Vehicle Number: **{vehicle_number}**
    """)


