import paho.mqtt.client as mqtt
from sense_hat import SenseHat
import json
import datetime
import time

# Function to get sensor data
def get_sensor_data():
    sense = SenseHat()
    temp = sense.get_temperature()
    humidity = sense.get_humidity() # assuming you have a humidity sensor as well
    data = {
        'batchNo': 'batchNo',
        'warehouseNo': 'warehouseNo',
        'iotId': 'iotId',
        'temperatureSensorId': 'temperatureSensorId',
        'humiditySensorId': 'humiditySensorId',
        'timestamp': datetime.datetime.now().isoformat(),
        'temperature': str(temp),
        'humidity': str(humidity)
    }
    print("Sensor data: ", data)
    return json.dumps(data)  # Converts the dictionary into a JSON string

# Callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {str(rc)}")
    
# Callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

# Setup MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Set the MQTT broker IP address and port
broker_ip = "149.102.154.14"
broker_port = 1883

print(f"Connecting to broker at {broker_ip}:{broker_port}")
# Connect to the broker
client.username_pw_set("iot", "iot123456")

client.connect(broker_ip, broker_port, 60)

# Start the MQTT client
client.loop_start()

while True:
    print("Getting sensor data")
    # Get the sensor data
    sensor_data = get_sensor_data()

    print("Publishing sensor data to topic iot/data")
    # Publish the sensor data to a topic
    client.publish("iot/data", sensor_data)

    # Sleep for 5 seconds before next iteration
    time.sleep(5)
