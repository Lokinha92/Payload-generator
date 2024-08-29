#include <WiFi.h>
#include <WebServer.h>
#include <WebSocketsServer.h>

// Configurações da rede Wi-Fi
const char* ssid = "farinelli";
const char* password = "republica123";

WebServer server(80);
WebSocketsServer webSocket = WebSocketsServer(81);

String valorMensagem = "Nenhum valor recebido ainda.";
String idMensagem = "Nenhum ID recebido ainda.";

// Função para servir a página web
void handleRoot() {
  String ipAddress = WiFi.localIP().toString();
  String html = "<!DOCTYPE html><html><head><title>ESP32 WebSocket Server</title></head>"
                "<body><h1>ESP32 WebSocket Server</h1>"
                "<p>IP do Servidor: " + ipAddress + "</p>"
                "<p id='value'>valorMensagem</p>"
                "<p id='id'>idMensagem</p>"
                "<script>"
                "function updateValue() {"
                "  fetch('/value')"
                "    .then(response => response.text())"
                "    .then(data => {"
                "      document.getElementById('value').innerText = data;"
                "    });"
                "}"
                "function updateID() {"
                "  fetch('/id')"
                "    .then(response => response.text())"
                "    .then(data => {"
                "      document.getElementById('id').innerText = data;"
                "    });"
                "}"
                "setInterval(updateValue, 1000);"
                "setInterval(updateID, 1000);"
                "</script></body></html>";
  server.send(200, "text/html", html);
}

// Função para fornecer o valor atual
void handleValue() {
  server.send(200, "text/plain", valorMensagem);
}

// Função para fornecer o ID atual
void handleID() {
  server.send(200, "text/plain", idMensagem);
}

// Função para tratar eventos do WebSocket
void onWebSocketEvent(uint8_t client_num, WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_TEXT) {
    String msg = String((char *)payload);
    Serial.printf("[%u] Recebido texto: %s\n", client_num, payload);

    if (msg.startsWith("VALOR:")) {
      valorMensagem = msg.substring(6);
      webSocket.sendTXT(client_num, valorMensagem);
    } else if (msg.startsWith("ID:")) {
      idMensagem = msg.substring(3);
      webSocket.sendTXT(client_num, idMensagem);
    }
  }
}

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  Serial.print("Conectando à rede Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi conectado.");

  // Exibir IP do ESP32 no Monitor Serial
  Serial.print("IP do Servidor: ");
  Serial.println(WiFi.localIP());

  server.on("/", handleRoot);
  server.on("/value", handleValue);  // Adiciona o endpoint para o valor
  server.on("/id", handleID);  // Adiciona o endpoint para o ID
  server.begin();
  Serial.println("Servidor HTTP iniciado.");

  webSocket.begin();
  webSocket.onEvent(onWebSocketEvent);
  Serial.println("Servidor WebSocket iniciado.");
}

void loop() {
  server.handleClient();
  webSocket.loop();
}
