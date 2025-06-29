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

# Constants
IMAGE_FOLDER = "Images1"
BUCKET_NAME = "student-image"
VALID_EXTENSIONS = [".jpg", ".jpeg", ".png"]
FORCE_DOWNLOAD = False

# Ensure image folder exists
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Step 1: Download all images
print("📥 Downloading images from Supabase...")
files = supabase.storage.from_(BUCKET_NAME).list()
files = [f for f in files if os.path.splitext(f['name'])[1].lower() in VALID_EXTENSIONS]

for file in files:
    file_name = file['name']
    file_path = os.path.join(IMAGE_FOLDER, file_name)

    if FORCE_DOWNLOAD or not os.path.exists(file_path):
        try:
            data = supabase.storage.from_(BUCKET_NAME).download(file_name)
            with open(file_path, "wb") as f:
                f.write(data)
            print(f"✅ Downloaded: {file_name}")
        except Exception as e:
            print(f"❌ Failed to download {file_name}: {str(e)}")

print("📂 Image download complete.\n")

# Step 2: Encode all faces
print("🔍 Encoding faces...")
encodeList = []
studentIds = []
skipped_files = []

for img_name in sorted(os.listdir(IMAGE_FOLDER)):
    img_path = os.path.join(IMAGE_FOLDER, img_name)

    if os.path.splitext(img_name)[1].lower() not in VALID_EXTENSIONS:
        continue

    img = cv2.imread(img_path)
    if img is None:
        print(f"❌ Could not read {img_name}")
        skipped_files.append(img_name)
        continue

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(img_rgb)

    if encodings:
        encodeList.append(encodings[0])
        studentIds.append(os.path.splitext(img_name)[0])
    else:
        print(f"⚠️ No face found in {img_name}")
        skipped_files.append(img_name)

# Step 3: Save to EncodeFile
with open("EncodeFile.p", "wb") as f:
    pickle.dump((encodeList, studentIds), f)

# Step 4: Report
print(f"\n✅ Encoding complete.")
print(f"👨‍🎓 Total students encoded: {len(studentIds)}")
print(f"⚠️ Skipped or failed files: {len(skipped_files)}")
if skipped_files:
    print("🗒️ Skipped files:")
    for name in skipped_files:
        print(f" - {name}")