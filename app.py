from dotenv import load_dotenv
import streamlit as st
import cv2
import numpy as np
import face_recognition
from datetime import datetime, timedelta
import tempfile
import os
import pickle
from supabase import create_client
import pandas as pd
import plotly.express as px

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load known encodings
with open("EncodeFile.p", "rb") as f:
    encodeListKnown, studentIds = pickle.load(f)

# Streamlit UI
st.set_page_config(page_title="Face Attendance System", layout="wide")
st.title("🎓 Face Recognition Attendance System")

# Sidebar for mode selection
mode = st.sidebar.radio("Select Mode", ["📸 Attendance", "🆕 Register New Student", "📊 Dashboard"])

if mode == "📸 Attendance":
    st.subheader("Mark Attendance via Face Recognition")
    camera = st.camera_input("Capture a photo")

    if camera is not None:
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
                    st.success(f"✅ Welcome {student['name']} ({student_id})")

                    now = datetime.now()
                    if last_time:
                        last_dt = datetime.fromisoformat(last_time)
                        if now - last_dt > timedelta(seconds=30):
                            supabase.table("students").update({
                                "total_attendence": student.get("total_attendence", 0) + 1,
                                "last_attendence_time": now.strftime("%Y-%m-%d %H:%M:%S")
                            }).eq("id", student_id).execute()
                            st.info("📌 Attendance updated.")
                        else:
                            wait_time = 30 - (now - last_dt).seconds
                            st.warning(f"⏳ Already marked. Please wait {wait_time} more seconds.")
                    else:
                        supabase.table("students").update({
                            "total_attendence": 1,
                            "last_attendence_time": now.strftime("%Y-%m-%d %H:%M:%S")
                        }).eq("id", student_id).execute()
                        st.info("✅ First attendance recorded.")
                else:
                    st.warning(f"No student found with ID {student_id}.")
            else:
                st.warning("⚠️ Face not recognized.")
        else:
            st.error("❌ No face detected.")

elif mode == "🆕 Register New Student":
    st.subheader("Register a New Student")
    camera = st.camera_input("Capture a photo for registration")
    if camera is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img:
            temp_img.write(camera.getvalue())
            img_path = temp_img.name

    with st.form("register_form"):
        student_id = st.text_input("Student ID")
        name = st.text_input("Name")
        major = st.text_input("Major")
        year = st.number_input("Year", min_value=1, max_value=6)
        starting_year = st.number_input("Starting Year", min_value=2000, max_value=2100)
        standing = st.selectbox("Standing", ["G", "B", "P"])
        submitted = st.form_submit_button("Register")

    if submitted and camera:
        filename = f"{student_id}.jpg"
        with open(img_path, "rb") as f:
            upload_res = supabase.storage.from_("student-image").upload(filename, f)

        if hasattr(upload_res, "status_code") and upload_res.status_code < 300:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            st.success(f"🎉 Registered {name} successfully!")
        else:
            st.error("❌ Failed to upload image.")

elif mode == "📊 Dashboard":
    st.subheader("📈 Attendance Dashboard")
    student_data = supabase.table("students").select("*").execute()
    if student_data.data:
        df = pd.DataFrame(student_data.data)
        col1, col2, col3 = st.columns(3)
        col1.metric("👨‍🎓 Total Students", len(df))
        col2.metric("✅ Total Attendance", df["total_attendence"].sum())
        col3.metric("📉 Average Attendance", round(df["total_attendence"].mean(), 2))

        bar_chart = px.bar(df, x="name", y="total_attendence", color="standing", title="Attendance by Student")
        st.plotly_chart(bar_chart, use_container_width=True)

        pie_chart = px.pie(df, names="major", title="Distribution by Major")
        st.plotly_chart(pie_chart, use_container_width=True)

        st.dataframe(df.sort_values(by="total_attendence", ascending=False))
    else:
        st.warning("No student data found.")