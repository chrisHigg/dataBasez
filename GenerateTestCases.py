import csv
import random
from datetime import datetime, timedelta

def generate_dummy_data(filename, num_entries=1000000):
    start_date = datetime(2024, 1, 1)
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "value"])  # Write column names
        current_timestamp = start_date
        for _ in range(num_entries):
            current_timestamp += timedelta(seconds=random.randint(1, 3600))  # Increment timestamp by 1 to 3600 seconds
            value = random.randint(0, 100)  # Random value between 0 and 100
            writer.writerow([current_timestamp.strftime("%Y-%m-%dT%H:%M:%S"), value])

if __name__ == "__main__":
    generate_dummy_data("dummy_data1M.csv")
