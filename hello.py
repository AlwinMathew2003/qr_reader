import cv2
import numpy as np
import requests

# Set up the stream URL of your ESP32-CAM
url = 'http://192.168.43.2:80/'

# Send HTTP GET request to the stream
stream = requests.get(url, stream=True)

# Check if the connection was successful
if stream.status_code != 200:
    print("Failed to connect to stream")
    exit()

# Set up a variable to read the multipart stream
bytes_data = b''

for chunk in stream.iter_content(chunk_size=1024):
    bytes_data += chunk
    # Look for the boundary in the multipart data
    start_idx = bytes_data.find(b'\xff\xd8')  # Start of JPEG frame
    end_idx = bytes_data.find(b'\xff\xd9')    # End of JPEG frame

    if start_idx != -1 and end_idx != -1:
        # Slice out the JPEG frame
        jpg = bytes_data[start_idx:end_idx + 2]
        bytes_data = bytes_data[end_idx + 2:]  # Discard the used bytes

        # Convert the JPEG byte array into an image
        img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

        if img is not None:
            # Show the image using OpenCV
            cv2.imshow("ESP32-CAM Video Stream", img)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

cv2.destroyAllWindows()
