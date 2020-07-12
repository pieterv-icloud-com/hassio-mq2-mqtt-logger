from MQ2 import MQ2
from network import WLAN 
from umqtt.simple import MQTTClient
import wifimgr
import machine
import utime
import ujson
import sys

# MQ2 Sensor Analog Pin is connected to this pin on the ESP32
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

	gotValues = False
	retries = 4

	retry = 0

	try:
		smokeValue = sensor.readSmoke()
		lpgValue = sensor.readLPG()
		methaneValue = sensor.readMethane()
		hydrogenValue = sensor.readHydrogen()
		gotValues = True
	except Exception as e:
		print(e)
		gotValues = False
		retry = retry + 1
		if retry == retries:
			print("Retries exceeded, restarting...")
			machine.reset()

	if gotValues:
		# MQTT Message
		message = {}

		message["smoke"] = smokeValue
		message["lpg"] = lpgValue
		message["methane"] = methaneValue
		message["hydrogen"] = hydrogenValue

		print(message)

		# Publish message to MQTT

		client = MQTTClient(client_id="kitchen-mq2", server="10.0.1.200", user="mqtt", password="hassio") 

		connected = False

		while not connected:
			try:
				client.connect()
				connected = True
			except:
				connected = False
				utime.sleep(5)

		topic = "/kitchen/mq2"

		data = bytes(ujson.dumps(message),"utf-8")
		
		client.publish(topic=topic, msg=data)

		if connected:
			client.disconnect()

	# Wait
	utime.sleep(60)
