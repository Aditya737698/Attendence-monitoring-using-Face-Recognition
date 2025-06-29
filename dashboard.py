import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="📊 Attendance Dashboard", layout="wide")
st.title("📊 Face Recognition Attendance Dashboard")

# Fetch student data
students_res = supabase.table("students").select("*").execute()
students = students_res.data if students_res.data else []

# If no data
if not students:
    st.warning("No student records found.")
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(students)
df['total_attendence'] = df['total_attendence'].astype(int)

# Summary KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Students", len(df))
col2.metric("Total Attendance Entries", df['total_attendence'].sum())
col3.metric("Average Attendance", round(df['total_attendence'].mean(), 2))

st.divider()

# Attendance by Standing
if 'standing' in df.columns:
    standing_fig = px.bar(df.groupby('standing')['total_attendence'].sum().reset_index(),
                          x='standing', y='total_attendence',
                          color='standing',
                          title="Attendance by Standing")
    st.plotly_chart(standing_fig, use_container_width=True)

# Attendance by Major
if 'major' in df.columns:
    major_fig = px.pie(df, values='total_attendence', names='major', title="Attendance by Major")
    st.plotly_chart(major_fig, use_container_width=True)

# Detailed Table
st.subheader("📋 Detailed Student Attendance Table")
st.dataframe(df[['id', 'name', 'major', 'year', 'standing', 'total_attendence', 'last_attendence_time']]
             .sort_values(by='total_attendence', ascending=False),
             use_container_width=True)