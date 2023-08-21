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
global_temp = 0.0
global_humidity = 0.0

sense = SenseHat()


def on_connect(client, flags, rc, properties):
    print("Connected")


def on_disconnect(client, packet, exc=None):
    print("Disconnected")


def on_message(client, topic, payload, qos, properties):
    print(topic, payload)


def ask_exit(*args):
    STOP.set()


async def update_sensor_values():
    global global_temp, global_humidity
    while True:
        global_temp = sense.get_temperature()
        global_humidity = sense.get_humidity()
        await asyncio.sleep(2)


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
    return data


async def send_bulk_data(client, bulk_data):
    print("Publishing bulk data...")
    client.publish("iot/data", json.dumps(bulk_data))


async def main():
    client = MQTTClient("client-id")

    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.set_auth_credentials(USERNAME, PASSWORD)
    await client.connect(BROKER_HOST, BROKER_PORT)

    update_task = asyncio.create_task(update_sensor_values())
    bulk_data = []

    for device_id in range(1, 1001):
        for sensor_id in range(1, 6):
            sensor_data = await get_sensor_data(device_id, sensor_id)
            bulk_data.append(sensor_data)

            if len(bulk_data) == 3000:
                await send_bulk_data(client, bulk_data)
                bulk_data.clear()  # Clear the list for the next set of 3000

    await STOP.wait()
    update_task.cancel()
    await client.disconnect()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
