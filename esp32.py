import requests

esp32_url = "http://<ESP32-IP>/seat"  # Replace <ESP32-IP> with your ESP32's IP address
headers = {'Content-Type': 'application/json'}
seat_number = 2

payload = {'seat_number': seat_number}
try:
    response = requests.post(esp32_url, json=payload, headers=headers)
    if response.status_code == 200:
        print("Successfully sent data to ESP-32")
    else:
        print(f"Failed to send data to ESP-32: {response.status_code}, {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Connection failed: {e}")
