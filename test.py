#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Copyright 2016, Frank Heuer, Germany
test.py is demonstrating some capabilities of the SDS011 module.
If you run this using your Nova Fitness Sensor SDS011 and
do not get any error (one warning will be ok) all is fine.

This is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

'''
import sys
import time

# Create a new sensor instance
from main import SDS011

'''
On Win, the path is one of the com ports. On Linux / Raspberry Pi
it depends. May be one of "/dev/ttyUSB..." or "/dev/ttyAMA...".
On the Pi make sure the login getty() is not using the serial interface.
Have a look at Win or Linux documentation.
Look e.g. via lsusb command for Qin Hen Electronics USB id.
'''

import matplotlib.pyplot as plt
def printlog(level, string):
    """Change this to reflect the way logging is done."""
    sys.stderr.write("%s: %s\n" % (level, string))

debug = 0       # debug level in sds011 class module
cycles = 4      # serial read timeout in seconds, dflt 2
timeout = 2     # timeout on serial line read
# print values in mass or pieces
unit_of_measure = SDS011.UnitsOfMeasure.MassConcentrationEuropean
for arg in range(len(sys.argv) - 1, 0, -1):
    if sys.argv[arg][0:2] == '-d':
        debug += 1
        debug = int(sys.argv[arg + 1])
        del sys.argv[arg + 1]
        del sys.argv[arg]
    elif sys.argv[arg][0:2] == '-c':
        cycles = int(sys.argv[arg + 1])
        del sys.argv[arg + 1]
        del sys.argv[arg]
    elif sys.argv[arg][0:2] == '-t':
        timeout = int(sys.argv[arg + 1])
        del sys.argv[arg + 1]
        del sys.argv[arg]
    elif sys.argv[arg][0:2] == '-u':
        if sys.argv[arg + 1] == '0':
            unit_of_measure = SDS011.UnitsOfMeasure.MassConcentrationEuropean
        elif sys.argv[arg + 1] == '1':
            unit_of_measure = SDS011.UnitsOfMeasure.ParticelConcentrationImperial
        else:
            raise RuntimeError("%s is not a valid unit of measure")
        del sys.argv[arg + 1]
        del sys.argv[arg]
print ('Argument List:', str(sys.argv))
if len(sys.argv) < 2:
    sys.exit("Usage: python test.py [-d {1..5}] [-c cnt] [-t secs] [-u 0|1] com_port [duty_cycle 0..30]\n"
             "com port e.g. /dev/ttyUSB0\n"
             "-d(ebug) debug level (dflt 0). Use 10, 14, 16, 18, 20, 30, 40, 50. Low value means verbose, 0 means off\n"
             "-c(nt) cnt defines the amount of test cycles (dflt 4).\n"
             "-t(imeout) secs defines the timeout of serial line readings (dflt 2).\n"
             "-u(nit_of_measure):\n\
             \t0: output in µg/m3 (default);\n\
             \t1: output in pcs/0.01qf (pieces per cubic feet)\n"
             "\t\tduty cycle defines sensor measurement time in minutes (dflt 2).")
if debug > 0:
    # Activate simple logging
    import logging
    import logging.handlers
    logger = logging.getLogger()
    # Available levels are the well known
    # logging.INFO, logging.WARNING and so forth.
    # Between INFO (=20)and DEBUG (=10) are fine grained
    # messages with levels 14,16 and 18. You might want
    # to use these values. Here is an Example with 16
    # logger.setLevel(16)
    # Activate simple logging
    logger.setLevel(debug)

def printValues(timing, values, unit_of_measure):

    print("PM2.5: "+ str(values[1]), ", PM10: "+ str(values[0]))
    # print("Values measured in pcs/0.01sqf: PM2.5 %d, PM10 %d" % (Mass2Con('pm25',values[1]), Mass2Con('pm10',values[0])))

# simple parsing the command arguments for setting options
# Create an instance of your sensor
# options defaults: logging None, debug level 0, serial line timeout 2
# option unit_of_measure (default False) values in pcs/0.01sqf or mass ug/m3
time.sleep(1)

sensor = SDS011(sys.argv[1], timeout=timeout, unit_of_measure=unit_of_measure)
# raise KeyboardInterrupt
# Now we have some details about it
print("SDS011 sensor info:")
print("Device ID: ", sensor.device_id)
print("Device firmware: ", sensor.firmware)
print("Current device cycle (0 is permanent on): ", sensor.dutycycle)
time.sleep(1)
print(sensor.workstate)
time.sleep(1)

print(sensor.reportmode)
if unit_of_measure == SDS011.UnitsOfMeasure.MassConcentrationEuropean:
    unit = 'µg/m³'
else:
    unit = 'pcs/0.01cft'
print("Units: "+str(unit))

# Set dutycyle to nocycle (permanent)
sensor.reset()
sleepTime=0
warmupTime= 0
# Example of switching the WorkState
pm25Array=[]
pm100Array=[]
i=100
while i>0:
    #print("Measurement "+ str(i)+"\n")
    #print("Warming up sensor for " + str(warmupTime) +" seconds")
    sensor.workstate = SDS011.WorkStates.Measuring
    time.sleep(warmupTime)
    last = time.time()
    while True:
        last1 = time.time()
        values = sensor.get_values()
        if values is not None:
            printValues(time.time() - last, values, sensor.unit_of_measure)
            break
        time.sleep(2)

    #print("Read was succesfull. Going to sleep for "+str(sleepTime)+" seconds")
    #sensor.workstate = SDS011.WorkStates.Sleeping
    time.sleep(sleepTime)
    i-=1
    pm25Array.append(values[1])
    pm100Array.append(values[0])
print("Plotting data...")
print("PM100:\n")
print(pm100Array)
print("PM2.5")
print(pm25Array)

plt.plot(pm25Array, "ro")
plt.ylabel("PM2.5")

plt.xlabel("Measurement Number")
plt.show()

