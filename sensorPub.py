# Standard Imports
import time
import paho.mqtt.client as mqtt

# Set MQTT broker and Topic
broker = "test.mosquitto.org"
pub_topic = "weatheralytics/data"


# MQTT Connection related functions
def on_connect(client, userdata, flags, rc):
	if rc==0:
		print("Connection established. Code: "+str(rc))
	else:
		print("Connection failed. Code: " + str(rc))
		
def on_publish(client, userdata, mid):
    print("Published: " + str(mid))
	
def on_disconnect(client, userdata, rc):
	if rc != 0:
		print ("Unexpected disonnection. Code: ", str(rc))
	else:
		print("Disconnected. Code: " + str(rc))
	
def on_log(client, userdata, level, buf):		# Message is in buf
    print("MQTT Log: " + str(buf))

	
############### Sensor section ##################	
def getSensorData():
	"""
    Stub API to collect sensor data and return it to calling function.

    Input: None
    Output: String, comma seperated formatting
    """
	return 0 # Not Implemented, for demonstration purposes only

	
# Connect functions for MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish
client.on_log = on_log

# Connect to MQTT 
print("Attempting to connect to broker " + broker)
client.connect(broker)	# Broker address, port and keepalive (maximum period in seconds allowed between communications with the broker)
client.loop_start()


# Loop to publish sensor data to MQTT topic
while True:
	sensorData = getSensorData()
	client.publish(pub_topic, sensorData)
	time.sleep(2.0)	# Set delay
