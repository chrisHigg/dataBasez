from flask import Flask, request, jsonify
from datetime import datetime
from newbplustreeIter2 import BPlusTree
import time
import csv


bplustree = BPlusTree(order=100)
app = Flask(__name__)

@app.route('/insert', methods=['POST'])
def insert():
    try:
        # Get data from the request
        data = request.json
        timestamp = datetime.fromisoformat(data['time'])
        value = data['value']

        # Insert into the B+-tree
        s = time.perf_counter()
        bplustree.insert(timestamp, value)
        e = time.perf_counter()
        return jsonify({'message': f'Data inserted successfully in {e - s} seconds'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/query_exact', methods=['GET'])
def query_exact():
    try:
        # Get the time from the request arguments
        time_str = request.args.get('time')
        timestamp = datetime.fromisoformat(time_str)

        # Measure performance
        s = time.perf_counter()
        # Perform exact lookup in the B+-tree
        value = bplustree.retrieve(timestamp)
        e = time.perf_counter()
        print(f"Exact query operation elapsed time: {e - s} seconds")

        if value is not None:
            return jsonify({'value': value, 'elapsed_time': e - s}), 200
        else:
            return jsonify({'message': 'No data found for the given time', 'elapsed_time': e - s}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/query_range', methods=['GET'])
def query_range():
    try:
        # Get start and end times from the request arguments
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')
        start_timestamp = datetime.fromisoformat(start_time_str)
        end_timestamp = datetime.fromisoformat(end_time_str)

        # Measure performance
        s = time.perf_counter()
        # Use the custom range query function of your B+ tree
        result = bplustree.range_query(start_timestamp, end_timestamp)
        e = time.perf_counter()

        if result is not None:
            for r in result:
                formatted_result = [{'value': r} for r in result]
                # Add elapsed time to the response
                formatted_result.append({'elapsed_time': e - s})
                return jsonify(formatted_result), 200
        else:
            return jsonify({'message': 'No data found for the given time', 'elapsed_time': e - s}), 404

        print(f"Formatted result: {formatted_result}")

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/query_range_sum', methods=['GET'])
def query_range_sum():
    try:
        # Get start and end times from the request arguments
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')
        start_timestamp = datetime.fromisoformat(start_time_str)
        end_timestamp = datetime.fromisoformat(end_time_str)

        # Measure performance
        s = time.perf_counter()
        # Use the custom range query function of your B+ tree
        result = bplustree.range_sum(start_timestamp, end_timestamp)
        e = time.perf_counter()

        if result is not None:
            return jsonify({'value': result, 'elapsed_time': e - s}), 200
        else:
            return jsonify({'message': 'No data found for the given time', 'elapsed_time': e - s}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/query_range_avg', methods=['GET'])
def query_range_avg():
    try:
        # Get start and end times from the request arguments
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')
        start_timestamp = datetime.fromisoformat(start_time_str)
        end_timestamp = datetime.fromisoformat(end_time_str)

        # Measure performance
        s = time.perf_counter()
        # Use the custom range query function of your B+ tree
        result = bplustree.range_avg(start_timestamp, end_timestamp)
        e = time.perf_counter()

        if result is not None:
            return jsonify({'value': result, 'elapsed_time': e - s}), 200
        else:
            return jsonify({'message': 'No data found for the given time', 'elapsed_time': e - s}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/query_range_min', methods=['GET'])
def query_range_min():
    try:
        # Get start and end times from the request arguments
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')
        start_timestamp = datetime.fromisoformat(start_time_str)
        end_timestamp = datetime.fromisoformat(end_time_str)

        # Measure performance
        s = time.perf_counter()
        # Use the custom range query function of your B+ tree
        result = bplustree.range_min(start_timestamp, end_timestamp)
        e = time.perf_counter()

        if result is not None:
            return jsonify({'value': result, 'elapsed_time': e - s}), 200
        else:
            return jsonify({'message': 'No data found for the given time', 'elapsed_time': e - s}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/query_range_max', methods=['GET'])
def query_range_max():
    try:
        # Get start and end times from the request arguments
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')
        start_timestamp = datetime.fromisoformat(start_time_str)
        end_timestamp = datetime.fromisoformat(end_time_str)

        # Measure performance
        s = time.perf_counter()
        # Use the custom range query function of your B+ tree
        result = bplustree.range_max(start_timestamp, end_timestamp)
        e = time.perf_counter()

        if result is not None:
            return jsonify({'value': result, 'elapsed_time': e - s}), 200
        else:
            return jsonify({'message': 'No data found for the given time', 'elapsed_time': e - s}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400




@app.route('/insert_bulk', methods=['POST'])
def insert_bulk():
    try:
        csv_file = "dummy_data.csv"

        with open(csv_file, mode="r") as file:
            reader = csv.DictReader(file)
            s = time.time()  # Start timing
            for row in reader:
                time_key = datetime.fromisoformat(row["timestamp"])
                temperature = float(row["value"])
                bplustree.insert(time_key, temperature)
            e = time.time()  # End timing
        #print(f"Added 10000 Entries to B+ Tree: \n - Elapsed time: {e2 - s2} seconds")
        return jsonify({'message': f'Added 100 000 entries successfully in {e - s} seconds'}), 201

    except Exception as e:

        return jsonify({'error': str(e)}), 400



if __name__ == '__main__':
    app.run(debug=True)

# How to use the API commands:
#
# 1. Insert Data (Single Entry):
#    - Endpoint: /insert
#    - Method: POST
#    - Payload: {"time": "2024-01-01T12:00:00", "value": 50}
#    - Description: Insert a single timestamp-value pair into the B+ tree.
#    - CURL Command:
#      curl -X POST http://127.0.0.1:5000/insert -H "Content-Type: application/json" -d "{\"time\": \"2024-01-01T12:00:00\", \"value\": 50}"
#
# 2. Insert Data in Bulk:
#    - Endpoint: /insert_bulk
#    - Method: POST
#    - Description: Insert multiple entries from a CSV file (assumes file named 'time_series_data100k.csv' is available).
#    - CURL Command:
#      curl -X POST http://127.0.0.1:5000/insert_bulk
#
# 3. Exact Query:
#    - Endpoint: /query_exact
#    - Method: GET
#    - Query Parameter: time=<ISO 8601 formatted time string>
#    - Example: /query_exact?time=2024-01-01T12:00:00
#    - Description: Retrieve the value for a specific timestamp from the B+ tree.
#    - CURL Command:
#      curl -X GET "http://127.0.0.1:5000/query_exact?time=2024-01-01T12:00:00"
#
# 4. Range Query:
#    - Endpoint: /query_range
#    - Method: GET
#    - Query Parameters: start_time=<ISO 8601 formatted time string>, end_time=<ISO 8601 formatted time string>
#    - Example: /query_range?start_time=2024-01-01T12:00:00&end_time=2024-01-02T12:00:00
#    - Description: Retrieve all entries between the specified start and end timestamps from the B+ tree.
#    - CURL Command:
#      curl -X GET "http://127.0.0.1:5000/query_range?start_time=2024-01-01T12:00:00&end_time=2024-01-02T12:00:00"
