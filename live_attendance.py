from dotenv import load_dotenv
import streamlit as st
import cv2
import numpy as np
import face_recognition
from datetime import datetime, timedelta
import tempfile
import os
import pickle
import subprocess
import pandas as pd
import plotly.express as px
from supabase import create_client
import requests

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Set Streamlit config
st.set_page_config(page_title="🎓 Face Recognition Attendance System", layout="wide")
st.title("🎓 Face Recognition Attendance System")

# Load encodings
if os.path.exists("EncodeFile.p"):
    with open("EncodeFile.p", "rb") as f:
        encodeListKnown, studentIds = pickle.load(f)
else:
    encodeListKnown, studentIds = [], []

# UI options
mode = st.radio("Choose Mode", ["Mark Attendance", "Register New Student", "View Dashboard"])

# Camera input
if mode != "View Dashboard":
    camera = st.camera_input("Capture a photo")

if mode == "Mark Attendance" and camera is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img:
        temp_img.write(camera.getvalue())
        img_path = temp_img.name

    img = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(img_rgb)
    face_encodings = face_recognition.face_encodings(img_rgb, face_locations)

    if face_encodings:
        face = face_encodings[0]
        matches = face_recognition.compare_faces(encodeListKnown, face)
        face_dist = face_recognition.face_distance(encodeListKnown, face)
        best_match_index = np.argmin(face_dist)

        if matches[best_match_index]:
            student_id = studentIds[best_match_index]
            student_res = supabase.table("students").select("*").eq("id", student_id).limit(1).execute()

            if student_res.data:
                student = student_res.data[0]
                last_time = student.get("last_attendence_time")
                now = datetime.now()
                st.success(f"✅ Welcome {student['name']} ({student_id})")

                try:
                    last_dt = datetime.fromisoformat(last_time) if last_time else now - timedelta(seconds=31)
                except:
                    last_dt = now - timedelta(seconds=31)

                if (now - last_dt).total_seconds() >= 30:
                    new_total = student.get("total_attendence", 0) + 1
                    supabase.table("students").update({
                        "total_attendence": new_total,
                        "last_attendence_time": now.isoformat()
                    }).eq("id", student_id).execute()
                    st.info(f"📌 Attendance updated. Total: {new_total}")
                else:
                    wait_time = 30 - int((now - last_dt).total_seconds())
                    st.warning(f"⏳ Already marked. Wait {wait_time} seconds.")
            else:
                st.warning("⚠️ No student found.")
        else:
            st.warning("⚠️ Face not recognized.")
    else:
        st.error("❌ No face detected.")

elif mode == "Register New Student" and camera is not None:
    with st.form("register_form"):
        student_id = st.text_input("Student ID")
        name = st.text_input("Name")
        major = st.text_input("Major")
        year = st.number_input("Year", min_value=1, max_value=6)
        starting_year = st.number_input("Starting Year", min_value=2000, max_value=2100)
        standing = st.selectbox("Standing", ["G", "B", "P"])
        submitted = st.form_submit_button("Register")

    if submitted:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img:
            temp_img.write(camera.getvalue())
            img_path = temp_img.name

        filename = f"{student_id}.jpg"
        with open(img_path, "rb") as f:
            upload_res = supabase.storage.from_("student-image").upload(filename, f)

        if hasattr(upload_res, "status_code") and upload_res.status_code < 300:
            now = datetime.now().isoformat()
            supabase.table("students").insert({
                "id": student_id,
                "name": name,
                "major": major,
                "year": year,
                "starting_year": starting_year,
                "standing": standing,
                "total_attendence": 0,
                "last_attendence_time": now
            }).execute()

            # Download image from Supabase to Images1
            image_url = f"{SUPABASE_URL}/storage/v1/object/public/student-image/{student_id}.jpg"
            img_save_path = f"Images1/{student_id}.jpg"
            response = requests.get(image_url)
            if response.status_code == 200:
                with open(img_save_path, "wb") as f:
                    f.write(response.content)
                st.success("📥 Image saved locally.")
            else:
                st.warning("⚠️ Could not download image to Images1.")

            # Auto-run EncodeGenerator
            subprocess.run(["python", "EncodeGenerator.py"])

            st.success(f"🎉 Registered {name} successfully!")
        else:
            st.error("❌ Failed to upload image.")

elif mode == "View Dashboard":
    st.title("📊 Attendance Dashboard")
    students_res = supabase.table("students").select("*").execute()
    students = students_res.data if students_res.data else []

    if not students:
        st.warning("No student records found.")
        st.stop()

    df = pd.DataFrame(students)
    df['total_attendence'] = df['total_attendence'].astype(int)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Students", len(df))
    col2.metric("Total Attendance Entries", df['total_attendence'].sum())
    col3.metric("Average Attendance", round(df['total_attendence'].mean(), 2))

    st.divider()

    if 'standing' in df.columns:
        standing_fig = px.bar(df.groupby('standing')['total_attendence'].sum().reset_index(),
                              x='standing', y='total_attendence',
                              color='standing', title="Attendance by Standing")
        st.plotly_chart(standing_fig, use_container_width=True)

    if 'major' in df.columns:
        major_fig = px.pie(df, values='total_attendence', names='major', title="Attendance by Major")
        st.plotly_chart(major_fig, use_container_width=True)

    st.subheader("📋 Detailed Attendance Table")
    st.dataframe(df[['id', 'name', 'major', 'year', 'standing', 'total_attendence', 'last_attendence_time']]
                 .sort_values(by='total_attendence', ascending=False),
                 use_container_width=True)