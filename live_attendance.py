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

# Load environment variables
load_dotenv()
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="🎓 Face Recognition Attendance System", layout="wide")

# Sidebar Role Selection
st.sidebar.title("🔐 Login Panel")
role = st.sidebar.selectbox("Login As", ["Student Login", "Student Signup", "Admin Login"])

# Session state for Admin
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# ====================== STUDENT LOGIN =========================
if role == "Student Login":
    st.title("🎓 Student Face Attendance")
    student_id = st.text_input("Enter Student ID to Mark Attendance")
    camera = st.camera_input("Capture a photo")

    if camera and student_id:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img:
            temp_img.write(camera.getvalue())
            img_path = temp_img.name

        img = cv2.imread(img_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img_rgb)

        if encodings:
            face = encodings[0]

            if os.path.exists("EncodeFile.p"):
                with open("EncodeFile.p", "rb") as f:
                    encodeListKnown, studentIds = pickle.load(f)
            else:
                st.error("❌ Face encoding file not found.")
                st.stop()

            matches = face_recognition.compare_faces(encodeListKnown, face, tolerance=0.51)
            face_dist = face_recognition.face_distance(encodeListKnown, face)
            best_match_index = np.argmin(face_dist)

            if matches[best_match_index] and studentIds[best_match_index] == student_id:
                res = supabase.table("students").select("*").eq("id", student_id).limit(1).execute()
                student = res.data[0] if res.data else None

                if student:
                    now = datetime.now()
                    last_time = student.get("last_attendence_time")
                    last_dt = datetime.fromisoformat(last_time) if last_time else now - timedelta(seconds=31)

                    if (now - last_dt).total_seconds() >= 30:
                        new_total = student.get("total_attendence", 0) + 1
                        supabase.table("students").update({
                            "total_attendence": new_total,
                            "last_attendence_time": now.isoformat()
                        }).eq("id", student_id).execute()
                        st.success(f"✅ Attendance marked. Total: {new_total}")
                    else:
                        remaining = 30 - int((now - last_dt).total_seconds())
                        st.warning(f"⏳ Wait {remaining} seconds before marking again.")

                    st.info(f"🧾 Name: {student['name']}")
                    st.info(f"🎓 Major: {student['major']} | Year: {student['year']} | Standing: {student['standing']}")
                    #st.info(f"📊 Total Attendance: {student['total_attendence']}")
                else:
                    st.error("❌ Student not found.")
            else:
                st.error("⚠️ Face and ID mismatch.")
        else:
            st.error("❌ No face detected.")

# ====================== STUDENT SIGNUP ========================
elif role == "Student Signup":
    st.title("🆕 Register New Student")
    camera = st.camera_input("Capture Your Photo")

    with st.form("signup_form"):
        student_id = st.text_input("Student ID")
        name = st.text_input("Name")
        major = st.text_input("Major")
        year = st.number_input("Year", 1, 6)
        starting_year = st.number_input("Starting Year", 2000, 2100)
        standing = st.selectbox("Standing", ["G", "B", "P"])
        submit = st.form_submit_button("Register")

    if submit and camera and student_id:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img:
            temp_img.write(camera.getvalue())
            img_path = temp_img.name

        filename = f"{student_id}.jpg"
        with open(img_path, "rb") as f:
            file_bytes = f.read()
            upload_res = supabase.storage.from_("student-image").upload(
                path=filename,
                file=file_bytes,
                file_options={"x-upsert": "true", "content-type": "image/jpeg"}
            )
            if hasattr(upload_res, 'error') and upload_res.error:
                st.error(f"Upload failed: {upload_res.error}")
            else:
                st.success("✅ Upload successful")

        if not hasattr(upload_res, "error") or upload_res.error is None:
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

            subprocess.run(["python", "EncodeGenerator.py"])
            st.success(f"🎉 {name} registered successfully!")
        else:
            st.error("❌ Failed to upload image to Supabase.")

