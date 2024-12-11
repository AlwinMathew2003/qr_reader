from flask import Flask, render_template, jsonify, request
import mysql.connector
import cv2
import requests  # Importing 'requests' as a standalone library
import json
import numpy as np
import threading
import urllib.request

app = Flask(__name__)

db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="qrcode_db"
)

cursor = db_connection.cursor()
# Initialize the QR Code detector
detector = cv2.QRCodeDetector()

# Initialize global variable to store QR code data
qr_data = None

# Start capturing video from ESP32-CAM stream URL (or use a webcam for testing)
video_stream_url = 'http://192.168.43.2:80/mjpeg'

# Function to process the video feed and detect QR codes
def detect_qr_code():
    global qr_data
    cv2.namedWindow("QR Code Scanner", cv2.WINDOW_AUTOSIZE)

    # Open the video stream
    cap = cv2.VideoCapture(video_stream_url)

    if not cap.isOpened():
        print("Error: Unable to open video stream.")
        return

    while True:
        try:
            # Read a frame from the video stream
            ret, frame = cap.read()

            if not ret:
                print("Failed to fetch frame from stream")
                continue

            # Detect and decode the QR code
            data, bbox, _ = detector.detectAndDecode(frame)

            # If QR code is detected
            if data:
                qr_data = data
                print(f"QR Code Detected: {data}")
                # Draw the decoded data on the video frame
                cv2.putText(frame, data, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Display the frame with bounding box if QR code is detected
            if bbox is not None:
                bbox = np.int32(bbox)  # Convert coordinates to integers
                for i in range(len(bbox[0])):
                    # Draw lines around the QR code
                    pt1 = tuple(bbox[0][i])
                    pt2 = tuple(bbox[0][(i + 1) % len(bbox[0])])
                    cv2.line(frame, pt1, pt2, (255, 0, 0), 2)

            # Show the video frame
            cv2.imshow("QR Code Scanner", frame)

            # Exit on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except Exception as e:
            print(f"Error: {e}")
            break

    cap.release()
    cv2.destroyAllWindows()

# Route to get QR code data
@app.route('/get_qr_data')
def get_qr_data():
    global qr_data
    print("I Reached Here")
    # Parse the qr_data JSON string to get the ID
    try:
        qr_data_json = json.loads(qr_data)  # Parse the JSON string into a Python dictionary
        qr_id = qr_data_json.get('id')  # Extract the 'id' field from the JSON object
        print(qr_id,"I am parsed to dictionary")
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid QR data format'}), 400

    if not qr_id:
        return jsonify({'error': 'ID not found in QR data'}), 400
    
    # Query the database to check if the ID exists
    print(f"qr_id value: {qr_id}")
    query = "SELECT * FROM passengers WHERE id = %s"
    cursor.execute(query, (qr_id,))
    user = cursor.fetchone()  # Fetch one matching row
    print(user)

    if user:
                # Format user data as a dictionary
        user_data = {
            'id': user[0],  # Assuming 'user' tuple columns
            'name': user[1],
            'start_location':user[2],
            'destination':user[3],
            'seat_number': user[4]
            # Add other fields as needed
        }
        # If the user exists, return the data
        seat_number = user[4]
        print("Successfully Fetched!")
        # Send only the seat_number to the ESP32
        esp32_url = "http://<ESP32-IP>/receive_data"
        headers = {'Content-Type': 'application/json'}

        # Send the seat_number to ESP32
        try:
            payload = {'seat_number': seat_number}  # Only send the seat_number
            response = requests.post(esp32_url, json=payload, headers=headers)
            if response.status_code == 200:
                print("Successfully send data to ESP-32")
            else:
                print("Failed to send data to ESP-32")
        except requests.exceptions.RequestException as e:
            print("Failed in establishing connection")
        return jsonify({'user':user_data}), 200
    else:
        # If the user is not found, return an error message
        return jsonify({'error': 'QR code ID not found in the database'}), 404

@app.route('/')
def hello_world():
    return render_template('index.html')

# def hai():
#     return "Hai I am inside add_url_rule"

# app.add_url_rule('/','hello',hai)

if __name__=='__main__':
    thread = threading.Thread(target=detect_qr_code)
    thread.daemon = True
    thread.start()
    app.run(host='0.0.0.0', port=5000)