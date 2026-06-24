#include <WiFi.h>
#include <ETH.h>
#include <PubSubClient.h>

const char* mqtt_server = "10.10.3.56";

const int INPUT_PIN = 5;
const int FAULT_PIN = 15;

WiFiClient espClient;
PubSubClient client(espClient);

bool previousState = HIGH;
unsigned long pieces = 0;
unsigned long lastPulse = 0;
bool previousFaultState = HIGH;

void reconnectMQTT()
{
    while (!client.connected())
    {
        Serial.println("Connecting MQTT...");

        if (client.connect("ZM34"))
        {
            Serial.println("MQTT connected");
        }
        else
        {
            Serial.print("Failed, rc=");
            Serial.println(client.state());
            delay(2000);
        }
    }
}

void publishPiece()
{
    String payload =
        "{\"machine\":\"ZM34\",\"event\":\"piece\"}";

    client.publish(
        "factory/ZM34/status",
        payload.c_str()
    );

    Serial.println(payload);
}

void publishFault(bool fault)
{
    String payload =
        "{\"machine\":\"ZM34\","
        "\"event\":\"fault\","
        "\"state\":" + String(fault ? 1 : 0) +
        "}";

    client.publish(
        "factory/ZM34/status",
        payload.c_str()
    );

    Serial.println(payload);
}

void setup()
{
    Serial.begin(115200);

    pinMode(INPUT_PIN, INPUT_PULLUP);
    pinMode(FAULT_PIN, INPUT_PULLUP);

    Serial.println("Starting Ethernet...");

    ETH.begin();

    while (!ETH.linkUp())
    {
        delay(100);
    }

    Serial.println("Ethernet connected");
    Serial.print("IP: ");
    Serial.println(ETH.localIP());

    client.setServer(mqtt_server, 1883);

    reconnectMQTT();

    Serial.println("MES Ready");
}

void loop()
{
    if (!client.connected())
    {
        reconnectMQTT();
    }

    client.loop();

    bool currentFaultState = digitalRead(FAULT_PIN);

    if (currentFaultState != previousFaultState)
    {
        bool fault = (currentFaultState == LOW);

        publishFault(fault);

        previousFaultState = currentFaultState;
    }

    bool currentState = digitalRead(INPUT_PIN);

    if (currentState == LOW &&
        previousState == HIGH &&
        millis() - lastPulse > 50)
    {
        lastPulse = millis();

        pieces++;

        Serial.print("PIECE ");
        Serial.println(pieces);

        publishPiece();
    }

    previousState = currentState;
}