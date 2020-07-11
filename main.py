from MQ2 import MQ2
from network import WLAN 
from umqtt.simple import MQTTClient
import wifimgr
import machine
import utime
import ujson

pin = machine.Pin(34) 

sensor = MQ2(pinData = pin)

print("Calibrating")
sensor.calibrate()
print("Calibration completed")
print("Base resistance:{0}".format(sensor._ro))

while True:
	# WiFi setup
	wlan = wifimgr.get_connection()

	if wlan is None:
		print("Could not initialize the network connection.")
		while True:
			pass  # you shall not pass :D

	# Read Sensor data
	smokeValue = sensor.readSmoke()
	lpgValue = sensor.readLPG()
	methaneValue = sensor.readMethane()
	hydrogenValue = sensor.readHydrogen()

	# MQTT Message
	message = {}

	message["smoke"] = smokeValue
 	message["lpg"] = lpgValue
	message["methane"] = methaneValue
	message["hydrogen"] = hydrogenValue

	print(message)

	# Publish message to MQTT
	topic = "kitchen/mq2"

	client = MQTTClient("hassio.local", topic, user="mqtt", password="hassio", port=1883) 

	client.Connect()

	data = ujson.dumps(message)
	
	client.publish(topic=topic, msg=data)

	# Wait
	utime.sleep(60)
