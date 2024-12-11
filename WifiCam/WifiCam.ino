#include <WebServer.h>
#include <WiFi.h>
#include <esp32cam.h>

const char* WIFI_SSID = "RedmiNote7";
const char* WIFI_PASS = "12345678";

WebServer server(80);

// Camera resolutions
static auto loRes = esp32cam::Resolution::find(320, 240);
static auto midRes = esp32cam::Resolution::find(350, 530);
static auto hiRes = esp32cam::Resolution::find(800, 600);

// Initialize the camera
void startCamera() {
  using namespace esp32cam;
  Config cfg;
  cfg.setPins(pins::AiThinker);
  cfg.setResolution(hiRes);
  cfg.setBufferCount(2);
  cfg.setJpeg(80);

  if (!Camera.begin(cfg)) {
    Serial.println("Failed to start the camera");
    while (true); // Halt if camera fails
  }
  Serial.println("Camera initialized");
}

// Serve a static JPEG image
void serveJpg() {
  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("Capture failed");
    server.send(503, "text/plain", "Capture failed");
    return;
  }

  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client);
}

// Handlers for static image endpoints
void handleJpgLo() {
  if (!esp32cam::Camera.changeResolution(loRes)) {
    Serial.println("Low resolution set failed");
    server.send(500, "text/plain", "Resolution change failed");
    return;
  }
  serveJpg();
}

void handleJpgMid() {
  if (!esp32cam::Camera.changeResolution(midRes)) {
    Serial.println("Mid resolution set failed");
    server.send(500, "text/plain", "Resolution change failed");
    return;
  }
  serveJpg();
}

void handleJpgHi() {
  if (!esp32cam::Camera.changeResolution(hiRes)) {
    Serial.println("High resolution set failed");
    server.send(500, "text/plain", "Resolution change failed");
    return;
  }
  serveJpg();
}

// Serve MJPEG stream
void handleMjpegStream() {
  WiFiClient client = server.client();

  // Send HTTP headers
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: multipart/x-mixed-replace; boundary=frame");
  client.println();

  while (client.connected()) {
    auto frame = esp32cam::capture();
    if (!frame) {
      Serial.println("Failed to capture frame");
      break;
    }

    client.print("--frame\r\n");
    client.print("Content-Type: image/jpeg\r\n");
    client.printf("Content-Length: %d\r\n\r\n", frame->size());
    frame->writeTo(client);
    client.print("\r\n");

    delay(100); // ~10 FPS
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println();

  startCamera();

  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Camera Ready! Access it at: http://");
  Serial.println(WiFi.localIP());
  Serial.println("Endpoints:");
  Serial.println("  /cam-lo.jpg - Low-resolution static image");
  Serial.println("  /cam-mid.jpg - Mid-resolution static image");
  Serial.println("  /cam-hi.jpg - High-resolution static image");
  Serial.println("  /mjpeg - MJPEG video stream");

  // Define server endpoints
  server.on("/cam-lo.jpg", handleJpgLo);
  server.on("/cam-mid.jpg", handleJpgMid);
  server.on("/cam-hi.jpg", handleJpgHi);
  server.on("/mjpeg", handleMjpegStream);

  server.begin();
}

void loop() {
  server.handleClient();
}
