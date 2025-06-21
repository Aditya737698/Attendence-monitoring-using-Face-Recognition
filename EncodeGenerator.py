# EncoderGenerator.py

import os
import cv2
import face_recognition
import pickle
from supabase import create_client, Client

# ✅ Supabase config
url = "https://daqnmrsardrtjqilyzsi.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRhcW5tcnNhcmRydGpxaWx5enNpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA1MTQ1MDEsImV4cCI6MjA2NjA5MDUwMX0.Hfqvjs-ZxowpMtvP38QeHtefhiyKt0er7IEMLNyqVuc"
supabase: Client = create_client(url, key)

# ✅ Local image folder
folderPath = "Images1"
pathList = os.listdir(folderPath)
print(pathList)

imgList = []
studentIds = []

for path in pathList:
    # Read & encode
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])

    # ✅ Upload image to Supabase Storage
    fileName = f'{folderPath}/{path}'
    with open(fileName, "rb") as f:
        res = supabase.storage.from_("student-image").upload(path, f)
        print(f"Uploaded {path} | Response: {res}")

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

print("Encoding Started ..")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding Complete")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()


# import os
# import cv2
# import face_recognition_models
# import face_recognition
# import pickle
# from supabase import create_client, Client
# import supabase
# from supabase.client import ClientOptions

# url="https://daqnmrsardrtjqilyzsi.supabase.co"
# key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRhcW5tcnNhcmRydGpxaWx5enNpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA1MTQ1MDEsImV4cCI6MjA2NjA5MDUwMX0.Hfqvjs-ZxowpMtvP38QeHtefhiyKt0er7IEMLNyqVuc"
# supabase: Client = create_client(  url,  key)

# # Importing student images 
# folderPath ="Images1"
# pathList=os.listdir(folderPath)
# print(pathList)
# imgList=[]
# studentIds=[]
# for path in pathList:
#     imgList.append(cv2.imread(os.path.join(folderPath, path)))
#     studentIds.append(os.path.splitext(path)[0])  
    
#     fileName=os.path.join(folderPath, path)
#     bucket=supabase.storage.bucket()
#     blob=bucket.blob(fileName)
#     blob.upload_from_filename(fileName)
#     #print(path)
#     #print(os.path.splitext(path)[0]) # Extracting the name from the file name - 0th index
# # print(studentIds)

# def findEncodings(imgagesList):
#     encodeList = []
#     for img in imgagesList:
#         img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
#         encode=face_recognition.face_encodings(img)[0]
#         encodeList.append(encode)
#     return encodeList

# print("Encoding Started ..")
# encodeListKnown = findEncodings(imgList)
# encodeListKnownWithIds=[encodeListKnown, studentIds ]
# #print(encodeListKnown)
# print("Encoding Complete")

# file=open("EncodeFile.p", 'wb')
# pickle.dump(encodeListKnownWithIds, file)
# file.close()