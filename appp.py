import streamlit as st
import sqlite3
import pandas as pd
from io import BytesIO
from datetime import datetime, date

# ---------------- DATABASE (SQLite) ----------------
DB_FILE = "clinic.db"

@st.cache_resource
def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    return conn

conn = get_connection()

def fetch(query, params=None):
    return pd.read_sql(query, conn, params=params)

def execute(query, params=None):
    cur = conn.cursor()
    cur.execute(query, params or [])
    conn.commit()

# ---------------- CREATE TABLES ----------------
execute("""
CREATE TABLE IF NOT EXISTS patients(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    gender TEXT,
    phone TEXT
)
""")

execute("""
CREATE TABLE IF NOT EXISTS doctors(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    specialization TEXT,
    qualification TEXT DEFAULT 'MBBS',
    rating REAL DEFAULT 4.5,
    about TEXT DEFAULT 'Experienced Doctor',
    fees INTEGER DEFAULT 500
)
""")

execute("""
CREATE TABLE IF NOT EXISTS appointments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    doctor_id INTEGER,
    date TEXT,
    time TEXT,
    note TEXT
)
""")

execute("""
CREATE TABLE IF NOT EXISTS prescriptions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id INTEGER,
    medicines TEXT,
    advice TEXT
)
""")

# ---------------- FUNCTIONS ----------------
def insert_patient(name, age, gender, phone):
    execute(
        "INSERT INTO patients VALUES (NULL,?,?,?,?)",
        (name, age, gender, phone)
    )

def insert_doctor(name, specialization):
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM doctors WHERE name=? AND specialization=?",
        (name, specialization)
    )
    row = cur.fetchone()
    if row:
        return row[0]

    cur.execute(
        "INSERT INTO doctors (name, specialization) VALUES (?,?)",
        (name, specialization)
    )
    conn.commit()
    return cur.lastrowid

