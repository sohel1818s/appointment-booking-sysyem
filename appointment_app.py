import streamlit as st
import mysql.connector
import pandas as pd
from io import BytesIO
from datetime import datetime, date

DB = {
    "host": "localhost",
    "user": "root",
    "password": "@dmin$12345678",
    "database": "clinic_db"
}

def get_connection():
    return mysql.connector.connect(**DB)

# DB helps
def fetch(query, params=None):
    conn = get_connection()
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

def execute(query, params=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()

# Insert Functions
def insert_patient(name, age, gender, phone):
    execute("INSERT INTO patients (name, age, gender, phone) VALUES (%s, %s, %s, %s)",
            (name, age, gender, phone))

def insert_doctor(name, specialization):
    execute("INSERT INTO doctors (name, specialization) VALUES (%s, %s)",
            (name, specialization))

def insert_appointment(patient_id, doctor_id, date_, time_, note):
    execute("""
        INSERT INTO appointments (patient_id, doctor_id, date, time, note)
        VALUES (%s, %s, %s, %s, %s)
    """, (patient_id, doctor_id, date_, time_, note))

# Update Functions
def update_patient(id_, name, age, gender, phone):
    execute("UPDATE patients SET name=%s, age=%s, gender=%s, phone=%s WHERE id=%s",
            (name, age, gender, phone, id_))

def update_doctor(id_, name, specialization):
    execute("UPDATE doctors SET name=%s, specialization=%s WHERE id=%s",
            (name, specialization, id_))

def update_appointment(id_, patient_id, doctor_id, date_, time_, note):
    execute("""
        UPDATE appointments SET patient_id=%s, doctor_id=%s, date=%s, time=%s, note=%s WHERE id=%s
    """, (patient_id, doctor_id, date_, time_, note, id_))

# Delete Functions
def delete_record(table, id_):
    execute(f"DELETE FROM {table} WHERE id=%s", (id_,))

# Fetch Tables
def fetch_patients():
    return fetch("SELECT * FROM patients")

def fetch_doctors():
    return fetch("SELECT * FROM doctors")

def fetch_appointments():
    return fetch("""
        SELECT a.id, p.name AS patient, d.name AS doctor, a.date, a.time, a.note
        FROM appointments a
        JOIN patients p ON p.id = a.patient_id
        JOIN doctors d ON d.id = a.doctor_id
        ORDER BY a.date DESC, a.time DESC
    """)

# ---------------- LOGIN SYSTEM ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login_page():
    st.title("🔐 Admin Login")

    username = st.text_input("Username",placeholder = "admin")
    password = st.text_input("Password", type="password",value = "admin123")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

if not st.session_state.logged_in:
    login_page()
    st.stop()

# Mian page
st.set_page_config(page_title = "Clinic Appointment System",
                   page_icon = "🏥",
                   layout = "wide")
st.title("🏥 Clinic Appointment System")

menu = [
    "Dashboard",
    "Add Patient", "Add Doctor", "Book Appointment",
    "View Appointments",
    "Edit/Delete Records",
    "Export to Excel",
    "Logout"
]

choice = st.sidebar.selectbox("Menu", menu)

# Logout
if choice == "Logout":
    st.session_state.logged_in = False
    st.rerun()

# Dashboard
if choice == "Dashboard":
    st.header("📊 Dashboard")
    patients = fetch_patients()
    doctors = fetch_doctors()
    appointments = fetch_appointments()

    col1, col2, col3 = st.columns(3)
    col1.metric("Patients", len(patients))
    col2.metric("Doctors", len(doctors))
    col3.metric("Appointments", len(appointments))

    st.subheader("Recent Appointments")
    st.dataframe(appointments)

# patients records..
if choice == "Add Patient":
    st.header("➕ Add Patient")

    name = st.text_input("Name")
    age = st.number_input("Age", 1, 120)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    phone = st.text_input("Phone")

    if st.button("Save"):
        insert_patient(name, age, gender, phone)
        st.success("Patient added!")

# doctor records
if choice == "Add Doctor":
    st.header("➕ Add Doctor")

    name = st.selectbox("Select Doctor's",["Dr.python","Dr.Sohel","Dr.Sajid","Dr.Salunkhe","Dr.Moinuddin"])
    specialization = st.selectbox("Select Specialization",["coderrologist","Neurologist","ENT","Cardiologist","Gastologist"])

    if st.button("Save"):
        insert_doctor(name, specialization)
        st.success("Doctor added!")

# Book Appointment
if choice == "Book Appointment":
    st.header("📅 Book Appointment")

    patients = fetch_patients()
    doctors = fetch_doctors()

    patient_sel = st.selectbox("Select Patient", patients['name'])
    doctor_sel = st.selectbox("Select Doctor", doctors['name'])

    patient_id = int(patients[patients['name'] == patient_sel]['id'].values[0])
    doctor_id = int(doctors[doctors['name'] == doctor_sel]['id'].values[0])

    date_ = st.date_input("Date", date.today())
    time_ = st.time_input("Time", datetime.now().time())
    note = st.text_area("Note")

    if st.button("Book"):
        insert_appointment(patient_id, doctor_id, date_, time_, note)
        st.success("Appointment booked!")

# View details
if choice == "View Appointments":
    st.header("📄 All Appointments")
    st.dataframe(fetch_appointments())

# Update and delete
if choice == "Edit/Delete Records":
    st.header("✏ Edit & 🗑 Delete Records")

    tab = st.selectbox("Select Table", ["Patients", "Doctors", "Appointments"])

    if tab == "Patients":
        df = fetch_patients()
        st.dataframe(df)

        id_ = st.number_input("Enter Patient ID to Edit/Delete", 1)
        if id_ in df["id"].values:
            name = st.text_input("Name", df[df.id == id_].iloc[0].name)
            age = st.number_input("Age", 1, 120, df[df.id == id_].iloc[0].age)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                                  index=["Male","Female","Other"].index(df[df.id == id_].iloc[0].gender))
            phone = st.text_input("Phone", df[df.id == id_].iloc[0].phone)

            if st.button("Update Patient"):
                update_patient(id_, name, age, gender, phone)
                st.success("Updated!")
                st.rerun()

            if st.button("Delete Patient"):
                delete_record("patients", id_)
                st.error("Deleted!")
                st.rerun()

    if tab == "Doctors":
        df = fetch_doctors()
        st.dataframe(df)

        id_ = st.number_input("Enter Doctor ID to Edit/Delete", 1)
        if id_ in df["id"].values:
            name = st.text_input("Name", df[df.id == id_].iloc[0].name)
            specialization = st.text_input("Specialization", df[df.id == id_].iloc[0].specialization)

            if st.button("Update Doctor"):
                update_doctor(id_, name, specialization)
                st.success("Updated!")
                st.rerun()

            if st.button("Delete Doctor"):
                delete_record("doctors", id_)
                st.error("Deleted!")
                st.rerun()

    if tab == "Appointments":
        df = fetch_appointments()
        st.dataframe(df)

        id_ = st.number_input("Enter Appointment ID to Edit/Delete", 1)
        if id_ in df["id"].values:
            patients = fetch_patients()
            doctors = fetch_doctors()

            patient_sel = st.selectbox("Patient", patients['name'])
            doctor_sel = st.selectbox("Doctor", doctors['name'])

            patient_id = int(patients[patients['name'] == patient_sel].id.values[0])
            doctor_id = int(doctors[doctors['name'] == doctor_sel].id.values[0])

            date_edit = st.date_input("Date")
            time_edit = st.time_input("Time")
            note = st.text_area("Note")

            if st.button("Update Appointment"):
                update_appointment(id_, patient_id, doctor_id, date_edit, time_edit, note)
                st.success("Updated!")
                st.rerun()

            if st.button("Delete Appointment"):
                delete_record("appointments", id_)
                st.error("Deleted!")
                st.rerun()

# ---------------- EXPORT ALL IN ONE EXCEL ----------------
if choice == "Export to Excel":
    st.header("📤 Export Complete Database")

    patients = fetch_patients()
    doctors = fetch_doctors()
    appointments = fetch_appointments()

    def create_excel():
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        patients.to_excel(writer, sheet_name='Patients', index=False)
        doctors.to_excel(writer, sheet_name='Doctors', index=False)
        appointments.to_excel(writer, sheet_name='Appointments', index=False)
        writer.close()
        return output.getvalue()

    st.download_button(
        label="📥 Download Full Database (Excel)",
        data=create_excel(),
        file_name="clinic_database.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


