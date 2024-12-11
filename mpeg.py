import cv2

# Initialize OpenCV's QR Code Detector
qr_detector = cv2.QRCodeDetector()

# Stream URL from the ESP32-CAM (replace <ESP32-CAM-IP> with your ESP32's IP)
stream_url = "http://192.168.43.2:80/mjpeg"
cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    print("Error: Unable to access the video stream.")
    exit()

print("Starting QR Code Detection...")

def contourArea(points):
    """Helper function to calculate the area of the QR code's contour."""
    if points is not None and len(points) >= 4:
        points = points.astype(int)
        return cv2.contourArea(points)
    return 0

while True:
    # Read a frame from the stream
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to read frame from the stream.")
        break

    # Convert frame to grayscale (helps with QR code detection)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect and decode QR code
    qr_data, points, _ = qr_detector.detectAndDecode(gray_frame)

    # If QR Code is detected
    if points is not None and contourArea(points) > 0:
        if qr_data:
            print(f"QR Code Detected: {qr_data}")

        # Draw a polygon around the QR code
        points = points[0]  # Get points as a 2D array
        for i in range(len(points)):
            pt1 = tuple(points[i])
            pt2 = tuple(points[(i + 1) % len(points)])
            cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

    else:
        print("Invalid QR code or no QR code detected.")

    # Display the frame
    cv2.imshow("QR Code Detection", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
