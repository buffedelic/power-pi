#!/usr/bin/env python
import ow

def report_state():
	ow.init('localhost:4304')
	print(ow.Sensor( '/1D6CEC0C00000094').counter_A)
	print(ow.Sensor( '/1D00FD0C0000009B').counter_A)
	print(ow.Sensor( '/1D00FD0C0000009B').counter_A)

	sensorlist = ow.Sensor('/').sensorList()
	for sensor in sensorlist:
		print('Device Found')
		print('Address: ' + sensor.address)
		print('Family: ' + sensor.family)
    	print('ID: ' + sensor.id)
    	print('Type: ' + sensor.type)
    	print(' ')
	#return sensor.id
ow.finish()
report_state()
