import sqlite3
import csv
import time

conn = sqlite3.connect('project.db')
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS data')

cursor.execute("""
CREATE TABLE IF NOT EXISTS data (
    timestamp TEXT NOT NULL,
    value REAL NOT NULL,
    PRIMARY KEY (timestamp, value) 
)
""")

# Insert data from CSV
with open("dummy_data100k.csv", mode="r") as file:
    reader = csv.DictReader(file)
    # Measure insertion time
    start_time = time.time()  # Start the timer
    for row in reader:
        cursor.execute("INSERT INTO data (timestamp, value) VALUES (?, ?)", (row["timestamp"], row["value"]))

end_time = time.time()  # Stop the timer
conn.commit()  # Commit changes to the database
print(f"\nSQL: Added 100 000 entries in {end_time - start_time} seconds.\n")


# start = datetime(2024, 1, 1, 0, 0, 0)
# end = datetime(2025, 1, 1, 0, 15, 0)
start = "2024-01-01T00:00:00"
end = "2025-01-01T00:15:00"

s = time.time()
cursor.execute("SELECT * FROM data WHERE timestamp BETWEEN ? AND ?", (start,end))
results = cursor.fetchall()
e = time.time()
print(f"SQL: Found {len(results)} entries from [{start}] to [{end}] in {e - s:.6f} seconds.\n")

test = "2024-01-01T00:48:20"
s = time.perf_counter()
cursor.execute("SELECT value FROM data WHERE timestamp = ?", (test,))
result = cursor.fetchall()
e = time.perf_counter()
print(f"SQL: Found value: [{result[0][0]}] for timestamp: [{test}] in {e - s} seconds.")



