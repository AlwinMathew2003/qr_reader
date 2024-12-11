#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "YourWiFiSSID";
const char* password = "YourWiFiPassword";

// Initialize the web server on port 80
WebServer server(80);

// Define LED pins
const int ledPins[] = {
  2, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33
}; // Maximum GPIO pins suitable for LEDs
const int ledCount = sizeof(ledPins) / sizeof(ledPins[0]);

// Function to handle POST requests
void handleSeatRequest() {
  if (server.method() == HTTP_POST) {
    StaticJsonDocument<200> jsonDoc;
    DeserializationError error = deserializeJson(jsonDoc, server.arg("plain"));
    if (error) {
      server.send(400, "application/json", "{\"error\":\"Invalid JSON\"}");
      return;
    }

    int seatNumber = jsonDoc["seat_number"];
    if (seatNumber >= 1) {
      for (int i = 0; i < ledCount; i++) {
        digitalWrite(ledPins[i], LOW); // Turn off all LEDs first
      }
      digitalWrite(ledPins[seatNumber], HIGH); // Turn on the selected LED
      server.send(200, "application/json", "{\"message\":\"LED turned on\"}");
    } else {
      server.send(400, "application/json", "{\"error\":\"Invalid seat number\"}");
    }
  } else {
    server.send(405, "application/json", "{\"error\":\"Method not allowed\"}");
  }
}

void setup() {
  // Initialize serial communication
  Serial.begin(115200);

  // Configure LED pins as OUTPUT
  for (int i = 0; i < ledCount; i++) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW); // Ensure LEDs are initially off
  }

  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.println(WiFi.localIP());

  // Set up the route for handling POST requests
  server.on("/seat", HTTP_POST, handleSeatRequest);

  // Start the server
  server.begin();
  Serial.println("Web server started");
}

void loop() {
  server.handleClient(); // Handle incoming client requests
}
