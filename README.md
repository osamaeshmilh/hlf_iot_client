
# IoT Sensor Data Logger

This application logs sensor data from a Raspberry Pi and publishes it to an MQTT broker.

## Requirements

- Raspberry Pi
- Sense HAT module
- Python 3
- paho-mqtt Python package

## Usage

1. Install Sense HAT and MQTT Python package

```bash
pip install sense-hat paho-mqtt
```

2. Update the broker_ip and broker_port variables with your MQTT broker details

3. Run the script

```bash
python sensor_data_logger.py
```

4. The script will publish sensor data to the topic "iot/data" every 5 seconds

5. An MQTT client can subscribe to this topic to receive the messages

## Code Overview

- get_sensor_data() captures temperature and humidity from Sense HAT
- on_connect() callback prints status when connected to MQTT broker 
- on_message() callback prints messages received  
- MQTT client instance is configured and connects to broker
- Main loop calls get_sensor_data() and publishes to MQTT

## Message Format

The sensor data is published as a JSON string:

```json
{
  "batchNo": "batchNo",
  "warehouseNo": "warehouseNo", 
  "iotId": "iotId",
  "temperatureSensorId": "temperatureSensorId",
  "humiditySensorId": "humiditySensorId",
  "timestamp": "2023-02-13T12:34:56Z",
  "temperature": "23.5",
  "humidity": "46.2"
}
```

