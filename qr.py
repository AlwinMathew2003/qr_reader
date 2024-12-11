import cv2
import urllib.request
import numpy as np

# Replace with your ESP32-CAM's IP address and endpoint
video_stream_url = 'http://192.168.43.2/cam-hi.jpg'

# Initialize the QR Code Detector
detector = cv2.QRCodeDetector()

# Function to process the video feed and detect QR codes
def detect_qr_code():
    global qr_data
    cv2.namedWindow("QR Code Scanner", cv2.WINDOW_AUTOSIZE)

    while True:
        try:
            # Fetch the static image from the ESP32-CAM
            img_resp = urllib.request.urlopen(video_stream_url)
            img_np = np.array(bytearray(img_resp.read()), dtype=np.uint8)

            # Decode the image to OpenCV format
            frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

            if frame is None:
                print("Failed to decode image from stream")
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

    cv2.destroyAllWindows()

# Call the function to start detection
detect_qr_code()
