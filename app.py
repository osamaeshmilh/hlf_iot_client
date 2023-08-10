import paho.mqtt.client as mqtt
from sense_hat import SenseHat
import json
import datetime
import time

# Offline queue to hold messages when disconnected
offline_queue = []

# Function to get sensor data
def get_sensor_data(device_id, sensor_id):
    sense = SenseHat()
    temp = sense.get_temperature()
    humidity = sense.get_humidity()
    data = {
        'batchNo': '101',
        'warehouseNo': '01',
        'iotId': f'{device_id:02}',  # Format it to be 01, 02, 03, ...
        'temperatureSensorId': f'{sensor_id:02}',  # Format it to be 01, 02, 03, ...
        'humiditySensorId': f'{sensor_id:02}',
        'timestamp': datetime.datetime.now().isoformat(),
        'temperature': str(temp),
        'humidity': str(humidity)
    }
    print("Sensor data: ", data)
    return json.dumps(data)

# ... [rest of the callback functions] ...

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

while True:
    for device_id in range(1, 11):  # Looping for 10 devices
        for sensor_id in range(1, 6):  # Looping for 5 sensors for each device
            print(f"Getting sensor data for device {device_id} and sensor {sensor_id}")
            # Get the sensor data
            sensor_data = get_sensor_data(device_id, sensor_id)

            print("Publishing sensor data to topic iot/data")
            # Check if client is connected to the broker
            if client.is_connected():
                # Publish the sensor data to a topic
                client.publish("iot/data", sensor_data)
            else:
                print("Offline. Adding to queue.")
                offline_queue.append(sensor_data)

            # Sleep for 1 seconds before next iteration
            time.sleep(1)
