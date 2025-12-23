select * from doctors;
# Total Doctors
SELECT COUNT(*) AS total_doctors FROM doctors;

#Doctor-wise Appointment Count
SELECT d.name, COUNT(a.id) AS total_appointments
FROM doctors d
LEFT JOIN appointments a ON d.id = a.doctor_id
GROUP BY d.id;

# Most Busy Doctor
SELECT d.name, COUNT(a.id) AS visits
FROM doctors d
JOIN appointments a ON d.id = a.doctor_id
GROUP BY d.id
ORDER BY visits DESC
LIMIT 1;

# Doctor-wise Earnings
SELECT d.name, COUNT(a.id) * d.fees AS total_earnings
FROM doctors d
LEFT JOIN appointments a ON d.id = a.doctor_id
GROUP BY d.id;

# Highest Earning Doctor (Top 2)
SELECT d.name, COUNT(a.id) * d.fees AS earnings
FROM doctors d
JOIN appointments a ON d.id = a.doctor_id
GROUP BY d.id
ORDER BY earnings DESC
LIMIT 2;

# Doctor Specialization Count
SELECT specialization, COUNT(*) 
FROM doctors
GROUP BY specialization;




#The End ...
