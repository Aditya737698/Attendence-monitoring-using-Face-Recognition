# Attendance Monitoring using Face Recognition 🎯

A Python-based attendance monitoring system that uses face recognition technology to automatically detect and mark attendance of individuals in real-time using a webcam.

## 🚀 Features

- Real-time face detection using OpenCV
- Face recognition using `face_recognition` library
- Automatically marks attendance with name and timestamp
- Stores attendance in a CSV file
- Easily extendable and modular
- Realtime database sync using Supabase


## 🛠️ Technologies Used

- Python 3
- OpenCV
- face_recognition
- NumPy
- CSV module
- Supabase (for cloud and real-time sync)


## ✅ Setup Instructions

**1. Clone the Repository**
   ```bash
   git clone https://github.com/Aditya737698/Attendence-monitoring-using-Face-Recognition.git
   cd Attendence-monitoring-using-Face-Recognition

   ```

**2. Install Dependencies**
  ```bash
pip install -r requirements.txt
  ```
**3. Add Known Faces**
```bash
Add clear front-facing images to the dataset/ folder.

Name each image file with the person's name (e.g., Aditya.jpg).
```
**4. Encode Faces**
``` bash
python EncodeGenerator.py
```

**📸 Sample Output**
```bash
Webcam opens and detects faces in real-time

Recognized faces are marked present:
✅ Aditya marked present at 09:42:15
```
**🔧 Future Enhancements**
```bash
Add GUI with Tkinter or PyQt

Cloud storage or database integration

Face mask detection

Email/SMS alerts for absenteeism
```
**🙌 Author**
```bash
Aditya Mahendra Patil – GitHub Profile
```
**📃 License**
```bash
This project is licensed under the MIT License - see the LICENSE file for details.
```
