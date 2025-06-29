from supabase import create_client
import face_recognition
import cv2
import os
import pickle
from dotenv import load_dotenv

# Load Supabase credentials
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Define local image folder
IMAGE_FOLDER = "Images1"
BUCKET_NAME = "student-image"

# Create image folder if it doesn't exist
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Download all student images from Supabase Storage
print("📥 Downloading images from Supabase...")
files = supabase.storage.from_(BUCKET_NAME).list()
for file in files:
    file_name = file['name']
    file_path = os.path.join(IMAGE_FOLDER, file_name)
    
    # Skip if already exists (optional, can force update)
    if not os.path.exists(file_path):
        data = supabase.storage.from_(BUCKET_NAME).download(file_name)
        with open(file_path, "wb") as f:
            f.write(data)
print("✅ All images downloaded.\n")

# Encode faces
print("🔍 Encoding faces...")
encodeList = []
studentIds = []

for img_name in os.listdir(IMAGE_FOLDER):
    img_path = os.path.join(IMAGE_FOLDER, img_name)
    img = cv2.imread(img_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(img_rgb)
    
    if encodings:
        encodeList.append(encodings[0])
        studentIds.append(os.path.splitext(img_name)[0])
    else:
        print(f"⚠️ No face found in {img_name}")

# Save encoding file
with open("EncodeFile.p", "wb") as f:
    pickle.dump((encodeList, studentIds), f)

print(f"✅ Encoding complete. Total students: {len(studentIds)}")