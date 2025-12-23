select * from prescriptions;

# Total Prescriptions
SELECT COUNT(*) AS total_prescriptions FROM prescriptions;

# Most Prescribed Medicine
SELECT medicines, COUNT(*) AS times
FROM prescriptions
GROUP BY medicines
ORDER BY times DESC
LIMIT 1;

# The End..