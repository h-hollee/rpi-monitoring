# This program allows a user to monitor the temperature and humidity
# of the environment in which the sensors are located. The current
# program is set to read the readings every 30 minutes. The program
# uses LED lights to display the range of temperature and humidity and will
# also print the readings to an external LCD screen as well. The results are then
# pushed to an external json file and printed to an HTML page.

#!/usr/bin/env python

import time
import grovepi
from time import sleep
from grovepi import *
from math import isnan
import json
import grove_rgb_lcd import *

# Connect Grove light sensor to analog port A0 of GrovePi
light_sensor = 0

# Connect temperature / humidity sensor to port 7
dht_sensor_port = 7
dht_sensor_type = 0

# Connect LED to digital ports on GrovePi
blueLED = 4
greenLED = 5
redLED = 6

# Set LCD background color to green (part of enhancement)
setRGB(0, 255, 0)

# Turn on LED once sensor exceeds threshold resistance
threshold = 10

# Set light sensor as input and LED as output
grovepi.pinMode(light_sensor, "INPUT")
grovepi.pinMode(blueLED, "OUTPUT")
grovepi.pinMode(greenLED, "OUTPUT")
grovepi.pinMode(redLED, "OUTPUT")

# Stores output data of temp and humidity readings
output = []

# First enhancement: to create a function to turn LEDs off
def ledOff():
		grovepi.digitalWrite(blueLED, 0)
		grovepi.digitalWrite(greenLED, 0)
		grovepi.digitalWrite(redLED, 0)
		
# While True, determine if ambient light is present. If so, obtain sensor readings,
# convert to Fahrenheit, illuminate appropriate LED bulbs, display information on LCD screen,
# and write data to JSON file.
while True:
        try:
		# get sensor value
		sensor_value = grovepi.analogRead(light_sensor)

		# Calculate resistance of sensor in K
		if sensor_value <= 0: #stops dividing by 0 errors
                        resistance = 0
                else:
                        resistance = float(1023 - sensor_value) * 10 / sensor_value

		# if ambient light, record values
		if resistance > threshold:
		# Send high to switch off LED
                        ledOff()
		else:
			# Get temperature and humidity readings from sensor
			[temp, humidity] = dht(dht_sensor_port, dht_sensor_type)

			# Convert celcius to farenheit
			temp = ((temp*9)/5.0) + 32
			print("temp =", temp, "F\thumidity =", humidity,"%")

			# Check for 'not a number' error (added as enhancement)
			if isnan(temp) is True of isnan(humidity) is True:
                                raise TypeError('nan error')

			# Send low to switch on LED according to temp and humidity 
			if temp > 95:
                                grovepi.digitalWrite(redLED, 1)
			elif (60 > temp < 85) and (humidity < 80):
				grovepi.digitalWrite(greenLed, 1)
			elif (85 > temp < 95) and (humidity < 80):
				grovepi.digitalWrite(blueLED, 1)
			elif humidity > 80:
				grovepi.digitalWrite(greenLED, 1)
				grovepi.digtalWrite(blueLED, 1)
			else:
                                print("Not applicable")

                        t = str(temp)
                        h = str(humidity)

                        # print data to LCD screen (enhancement)
                        setText_norefresh("Temp:" + t + "F\n" + "Humidity:" + h + "%")

        # Error exceptions
	except (IOError, TypeError) as e:
			print(str(e))
			setText("")

	except KeyboardInterrupt as e:
			print(str(e))
			ledOff() # utilizing newly created function
			break

	#  Append new readings for output 
	output.append([t, h])

	# Refresh and get new readings every 30 minutes (1800 seconds)
	sleep(1800)

# Sends data to output file
with open('output.json', 'a') as outfile:
	json.dump(output, outfile)
