'''
                    Simple model railway automation v1.0

Author:  Peter Wallen 
Created: 20/01/2013

This python script demonstrates the use of two python modules:
   hornby.py - this modules encapsulates the functions of the Hornby Elite DCC controller.
   heSensor.py - this module encapsulates the hall-effect sensors used to detect a trains position.
These modules can be replaced to accommodate alternative hardware. 
'''

# Use hornby.py as the interface for controlling trains and accessories
# see hornby.py for information on using this module.
import hornby
# Use heSensor.py as the interface for train detection
# see heSensor.py for information on using this module.
import heSensor

#Use python standard module time for simple timming functions 
import time

# example functions for South West Digital's Class 108 (55488) decoder

# F0 Lights on
def lights_on(t):
  t.function(0,hornby.ON)
# F0 Lights off
def lights_off(t):
  t.function(0,hornby.OFF)
# F1 Sound on
def sound_on(t):
  t.function(1,hornby.ON)
# F1 Sound off
def sound_off(t):
  t.function(1,hornby.OFF)
# F2 Horn 1
def horn1(t):
  t.function(2,hornby.ON)
  time.sleep(.1)
  t.function(2,hornby.OFF)
# F3 Horn 2
def horn2(t):
  t.function(3,hornby.ON)
  time.sleep(.1)
  t.function(3,hornby.OFF)
# F4 Brake
def brake(t):
  t.function(4,hornby.ON)
  time.sleep(.1)
  t.function(4,hornby.OFF)
# F5 Buzzer x 2
def buzzer2(t):
  t.function(5,hornby.ON)
  time.sleep(.1)
  t.function(5,hornby.OFF)
# F6 Buzzer x 1
def buzzer1(t):
  t.function(6,hornby.ON)
  time.sleep(.1)
  t.function(6,hornby.OFF)
# F7 Aux 1 on
def aux1_on(t):
  t.function(7,hornby.ON)
# F7 Aux 1 off
def aux1_off(t):
  t.function(7,hornby.OFF)
# F8 Aux 2 on
def aux2_on(t):
  t.function(8,hornby.ON)
# F8 Aux 2 off 
def aux2_off(t):
  t.function(8,hornby.OFF)
# F9 Directional Gear Change
def gear_change(t):
  t.function(9,hornby.ON)
  time.sleep(.1)
  t.function(9,hornby.OFF)
# F10 Guards Whistle
def guards_whistle(t):
  t.function(10,hornby.ON)
  time.sleep(.1)
  t.function(10,hornby.OFF)

# Accessory - station signal Go
def station_signal_go(a) :
  a.activate()
# Accessory - station signal Stop
def station_signal_stop(a) :
  a.deactivate()

# helper function - wait a given number of seconds
def wait(secs):
  print "Wait {0:d} seconds".format(secs)
  time.sleep(secs)

# Open a serial connection with the Hornby Elite DCC controller 
hornby.connection_open('/dev/ttyUSB1',9600)

# set_debug(True) to show the data transmitted and received from the controller
hornby.set_debug(False)

# Enable the I2C bus between the Rpi and the sensor controller(s)
# see heSensor.py for information
heSensor.i2Cbus_open()
# Configure the sensor controller(s) - call heSensor for each controller on the bus
# see heSensor.py for information
heSensor.config(0x20)

# create a sensor object to represent each sensor on the track
# parameter 1 = address of controller
# parameter 2 = which of the two banks on the controller the sensor is connected to (A or B)
# parameter 3 = which of the ports on the controller the sensor is connected to (1 to 8)
s1 = heSensor.Sensor(0x20,'A',1)
s2 = heSensor.Sensor(0x20,'A',2)

# create a train object to represent each train to be controlled
# parameter 1 = DCC addres
t1 = hornby.Train(3)

# creat a accessory object for each accessory (points, signals etc) to be controlled
# parameter 1 = address of accessory (0 - 251)
# parameter 2 = sub address of accessory (see accessory controller and xpressnet protocol) 
a1 = hornby.Accessory(0,2)

print '''
         Simple Model Railway Automation Demonstration
         ---------------------------------------------
         
      '''

repeat = 1
while repeat <= 1 :
  print "Iteration {0:d}".format(repeat)
  wait(10)
  print "sound on"
  sound_on(t1) 
  wait(10)
  print "lights on"
  lights_on(t1)
  wait(20)
  print "change signal to go"
  station_signal_go(a1)
  wait(5)
  print "blow guards whistle" 
  guards_whistle(t1)
  wait(2)
  print "sound buzzer"
  buzzer2(t1)
  wait(1)
  print "move train forward"
  t1.throttle(15,hornby.FORWARD)
  wait(10)
  print "change signal to stop"
  station_signal_stop(a1) 
  print "wait on sensor 2"
  s2.wait()
  print "stop train"
  t1.throttle(0,hornby.FORWARD)
  wait(10)
  print "directional gear change"
  gear_change(t1)
  wait(1)
  print "move train in reverse"
  t1.throttle(15,hornby.REVERSE)
  wait(22)
  print "sound horn twice"
  horn2(t1)
  print "stop train on signal"
  t1.throttle(0,hornby.REVERSE)
  print "brake"
  brake(t1) 
  wait(10)
  print "change signal to go"
  station_signal_go(a1)
  wait(2)
  print "move train in reverse"
  t1.throttle(15,hornby.REVERSE)
  print "wait on sensor 1"
  s1.wait()
  print "sound horn once"
  horn1(t1)
  wait(3)
  print "stop train" 
  t1.throttle(0,hornby.REVERSE)
  print "change signal to stop"
  station_signal_stop(a1)
  wait(10)
  print "brake"
  brake(t1)
  wait(5)
  print "sound off"
  sound_off(t1)
  wait(5)
  print "lights off"
  lights_off(t1) 

  repeat += 1

# close the connection with a Hornby Elite DCC controller 
hornby.connection_close()

print 'program terminates'
