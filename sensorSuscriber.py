# Standard Imports
import time
import paho.mqtt.client as mqtt
from db.connection import add_weatherData

def on_message(client, userdata, message):
    dataArray = str(message.payload.decode("utf-8")).split(",")
    add_weatherData(dataArray[0], dataArray[1], dataArray[2], dataArray[3], dataArray[4], dataArray[5], dataArray[6], dataArray[7], dataArray[8], dataArray[9])

# Set MQTT broker and Topic
broker = "test.mosquitto.org"
pub_topic = "weatheralytics/data"
	
# Connect functions for MQTT
client = mqtt.Client()

# Connect to MQTT 
print("Attempting to connect to broker " + broker)
client.connect(broker)
client.subscribe(pub_topic)
client.on_message = on_message
client.loop_start()

