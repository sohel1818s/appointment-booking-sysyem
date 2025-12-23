select * from appointments;
# Total Appointments
SELECT COUNT(*) AS total_appointments FROM appointments;



# Appointments Today
SELECT COUNT(*) 
FROM appointments 
WHERE date = CURDATE();






# Appointments Per Day
SELECT date, COUNT(*) AS total
FROM appointments
GROUP BY date;





# Appointments Without Prescription
SELECT COUNT(*) 
FROM appointments a
LEFT JOIN prescriptions p ON a.id = p.appointment_id
WHERE p.id IS NULL;





# Appointments by Doctor Specialization
SELECT d.specialization, COUNT(a.id) AS total
FROM doctors d
JOIN appointments a ON d.id = a.doctor_id
GROUP BY d.specialization;


# Monthly Appointment Count
SELECT MONTH(date) AS December_Month, COUNT(*) 
FROM appointments
GROUP BY MONTH(date);

# Complete Appointment Report
SELECT a.id,p.name AS patient,d.name AS doctor,a.date,a.time,a.note
FROM appointments a
JOIN patients p ON p.id = a.patient_id
JOIN doctors d ON d.id = a.doctor_id;

# The End..