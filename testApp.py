import asyncio
from gmqtt import Client as MQTTClient
from sense_hat import SenseHat
import json
import datetime

BROKER_HOST = "149.102.154.14"
BROKER_PORT = 1883
USERNAME = "iot"
PASSWORD = "iot123456"

STOP = asyncio.Event()

# Global variables for temperature and humidity
global_temp = None
global_humidity = None

sense = SenseHat()  # Initialize it once instead of multiple times

def on_connect(client, flags, rc, properties):
    print("Connected")

def on_disconnect(client, packet, exc=None):
    print("Disconnected")

def on_message(client, topic, payload, qos, properties):
    print(topic, payload)

def ask_exit(*args):
    STOP.set()

# Asynchronous function to update temperature and humidity every two seconds
async def update_sensor_values():
    global global_temp, global_humidity
    while True:
        global_temp = sense.get_temperature()
        global_humidity = sense.get_humidity()
        await asyncio.sleep(2)

# Function to get sensor data
async def get_sensor_data(device_id, sensor_id):
    data = {
        'batchNo': '101',
        'warehouseNo': '01',
        'iotId': f'{device_id:02}',
        'temperatureSensorId': f'{sensor_id:02}',
        'humiditySensorId': f'{sensor_id:02}',
        'timestamp': datetime.datetime.now().isoformat(),
        'temperature': str(global_temp),
        'humidity': str(global_humidity)
    }
    return json.dumps(data)

async def send_data(device_id, sensor_id, client):
    while True:
        sensor_data = await get_sensor_data(device_id, sensor_id)
        print(f"Publishing data from device {device_id} and sensor {sensor_id}")
        client.publish("iot/data", sensor_data)
        await asyncio.sleep(1)

async def main():
    client = MQTTClient("client-id")

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.set_auth_credentials(USERNAME, PASSWORD)
    await client.connect(BROKER_HOST, BROKER_PORT)

    # Start the sensor value update task
    update_task = asyncio.create_task(update_sensor_values())

    tasks = [update_task]
    for device_id in range(1, 11):
        for sensor_id in range(1, 7):
            task = asyncio.create_task(send_data(device_id, sensor_id, client))
            tasks.append(task)

    await STOP.wait()
    for task in tasks:
        task.cancel()
    await client.disconnect()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
