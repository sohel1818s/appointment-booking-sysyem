select * from patients;

SELECT COUNT(*) AS total_patients FROM patients;

SELECT COUNT(*) 
FROM patients p
LEFT JOIN appointments a ON p.id = a.patient_id
WHERE a.id IS NULL;

SELECT gender, COUNT(*) 
FROM patients
GROUP BY gender;

SELECT patient_id, COUNT(*) AS visits
FROM appointments
GROUP BY patient_id
HAVING visits > 1;

# Average Patient Age
SELECT AVG(age) AS average_age FROM patients;

# The End..