def insert_appointment(pid, did, d, t, note):
    execute(
        "INSERT INTO appointments VALUES (NULL,?,?,?,?,?)",
        (pid, did, d.strftime("%Y-%m-%d"), t.strftime("%H:%M:%S"), note or "")
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

# ---------------- UI ----------------
st.set_page_config("Clinic Appointment System", "🏥", layout="wide")
st.title("🏥 Clinic Appointment System")

menu = [
    "Dashboard","Add Patient","Add Doctor",
    "Book Appointment","Add Prescription",
    "View Appointments","Export to Excel"
]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------- DASHBOARD ----------------
if choice == "Dashboard":
    patients = fetch_patients()
    doctors = fetch_doctors()
    appointments = fetch_appointments()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Patients", len(patients))
    col2.metric("Doctors", len(doctors))
    col3.metric("Appointments", len(appointments))
    col4.metric("Today", date.today().strftime("%d-%m-%Y"))

    st.subheader("Recent Appointments")
    st.dataframe(appointments)

# ---------------- ADD PATIENT ----------------
if choice == "Add Patient":
    st.header("➕ Add Patient")
    name = st.text_input("Name")
    age = st.number_input("Age", 1, 120)
    gender = st.selectbox("Gender", ["Male","Female","Other"])
    phone = st.text_input("Phone")

    if st.button("Save"):
        insert_patient(name, age, gender, phone)
        st.success("Patient added successfully")

# ---------------- ADD DOCTOR ----------------
if choice == "Add Doctor":
    st.header("➕ Add Doctor")
    name = st.text_input("Doctor Name")
    specialization = st.text_input("Specialization")

    if st.button("Save Doctor"):
        insert_doctor(name, specialization)
        st.success("Doctor saved")

# ---------------- BOOK APPOINTMENT ----------------
if choice == "Book Appointment":
    patients = fetch_patients()
    doctors = fetch_doctors()

    if len(patients)==0 or len(doctors)==0:
        st.warning("Add patients and doctors first")
    else:
        p = st.selectbox("Patient", patients["name"])
        d = st.selectbox("Doctor", doctors["name"])

        pid = patients[patients.name==p].id.values[0]
        did = doctors[doctors.name==d].id.values[0]

        ap_date = st.date_input("Date", date.today())
        ap_time = st.time_input("Time", datetime.now().time())
        note = st.text_area("Note")

        if st.button("Book"):
            insert_appointment(pid, did, ap_date, ap_time, note)
            st.success("Appointment booked")

# ---------------- PRESCRIPTION ----------------
if choice == "Add Prescription":
    appointments = fetch_appointments()
    if len(appointments)==0:
        st.warning("No appointments")
    else:
        appt = st.selectbox(
            "Appointment",
            appointments.apply(
                lambda x: f"{x['id']} - {x['patient']} with {x['doctor']}",
                axis=1
            )
        )
        appt_id = int(appt.split(" - ")[0])

        meds = st.text_area("Medicines")
        advice = st.text_area("Advice")

        if st.button("Save Prescription"):
            execute(
                "INSERT INTO prescriptions VALUES (NULL,?,?,?)",
                (appt_id, meds, advice)
            )
            st.success("Prescription saved")

# ---------------- VIEW APPOINTMENTS ----------------
if choice == "View Appointments":
    st.dataframe(fetch_appointments())

# ---------------- EXPORT EXCEL ----------------
if choice == "Export to Excel":
    out = BytesIO()
    with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
        fetch_patients().to_excel(writer, "Patients", index=False)
        fetch_doctors().to_excel(writer, "Doctors", index=False)
        fetch_appointments().to_excel(writer, "Appointments", index=False)
        fetch("SELECT * FROM prescriptions").to_excel(writer, "Prescriptions", index=False)

    st.download_button(
        "Download Excel",
        out.getvalue(),
        "clinic_database.xlsx"
    )

st.success("Thanks for Visiting 🙏")
st.markdown("""
<style>

/* ----------- MAIN APP BACKGROUND ----------- */
.stApp {
    background: linear-gradient(
        rgba(0,0,0,0.15),
        rgba(0,0,0,0.15)
    ),
    url("https://images.unsplash.com/photo-1526256262350-7da7584cf5eb");
    background-size: cover;
    background-attachment: fixed;
}

/* ----------- SIDEBAR GLASS EFFECT ----------- */
[data-testid="stSidebar"] {
    background: rgba(200,220,240,0.75);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-right: 1px solid rgba(255,255,255,0.3);
}

/* Sidebar text color */
[data-testid="stSidebar"] * {
    color: #003049 !important;
    font-weight: 500;
}

/* ----------- CONTAINERS / CARDS ----------- */
[data-testid="stContainer"] {
    background: rgba(255,255,255,0.88);
    border-radius: 12px;
    padding: 18px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.12);
}

/* ----------- METRIC BOX STYLE ----------- */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.95);
    border-radius: 12px;
    padding: 10px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

/* ----------- SELECTBOX / INPUT ----------- */
.stSelectbox > div > div,
.stTextInput > div > div,
.stNumberInput > div > div,
.stTextArea > div > textarea {
    background-color: rgba(255,255,255,0.95);
    border-radius: 25px;
    border: 1px solid rgba(0,0,0,0.15);
    color: #003049;
}

/* Hover effect */
.stSelectbox > div > div:hover {
    background-color: rgba(235,245,255,1);
}

/* ----------- BUTTON STYLE ----------- */
.stButton > button {
    background: linear-gradient(135deg, #003049, #0077b6);
    color: white;
    border-radius: 25px;
    padding: 0.5em 1.8em;
    font-weight: 600;
    border: none;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.05);
    background: linear-gradient(135deg, #0077b6, #003049);
}

/* ----------- DATAFRAME ----------- */
[data-testid="stDataFrame"] {
    background: white;
    border-radius: 12px;
    padding: 10px;
}

/* ----------- FOOTER MESSAGE ----------- */
footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)
