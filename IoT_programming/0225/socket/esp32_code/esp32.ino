#include <WiFi.h>
#include <WiFiMulti.h> // #include <ESP8266WiFiMulti.h>
#include <SocketIoClient.h>
#include <DHT.h>

#define DHTTYPE DHT11
#define DHTPIN 4

WiFiMulti WiFiMulti;
SocketIoClient webSocket;

const char* ssid = "5Ãþ";
const char* password = "48864886";
const char *serverIp = "192.168.0.54";
const int port = 5000;

DHT dht(DHTPIN, DHTTYPE);

float temp, humi;
String webString = "";
char ch[52] = {0};
unsigned long previousMillis = 0;
const long interval = 5000;
const int led = 2;
int ledstate = 0;

void handleconnect(const char * payload, size_t length){
  Serial.printf("Connecter to websocket\n");
  webSocket.emit("join_dev", "{\"room\": \"DEV\"}");
  delay(1000);
}

void handleled(const char * payload, size_t length){
  ledstate = !ledstate;
  digitalWrite(led, ledstate);
  Serial.print("led"); Serial.println(ledstate);
}

void gettemphumi();

void handleevents(){
  gettemphumi();
  webString="{\"temperature\": \"" + String(temp) + "\", \"humidity\": \"" + String(humi) + "\"}";
  webString.toCharArray(ch, webString.length()+1);
  Serial.println(ch);
  webSocket.emit("events", ch);
  yield();
}

void setup(){
  pinMode(led, OUTPUT);
  digitalWrite(led, 0);
  Serial.begin(115200);
  delay(10);
  dht.begin();

  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFiMulti.addAP(ssid, password);

  while (WiFiMulti.run() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi Connected");
  Serial.println(WiFi.localIP());

  webSocket.on("connect", handleconnect);
  webSocket.on("led_control", handleled);
  webSocket.begin(serverIp, port);
}

void loop(){
  webSocket.loop();
  
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval){
    previousMillis = currentMillis;
    handleevents();
  }
  delay(1000);
}

void gettemphumi(){
  humi = dht.readHumidity();
  temp = dht.readTemperature();
  if (isnan(humi) || isnan(temp)){
    Serial.println("Failed to read dht sensor");
    return;
  }
}

