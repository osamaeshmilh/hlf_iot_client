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

def on_connect(client, flags, rc, properties):
    print("Connected")

def on_disconnect(client, packet, exc=None):
    print("Disconnected")

def on_message(client, topic, payload, qos, properties):
    print(topic, payload)

def ask_exit(*args):
    STOP.set()

# Function to get sensor data
async def get_sensor_data(device_id, sensor_id):
    sense = SenseHat()
    temp = sense.get_temperature()
    humidity = sense.get_humidity()
    data = {
        'batchNo': '101',
        'warehouseNo': '01',
        'iotId': f'{device_id:02}',
        'temperatureSensorId': f'{sensor_id:02}',
        'humiditySensorId': f'{sensor_id:02}',
        'timestamp': datetime.datetime.now().isoformat(),
        'temperature': str(temp),
        'humidity': str(humidity)
    }
    return json.dumps(data)

async def send_data(device_id, sensor_id, client):
    while True:
        sensor_data = await get_sensor_data(device_id, sensor_id)
        print(f"Publishing data from device {device_id} and sensor {sensor_id}")
        client.publish("iot/data", sensor_data)
        await asyncio.sleep(5)

async def main():
    client = MQTTClient("client-id")

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.set_auth_credentials(USERNAME, PASSWORD)
    await client.connect(BROKER_HOST, BROKER_PORT)

    tasks = []
    for device_id in range(1, 11):
        for sensor_id in range(1, 2):
            task = asyncio.create_task(send_data(device_id, sensor_id, client))
            tasks.append(task)

    await STOP.wait()
    for task in tasks:
        task.cancel()
    await client.disconnect()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