# ====================== ADMIN LOGIN ============================
elif role == "Admin Login":
    if not st.session_state.admin_logged_in:
        st.title("🔐 Admin Authentication")
        admin_user = st.text_input("Admin Username")
        admin_pass = st.text_input("Admin Password", type="password")

        ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
        ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

        if st.button("Login"):
            if admin_user == ADMIN_USERNAME and admin_pass == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.experimental_rerun()
            else:
                st.error("❌ Invalid credentials.")
        st.stop()

    # ========== ADMIN DASHBOARD ==========
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🗑️ Manage Students", "🚪 Logout"])

    with tab1:
        st.title("📊 Attendance Dashboard")
        students_res = supabase.table("students").select("*").execute()
        students = students_res.data or []

        if not students:
            st.warning("No student records found.")
            st.stop()

        df = pd.DataFrame(students)
        df['total_attendence'] = df['total_attendence'].astype(int)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Students", len(df))
        col2.metric("Attendance Entries", df['total_attendence'].sum())
        col3.metric("Average Attendance", round(df['total_attendence'].mean(), 2))

        st.divider()

        if 'standing' in df.columns:
            st.plotly_chart(px.bar(df.groupby('standing')['total_attendence'].sum().reset_index(),
                                   x='standing', y='total_attendence', color='standing',
                                   title="Attendance by Standing"), use_container_width=True)

        if 'major' in df.columns:
            st.plotly_chart(px.pie(df, values='total_attendence', names='major',
                                   title="Attendance by Major"), use_container_width=True)

        st.subheader("📋 Attendance Table")
        st.dataframe(df[['id', 'name', 'major', 'year', 'standing',
                         'total_attendence', 'last_attendence_time']]
                     .sort_values(by='total_attendence', ascending=False), use_container_width=True)

    # ========== DELETE STUDENT ==========
    with tab2:
        st.title("🗑️ Delete Student Record")

        try:
            student_list = supabase.table("students").select("id, name").execute().data
            if not student_list:
                st.warning("📭 No students found to delete.")
                st.stop()

            student_options = {f"{s['id']} - {s['name']}": s['id'] for s in student_list}
            selected_display = st.selectbox("Select Student to Delete", list(student_options.keys()))
            delete_id = student_options[selected_display]

            st.warning(f"⚠️ You are about to delete: **{selected_display}**")

            if st.button("🗑️ Confirm Delete", type="primary"):
                error_messages = []

                # 1. Delete from Supabase DB
                try:
                    supabase.table("students").delete().eq("id", delete_id).execute()
                    st.success("✅ Student record deleted from database")
                except Exception as e:
                    error_messages.append(f"Database deletion failed: {str(e)}")
                    st.error(f"❌ Database deletion failed: {str(e)}")

                # 2. Delete from Supabase Storage
                try:
                    deleted_from_storage = False
                    files = supabase.storage.from_("student-image").list()
                    for file in files:
                        file_name = file.get("name", "")
                        if file_name.startswith(str(delete_id)):
                            try:
                                supabase.storage.from_("student-image").remove([file_name])
                                st.success(f"✅ Deleted storage file: {file_name}")
                                deleted_from_storage = True
                            except Exception as e:
                                st.warning(f"⚠️ Failed to delete {file_name} from storage: {e}")
                    if not deleted_from_storage:
                        st.info("ℹ️ No matching image found in Supabase storage.")
                except Exception as e:
                    st.error(f"❌ Supabase storage deletion error: {e}")

                # 3. Delete from local Images1 folder
                try:
                    deleted_from_local = False
                    for file in os.listdir("Images1"):
                        if file.startswith(str(delete_id)):
                            path = os.path.join("Images1", file)
                            os.remove(path)
                            st.success(f"✅ Deleted local file: {file}")
                            deleted_from_local = True
                    if not deleted_from_local:
                        st.info("ℹ️ No matching local image found.")
                except Exception as e:
                    st.error(f"❌ Local file deletion error: {e}")

                # 4. Rebuild encodings
                try:
                    result = subprocess.run(["python", "EncodeGenerator.py"], capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        st.success("✅ Face encodings rebuilt successfully")
                    else:
                        st.warning(f"⚠️ Rebuild completed with warnings: {result.stderr}")
                except Exception as e:
                    error_messages.append(f"Encoding rebuild failed: {str(e)}")
                    st.warning(f"⚠️ Could not rebuild encodings: {str(e)}")

                # 5. Final Confirmation
                if not error_messages:
                    st.success(f"🎉 Successfully deleted student: {selected_display}")
                    st.rerun()
                else:
                    st.error("⚠️ Deletion completed with some issues. Check the messages above.")

        except Exception as e:
            st.error(f"❌ Error loading student list: {str(e)}")

    # ========== LOGOUT ==========
    with tab3:
        st.title("🚪 Logout")
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.experimental_rerun()