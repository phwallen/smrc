'''
               Simimple Model Railway Automation
               Hall-effect Sensor Support Module

Author : Peter Wallen 
Created : 21/1/13
Version 1.0

This code encapulates hardware associated with sensors used to detect the location of trains.

The hardware supported comprises of :
 One or more Microchip MCP23017 16-Bit I/O Expanders acting as sensor controllers.
 Each sensor controller can be connected to a maximum of 16 hall-effect sensors.

 This module requires python-smbus
'''

import smbus
import time

bus = 0

def i2Cbus_open():
  '''
    This function must be called once by the automation script to open the I2C bus between
    the Rpi and the sensor controller(s).
    
  '''
  global bus
  try:
    bus = smbus.SMBus(0)
  except EnvironmentError as e:
    print e
    raise RuntimeError("Unable to open I2C bus")
 
def config(address):
  '''
  This function must be called once by the automation script for each sensor controller.
  The address of the controller is determined by the A10,A1,A2 pins on the MCP23017 chip.
  eg. If A0,A1 and A2 are LOW then the address should be 0x20.

  For information about configuring the sensor controller see the Microchip MCP23017 datasheet.
  For eaxample to connect sensors to GPA0 - GPA7, use GPB0 - GPB7 to drive LED indicators and
  enable interupts to allow the last sensor triggered to be stored in the interupt capture register,
  configure as follows:
  bus.write_byte_data(address,IODIRA,0xff)  # set all ports in bank A to input
  bus.write_byte_data(address,IODIRB,0x00)  # set all ports in bank B to output
  bus.write_byte_data(address,GPPUA,0xff)   # enable pullup resistors for bank A
  bus.write_byte_data(address,GPINTENA,0xff) # enable interupts on port A  
  '''
  global bus

  # MCP23017 register constants
  IODIRA =  0x00 
  IODIRB =  0x01
  GPINTENA = 0X04
  GPINTENB = 0x05
  GPPUA  =  0x0c
  GPPUB  =  0x0d
  INTCAPA=  0x10
  INTCAPB=  0x11
  GPIOA  =  0x12
  GPIOB  =  0x13
  
  bus.write_byte_data(address,IODIRA,0xff)  # set all ports in bank A to input
  bus.write_byte_data(address,IODIRB,0x00)  # set all ports in bank B to output
  bus.write_byte_data(address,GPPUA,0xff)   # enable pullup resistors for bank A
  bus.write_byte_data(address,GPINTENA,0xff) # enable interupts on port A 
 
class Sensor(object):
  '''
    The class describing a sensor object.
    A sensor object is associate with each train detection sensor.
  '''
  def __init__(self,address,bank,port):
    '''
     The class constructor is called with the following parameters:
     address : the address of the sensor controller on the I2C bus eg. 0X20
     bank : the register group the sensor is connected to: 'A'  for GPA0 - GPA7 and 'B' for GPB0 - GPB7
     port : the port on the sensor controller the sensor is connected to (1 - 8).
            NB. port 1 corresponds to pin GPx0 and port 8 corresponds to pin GPx7
            where x = A or B
    '''  
    global bus   
    mask_table = [0x00,0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80]
    if bus == 0 :
      raise RuntimeError("I2C bus has not been opened")
    self.address = address
    self.port = 0
    if bank == "A" :
      self.iodir = 0x00
      self.gpinten = 0x04
      self.gppu = 0x0c
      self.intcap = 0x10
      self.gpio = 0x12
    elif bank == "B" :
      self.iodir = 0x01
      self.gpinten = 0x05
      self.gppu = 0x0d
      self.intcap = 0x11
      self.gpio = 0x13
    else :
      raise RuntimeError("Invalid bank must be A or B")  
    if port > 8 or port < 1 :
      raise RuntimeError("Invalid port must be between 1 and 8")
    else :
      self.port |= mask_table[port]

  def wait(self) : 
    '''
    This method will poll the interupt capture registor for the sensor until its triggered.
    In addition, it will control a status LED connected to the corresponding port on bank A. 
    '''
    x = bus.read_byte_data(self.address,self.intcap)

    # switch off indicator for appropriate port
    status  = bus.read_byte_data(self.address,0x13)
    status &= self.port
    bus.write_byte_data(self.address,0x13,status)

    while (x & self.port) :
      x = bus.read_byte_data(self.address,self.intcap)
      time.sleep(1)

    # switch on indicator for appropriate port 
    status  = bus.read_byte_data(self.address,0x13)
    status |= self.port 
    bus.write_byte_data(self.address,0x13,status)

