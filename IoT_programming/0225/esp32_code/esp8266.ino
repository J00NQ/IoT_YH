#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <DHT.h>

#define DHTTYPE DHT11
#define DHTPIN 4
const char* ssid = "<SSID>";
const char* password = "<PASSWORD>";

ESP8266WebServer server(80);

DHT dht(DHTPIN, DHTTYPE);

float temp, humi;
String webString = "";
unsigned long previousMillis = 0;
const long interval = 2000;

void gettemphumi();
void handleevents(){
  gettemphumi();
  webString = "{\"temperature\": \"" + String(temp) + "=", \"humidity\": \"" + String(humi) + "\"}";

  Serial.println(webString);
  server.send(200, "text/plain", webString);
  yield();
}

void setup(){
  Serial.begin(115200);
  delay(10);
  dht.begin();

  Serial.print("Connecting to ");
  Serial.print(ssid);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println(WiFi.localIP());
  
  server.on("/events", handleevents);
  server.begin();
  Serial.println("HTTP server started");
}

void loop(){
  server.handleClient();
}

void gettemphumi(){
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval){
    previousMillis = currentMillis;
    humi = dht.readHumidity();
    temp = dht.readTemperature();
    if (isnan(humi) || isnan(temp)){
      Serial.println("Failed to read dht sensor");
      return;
    }
  }
}

