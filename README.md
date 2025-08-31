# 🎓 Face Recognition Attendance System

A modern web-based attendance monitoring system that uses facial recognition technology to automatically mark student attendance. Built with Streamlit, OpenCV, and Supabase.

## 🌟 Features

- **Real-time Face Recognition**: Instant face detection and matching
- **Student Registration**: Easy signup with photo capture
- **Attendance Tracking**: Automatic attendance marking with duplicate prevention
- **Admin Dashboard**: Comprehensive analytics and student management
- **Cloud Storage**: Secure image storage with Supabase
- **Responsive Design**: Works on desktop and mobile devices

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Python web framework)
- **Face Recognition**: `face_recognition` library (built on dlib)
- **Computer Vision**: OpenCV for image processing
- **Database**: Supabase (PostgreSQL with real-time features)
- **Storage**: Supabase Storage for student photos
- **Visualization**: Plotly for interactive charts

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Supabase account
- Webcam access

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd FaceRecognition
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file:
   ```env
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your_admin_password
   ```

4. **Set up Supabase**
   - Create a new Supabase project
   - Create a `students` table with the following schema:
   ```sql
   CREATE TABLE students (
       id VARCHAR PRIMARY KEY,
       name VARCHAR NOT NULL,
       major VARCHAR,
       year INTEGER,
       starting_year INTEGER,
       standing VARCHAR,
       total_attendence INTEGER DEFAULT 0,
       last_attendence_time TIMESTAMP
   );
   ```
   - Create a storage bucket named `student-image`

5. **Initialize the system**
   ```bash
   python EncodeGenerator.py
   ```

6. **Run the application**
   ```bash
   streamlit run live_attendance.py
   ```

## 📱 Usage

### Student Login
1. Select "Student Login" from the sidebar
2. Enter your Student ID
3. Capture your photo using the camera
4. System will verify your face and mark attendance

### Student Registration
1. Select "Student Signup" from the sidebar
2. Fill in your details
3. Capture your photo
4. Submit to register

### Admin Access
1. Select "Admin Login" from the sidebar
2. Enter admin credentials
3. Access dashboard and management features

## 🌐 Deployment

### Local Development
```bash
streamlit run live_attendance.py --server.port 8501
```

### Cloud Deployment (Render)
1. Push code to GitHub
2. Connect repository to Render
3. Add environment variables in Render dashboard
4. Deploy and wait for build completion

## 📊 Project Structure

```
FaceRecognition/
├── live_attendance.py          # Main application
├── dashboard.py                # Analytics dashboard
├── EncodeGenerator.py          # Face encoding processor
├── AddDataToDatabase.py        # Database seeder
├── requirements.txt            # Python dependencies
├── Images1/                    # Student photos
└── temp/                       # Temporary files
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Your Supabase project URL | Yes |
| `SUPABASE_KEY` | Your Supabase anon key | Yes |
| `ADMIN_USERNAME` | Admin login username | No (default: admin) |
| `ADMIN_PASSWORD` | Admin login password | Yes |

### Supabase Setup

1. **Database Table**
   ```sql
   CREATE TABLE students (
       id VARCHAR PRIMARY KEY,
       name VARCHAR NOT NULL,
       major VARCHAR,
       year INTEGER,
       starting_year INTEGER,
       standing VARCHAR,
       total_attendence INTEGER DEFAULT 0,
       last_attendence_time TIMESTAMP
   );
   ```

2. **Storage Bucket**
   - Create a bucket named `student-image`
   - Set appropriate permissions

## 🔍 Troubleshooting

### Common Issues

1. **dlib Installation Fails**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install cmake build-essential libdlib-dev
   
   # macOS
   brew install cmake dlib
   
   # Windows
   conda install -c conda-forge dlib
   ```

2. **Camera Not Working**
   - Ensure HTTPS is enabled (required for camera access)
   - Check browser permissions
   - Try a different browser

3. **Face Recognition Issues**
   - Ensure good lighting
   - Face should be clearly visible
   - Check image quality

4. **Database Connection Errors**
   - Verify Supabase credentials
   - Check network connectivity
   - Ensure table exists

## 🔒 Security Considerations

- **HTTPS Required**: Camera access requires secure connection
- **Environment Variables**: Never commit secrets to version control
- **Input Validation**: All user inputs are validated
- **Rate Limiting**: 30-second cooldown between attendance marks
- **Admin Authentication**: Secure admin access

## 📈 Performance Optimization

- **Reduce image resolution** for faster processing
- **Use SSD storage** for better I/O performance
- **Optimize database queries** with proper indexing
- **Cache face encodings** in memory

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation

---

**Note**: This system requires a webcam and works best with modern browsers that support camera access.

