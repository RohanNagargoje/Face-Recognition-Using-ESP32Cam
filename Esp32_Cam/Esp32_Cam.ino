#include <WebServer.h>
#include <WiFi.h>
#include <esp32cam.h>

const char* WIFI_SSID = "your-SSID"; //your Wi-Fi name 
const char* WIFI_PASS = "your-PASSWORD"; //your Wi-Fi password 

// Initialize web server on port 80
WebServer server(80);

// Resolution settings for low, medium, and high
static auto loRes = esp32cam::Resolution::find(320, 240);
static auto midRes = esp32cam::Resolution::find(640, 480);
static auto hiRes = esp32cam::Resolution::find(800, 600);

// Function to serve captured image over HTTP
void serveJpg() {
  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("Capture failed!");
    server.send(503, "text/plain", "Capture Failed");
    return;
  }

  // Print image details for debugging
  Serial.printf("Captured Image: %dx%d, %d bytes\n", frame->getWidth(), frame->getHeight(), frame->size());

  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client); // Send the image data
}

// Generic handler to change resolution and serve image
void handleJpg(const esp32cam::Resolution& res) {
  if (!esp32cam::Camera.changeResolution(res)) {
    Serial.printf("Resolution change failed: %dx%d\n", res.width(), res.height());
    server.send(503, "text/plain", "Resolution Change Failed");
    return;
  }
  serveJpg();
}

// Setup function
void setup() {
  // Start Serial communication
  Serial.begin(115200);
  Serial.println();

  // Camera configuration
  using namespace esp32cam;
  Config cfg;
  cfg.setPins(pins::AiThinker);  // Using AiThinker board configuration
  cfg.setResolution(hiRes);      // Set initial resolution to high
  cfg.setBufferCount(2);         // Set buffer count to 2 for better performance
  cfg.setJpeg(80);               // Set JPEG quality

  // Initialize the camera
  bool cameraStatus = Camera.begin(cfg);
  Serial.println(cameraStatus ? "Camera initialized successfully!" : "Camera initialization failed!");

  // Set up Wi-Fi connection
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  // Retry Wi-Fi connection if not connected within 10 seconds
  int retryCount = 0;
  while (WiFi.status() != WL_CONNECTED && retryCount < 20) {
    delay(500);
    Serial.print(".");
    retryCount++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("Connected to Wi-Fi. IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Failed to connect to Wi-Fi.");
  }

  // Setup routes for different resolutions with custom names
  server.on("/low-res.jpg", []() { handleJpg(loRes); });
  server.on("/medium-res.jpg", []() { handleJpg(midRes); });
  server.on("/high-res.jpg", []() { handleJpg(hiRes); });

  // Start the web server
  server.begin();
  Serial.println("Server started.");
}

// Loop function to handle incoming client requests
void loop() {
  server.handleClient();
}
