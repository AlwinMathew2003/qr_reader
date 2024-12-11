import cv2
import urllib.request
import numpy as np

# Replace with your ESP32-CAM's IP address and endpoint
url = 'http://192.168.43.2/cam-mid.jpg'  # Ensure this URL serves static images

cv2.namedWindow("Live Cam Testing", cv2.WINDOW_AUTOSIZE)

while True:
    try:
        # Fetch the static image from the ESP32-CAM
        img_resp = urllib.request.urlopen(url)
        img_np = np.array(bytearray(img_resp.read()), dtype=np.uint8)

        # Decode the image to OpenCV format
        frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

        if frame is None:
            print("Failed to decode image from stream")
            continue

        # Display the frame as a video
        cv2.imshow("Live Cam Testing", frame)

        # Exit the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except Exception as e:
        print(f"Error: {e}")
        break

cv2.destroyAllWindows()
