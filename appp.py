import streamlit as st
import sqlite3
import pandas as pd
from io import BytesIO
from datetime import datetime, date

# Database file
DB_FILE = "clinic.db"

# --- Database connection ---
def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

# --- Table creation ---
def create_tables():
    conn = get_connection()
    cur = conn.cursor()
    
    # Patients table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            phone TEXT
        )
    """)
    
    # Doctors table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            specialization TEXT,
            qualification TEXT DEFAULT '',
            rating REAL DEFAULT 0,
            about TEXT DEFAULT '',
            fees REAL DEFAULT 0
        )
    """)
    
    # Appointments table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            doctor_id INTEGER,
            date TEXT,
            time TEXT,
            note TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id),
            FOREIGN KEY(doctor_id) REFERENCES doctors(id)
        )
    """)
    
    # Prescriptions table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id INTEGER,
            medicines TEXT,
            advice TEXT,
            FOREIGN KEY(appointment_id) REFERENCES appointments(id)
        )
    """)
    
    conn.commit()
    conn.close()

# Call this first before anything else
create_tables()

# --- Helper functions ---
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

    cur.execute(
        "SELECT id FROM doctors WHERE name=? AND specialization=?",
        (name, specialization)
    )
    row = cur.fetchone()
    if row:
        conn.close()
        return row[0]

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
