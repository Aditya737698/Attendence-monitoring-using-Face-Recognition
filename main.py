# main.py
import os
import cv2
import pickle
import cvzone
import face_recognition
import numpy as np

from supabase import create_client, Client

# ✅ Supabase config
url = "https://daqnmrsardrtjqilyzsi.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRhcW5tcnNhcmRydGpxaWx5enNpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA1MTQ1MDEsImV4cCI6MjA2NjA5MDUwMX0.Hfqvjs-ZxowpMtvP38QeHtefhiyKt0er7IEMLNyqVuc"
supabase: Client = create_client(url, key)

cap=cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

imgBackground = cv2.imread("Resources/background.png")

# Load the mode images into a list
folderModePath ="Resources/Modes"
modePathList=os.listdir(folderModePath)
imgModeList=[]
#print(modePathList)
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
#print(len(imgModeList))

# load the encoding file

print("Loading Encode File ...")
file=open("EncodeFile.p", 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
#print(studentIds)
print("Encode File Loaded")

modeType=0
counter=0
id=-1

# Initialize the webcam
while True:
    success, img=cap.read()
    
    imgS= cv2.resize(img,(0,0), None, 0.25, 0.25)  # Resize the image to speed up processing
    imgS=cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)  # Convert the image to RGB format
    
    faceCurFrame = face_recognition.face_locations(imgS)  # Find the face locations in the current frame
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)  # Get the encodings of the faces in the current frame
    
    imgBackground[162:162+480, 55:55+640]=img
    imgBackground[44:44+633, 808:808+414]=imgModeList[0]  # Display the first mode image
    
    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        matches= face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis= face_recognition.face_distance(encodeListKnown, encodeFace)
        #print("matches:", matches)
        #print("faceDis:", faceDis)
        matchIndex = np.argmin(faceDis)  # Get the index of the closest match
        #print("matchIndex:", matchIndex)
        if matches[matchIndex]:
            #print("Known Face Detected")
            #print(studentIds[matchIndex])
            y1, x2, y2, x1=faceLoc  # Get the coordinates of the face location
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1 # Scale the coordinates to match the original image size
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
            id=studentIds[matchIndex]
            #print(id)
            if counter==0:
                counter=1
                
    if counter!=0:
        
        if counter==1:
            # Fetch student info from Supabase
            
            studentInfo = (supabase.table('students').select('*').eq('id', id).single().execute())
            print(studentInfo)
        counter+=1
            
    cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)