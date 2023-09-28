import paho.mqtt.client as mqtt
import json
import datetime
import time
from cryptography.fernet import Fernet
import random  # Added for generating random sensor data

# Offline queue to hold messages when disconnected
offline_queue = []

# Function to get sensor data
def get_sensor_data():
    temp = random.uniform(20.0, 30.0)
    humidity = random.uniform(50.0, 70.0)
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
    print("Fake sensor data: ", data)
    return json.dumps(data)  # Converts the dictionary into a JSON string

# Encrypt data using a secret key
def encrypt_data(data, key):
    cipher_suite = Fernet(key)
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data

# Callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    global offline_queue
    print(f"Connected with result code {str(rc)}")
    # Publish any messages that were queued while offline
    for message in offline_queue:
        client.publish("iot/data", message)
    offline_queue = []

# Callback for when the client is disconnected from the server.
def on_disconnect(client, userdata, rc):
    print(f"Disconnected with result code {str(rc)}")

# Callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

# Setup MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
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

# secret key
secret_key = b'ztdoy8Ej58Iq33oPUJFfXS__AHmRG_N2u5IPgwoVJM4='

while True:
    print("Getting sensor data")
    # Get the sensor data
    sensor_data = get_sensor_data()

    print("Encrypting sensor data")
    # Encrypt the sensor data
    encrypted_sensor_data = encrypt_data(sensor_data, secret_key)

    print("Publishing encrypted sensor data to topic iot/data")
    # Check if client is connected to the broker
    if client.is_connected():
        # Publish the encrypted sensor data to a topic
        client.publish("iot/data", encrypted_sensor_data)
    else:
        print("Offline. Adding to queue.")
        offline_queue.append(encrypted_sensor_data)

    # Sleep for 5 seconds before the next iteration
    time.sleep(5)
