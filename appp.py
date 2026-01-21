import streamlit as st
import sqlite3
import pandas as pd
from io import BytesIO
from datetime import datetime, date

# Database connection (SQLite file-based)
DB_FILE = "clinic.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def fetch(query, params=None):
    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def execute(query, params=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()

def insert_patient(name, age, gender, phone):
    execute(
        "INSERT INTO patients (name, age, gender, phone) VALUES (?, ?, ?, ?)",
        (name, age, gender, phone)
    )

def insert_doctor(name, specialization):
    conn = get_connection()
    cur = conn.cursor()

    # check existing doctor
    cur.execute(
        "SELECT id FROM doctors WHERE name=? AND specialization=?",
        (name, specialization)
    )
    row = cur.fetchone()

    if row:
        conn.close()
        return row[0]
    # insert new doctor
    cur.execute(
        "INSERT INTO doctors (name, specialization) VALUES (?, ?)",
        (name, specialization)
    )
    conn.commit()
    doctor_id = cur.lastrowid
    conn.close()
    return doctor_id

def insert_appointment(pid, did, d, t, note):
    d = d.strftime("%Y-%m-%d")
    t = t.strftime("%H:%M:%S")

    if note is None:
        note = ""

    execute(
        "INSERT INTO appointments (patient_id, doctor_id, date, time, note) VALUES (?, ?, ?, ?, ?)",
        (int(pid), int(did), d, t, note)
    )

def fetch_patients():
    return fetch("SELECT * FROM patients")

def fetch_doctors():
    return fetch("SELECT * FROM doctors")

def fetch_appointments():
    return fetch("""
        SELECT a.id, p.name patient, d.name doctor, a.date, a.time, a.note
        FROM appointments a
        JOIN patients p ON p.id=a.patient_id
        JOIN doctors d ON d.id=a.doctor_id
        ORDER BY a.date DESC, a.time DESC
    """)

# page top configuration()
st.set_page_config("Clinic Appointment System", "🏥", layout="wide")
st.title("🏥 Clinic Appointment System")

menu = ["Dashboard","Add Patient","Add Doctor","Book Appointment","Add Prescription","View Appointments","Export to Excel"]
choice = st.sidebar.selectbox("Menu", menu)

st.markdown("""
<style>
[data-testid="stContainer"]{
    border: 5px solid white;
    border-radius: 8px;
    padding: 15px;
}
[data-testid="metric-container"]{
    text-align: center;
}
.stApp {
    background: linear-gradient(
        rgba(0,0,0,0.15),
        rgba(0,0,0,0.15)
    ),
    url("https://images.unsplash.com/photo-1526256262350-7da7584cf5eb");
    background-size: cover;
    background-attachment: fixed;
}
[data-testid="stSidebar"] {
    background: rgba(200,220,240,0.75);
    backdrop-filter: blur(8px);
}
</style>
""", unsafe_allow_html=True)

# Dashboard view
if choice == "Dashboard":

    st.header("📊 Dashboard")

    patients = fetch_patients()
    doctors = fetch_doctors()
    appointments = fetch_appointments()

    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Patients", len(patients),"+100%")
        col2.metric("Doctors", len(doctors),"+100%")
        col3.metric("Appointments", len(appointments),"+100%")
        col4.metric("Today", date.today().strftime("%d-%m-%Y"),date.today().strftime("%B"))

    st.subheader("Recent Appointments")
    st.dataframe(appointments)

    st.markdown("---")

    st.subheader("👨‍⚕ Doctor Profile")
    docs = fetch("SELECT name, specialization, qualification, rating, about FROM doctors")

    doctor_name = st.selectbox("Select Doctor", docs["name"])
    
    filtered = docs[docs["name"] == doctor_name]

    if filtered.empty:
      st.warning("Doctor details not found")
    else:
       doc = filtered.iloc[0]

       st.markdown(f"""
    **👨‍⚕ {doc['name']}**  
    🧠 {doc['specialization']}  
    🎓 {doc['qualification']}  
    ⭐ {doc['rating']}/5  
    📝 {doc['about']}
    """)




    st.markdown("---")

    st.subheader("💰 Doctor Earnings")
    earnings = fetch("""
        SELECT d.name, d.fees,
               COUNT(a.id) visits,
               COUNT(a.id)*d.fees earnings
        FROM doctors d
        LEFT JOIN appointments a ON a.doctor_id=d.id
        GROUP BY d.id
    """)
    st.dataframe(earnings)

    st.markdown("---")

    st.subheader("📍 Clinic Location")
    st.components.v1.html(
    """
    <iframe
        src="https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d3770.0877133263957!2d72.8843002!3d19.1038076!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3be7c86df9ccf153%3A0x17c26c0037219f65!2sParamount%20General%20Hospital%20%26%20ICCU!5e0!3m2!1sen!2sin!4v1765694395108!5m2!1sen!2sin"
        width="100%"
        height="450"
        style="border:0;"
        allowfullscreen=""
        loading="lazy"
        referrerpolicy="no-referrer-when-downgrade">
    </iframe>
    """,
    height=500
    )

# Adding of patients
if choice == "Add Patient":

    st.header("➕ Add Patient")

    name = st.text_input("Name")
    age = st.number_input("Age", 1, 120)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    phone = st.text_input("Phone")

    if st.button("Save"):
        insert_patient(name, age, gender, phone)
        st.success("Patient added successfully!")

# Adding of doctor's
if choice == "Add Doctor":

    st.header("➕ Add Doctor")

    name = st.selectbox(
        "Select Doctor",
        ["Select","Dr.Python","Dr.Sohel","Dr.Sajid","Dr.Salunkhe","Dr.Moinuddin"]
    )

    specialization = st.selectbox(
        "Specialization",
        ["Select","Coderologist", "Neurologist", "ENT", "Cardiologist", "Gastrologist"]
    )

    if st.button("Save Doctor"):
        if name == "Select" or specialization == "Select":
            st.warning("Please select a valid Doctor name and Specialization")
        else:
            insert_doctor(name, specialization)
            st.success("Doctor added successfully!")

###
# Adding Prescriptions
if choice == "Add Prescription":

    st.header("💊 Add Prescription")

    appointments = fetch_appointments()
    
    if len(appointments) == 0:
        st.warning("No appointments found!")
    else:
        # Select appointment
        appt = st.selectbox(
            "Select Appointment",
            appointments.apply(lambda x: f"{x['id']} - {x['patient']} with {x['doctor']} on {x['date']}", axis=1)
        )
        
        appt_id = int(appt.split(" - ")[0])  

        medicines = st.text_area("Medicines")
        advice = st.text_area("Advice")

        if st.button("Save Prescription"):
            execute(
                "INSERT INTO prescriptions (appointment_id, medicines, advice) VALUES (?, ?, ?)",
                (appt_id, medicines, advice)
            )
            st.success("Prescription saved successfully!")

    # Show all prescriptions
    st.subheader("📄 All Prescriptions")
    prescriptions = fetch("SELECT id, appointment_id, medicines, advice FROM prescriptions")
    st.dataframe(prescriptions)
###

# appointment box
if choice == "Book Appointment":

    st.header("📅 Book Appointment")

    patients = fetch_patients()
    doctors = fetch_doctors()

    p = st.selectbox("Patient", patients["name"])
    d = st.selectbox("Doctor", doctors["name"])

    pid = patients[patients.name == p].id.values[0]
    did = doctors[doctors.name == d].id.values[0]

    ap_date = st.date_input("Date", date.today())
    ap_time = st.time_input("Time", datetime.now().time())
    note = st.text_area("Note")

    if st.button("Book"):
        insert_appointment(pid, did, ap_date, ap_time, note)
        st.success("Appointment booked!")

# Show all appointments
if choice == "View Appointments":
    st.header("📄 All Appointments")
    st.dataframe(fetch_appointments())

# Export to excel
if choice == "Export to Excel":
    st.header("📤 Export Database")

    patients = fetch_patients()
    doctors = fetch_doctors()
    appointments = fetch_appointments()
    prescriptions = fetch(
        "SELECT id, appointment_id, medicines, advice FROM prescriptions"
    )

    # Fetch earnings
    earnings = fetch("""
        SELECT 
            d.id,
            d.name AS doctor_name,
            d.fees,
            COUNT(a.id) AS visits,
            COALESCE(COUNT(a.id),0) * d.fees AS earnings
        FROM doctors d
        LEFT JOIN appointments a 
            ON a.doctor_id = d.id
        GROUP BY d.id, d.name, d.fees
    """)

    def create_excel():
        out = BytesIO()
        with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
            patients.to_excel(writer, "Patients", index=False)
            doctors.to_excel(writer, "Doctors", index=False)
            appointments.to_excel(writer, "Appointments", index=False)
            prescriptions.to_excel(writer, "Prescriptions", index=False)
            earnings.to_excel(writer, "Earnings", index=False)  
        return out.getvalue()

    st.download_button(
        "📥 Download Excel",
        create_excel(),
        "clinic_database.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Footer
st.markdown("---")
st.success("Thanks for Visiting, Visit again 🙏")

# Background
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(
            rgba(0,0,0,0.15),   
            rgba(0,0,0,0.15)
        ), 
        url("https://images.unsplash.com/photo-1526256262350-7da7584cf5eb");
        background-size: cover;
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar Background
st.markdown(
    """
    <style>

    [data-testid="stSidebar"] {
        background: rgba(200,220,240,0.75);  
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border-right: 1px solid rgba(255,255,255,0.2);
    }

    [data-testid="stSidebar"] * {
        color: #003049 !important; 
        font-weight: 400;
    }

    .stSelectbox > div > div {
        background-color: rgba(255,255,255,0.9) ;
        border-radius: 50px;
        color: #003049 !important;
        border: 1px solid rgba(0,0,0,0.1);
    }

    .stSelectbox > div > div:hover {
        background-color: rgba(235,245,255,1) ;
 
    }

    </style>
    """,
    unsafe_allow_html=True
)
