from __future__ import annotations
from math import ceil, floor
from datetime import datetime
import time
import csv
from newbplustreeIter2 import BPlusTree

bplustree = BPlusTree(order=10)

csv_file = "dummy_data1M.csv"  # Ensure this file exists and matches your schema

with open(csv_file, mode="r") as file:
    reader = csv.DictReader(file)
    start_time = time.time()  # Start timing
    for row in reader:
        time_key = datetime.fromisoformat(row["timestamp"])
        temperature = float(row["value"])
        bplustree.insert(time_key, temperature)
    end_time = time.time()  # End timing

print(f"\nB+: Added 1 000 000 entries in {end_time - start_time} seconds.\n")

# start = datetime(2024, 1, 1, 0, 0, 0)
# end = datetime(2025, 1, 1, 0, 15, 0)

start = "2024-01-01T00:00:00"
end = "2025-01-01T00:15:00"
test1 = datetime.fromisoformat(start)
test2 = datetime.fromisoformat(end)



s4 = time.perf_counter()
range_results2 = bplustree.range_query(test1, test2)
e4 = time.perf_counter()
print(f"B+: Found {len(range_results2)} entries from [{test1}] to [{test2}] in {e4 - s4:.6f} seconds. \n")

#test = datetime(2024, 1, 1, 00, 49, 42)
date = "2024-01-01T00:18:47"
test = datetime.fromisoformat(date)

s5 = time.perf_counter()
results3 = bplustree.retrieve(test)
e5 = time.perf_counter()
print(f"B+: Found value: {results3} for timestamp: [{test}] in {e5 - s5} seconds")

print("\nAggregate Functions: \n")

# ################# AGGREGATE FUNCTIONS ###################
#
# s6 = time.perf_counter()
# sum = bplustree.range_sum(test1, test2)
# e6 = time.perf_counter()
# print(f"B+: Found sum {sum} of values from [{test1}] to [{test2}] in {e4 - s4:.6f} seconds. \n")
#
# s7 = time.perf_counter()
# avg = bplustree.range_avg(test1, test2)
# e7 = time.perf_counter()
# print(f"B+: Found Avg: {avg} value from [{test1}] to [{test2}] in {e4 - s4:.6f} seconds. \n")
#
# s8 = time.perf_counter()
# min = bplustree.range_min(test1, test2)
# e8 = time.perf_counter()
# print(f"B+: Found Min: {min} value from [{test1}] to [{test2}] in {e4 - s4:.6f} seconds. \n")
#
# s9 = time.perf_counter()
# max = bplustree.range_max(test1, test2)
# e9 = time.perf_counter()
# print(f"B+: Found Max: {max} value from [{test1}] to [{test2}] in {e4 - s4:.6f} seconds. \n")





