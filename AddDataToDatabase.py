# AddToDataBase.py
from supabase import create_client, Client

# ✅ Replace with your project details
url = "https://daqnmrsardrtjqilyzsi.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRhcW5tcnNhcmRydGpxaWx5enNpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA1MTQ1MDEsImV4cCI6MjA2NjA5MDUwMX0.Hfqvjs-ZxowpMtvP38QeHtefhiyKt0er7IEMLNyqVuc"

supabase: Client = create_client(url, key)

# ✅ Your data (just like Firebase)
data = {
    "243534": {
        "name": "Aditya Patil",
        "major": "ML",
        "starting_year": 2022,
        "total_attendence": 6,
        "standing": "G",
        "year": 3,
        "last_attendence_time": "2024-06-21 00:40:34"
    },
    
    "963852": {
        "name": "Elon Musk",
        "major": "SpaceX",
        "starting_year": 2020,
        "total_attendence": 8,
        "standing": "G",
        "year": 4,
        "last_attendence_time": "2024-06-21 00:40:34"
    },
    "852741": {
        "name": "Emly Blunt",
        "major": "Economics",
        "starting_year": 2012,
        "total_attendence": 9,
        "standing": "B",
        "year": 2,
        "last_attendence_time": "2024-06-21 00:40:34"
    }
}

# ✅ Loop through and insert each student
for key, value in data.items():
    student = {
        "id": key,  # custom ID like Firebase key
        "name": value["name"],
        "major": value["major"],
        "starting_year": value["starting_year"],
        "total_attendence": value["total_attendence"],
        "standing": value["standing"],
        "year": value["year"],
        "last_attendence_time": value["last_attendence_time"]
    }

    # Insert into Supabase table 'students'
    res = supabase.table("students").insert(student).execute()
    print(res)

