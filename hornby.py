'''
                     Simple Model Railway Automation 
                     Hornby Eilte Support Module

Author : Peter Wallen
Created: 20/1/13
Version: 1.0

This code encapsulates functions of the Hornby Elite DCC controller through the classes: Train and Accessory.
    
This module requires python-serial to be installed.    

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.    

'''

import serial
import struct
import time

FORWARD = 0
REVERSE = 1
OFF = 0
ON = 1

debug = 0

ser = 0

def connection_open(device,baud):
  '''
    This function must be called once by the automation script to open a serial connection between the computer
    and the DCC controller.
    usage:
      device = a string containing the USB serial port name.
      baud = the speed of the port eg. 9600
    example:
       connection_open('/dev/ttyUSB1',9600)
  '''
  global ser
  try: 
    ser = serial.Serial(device,baud)
  except EnvironmentError as e:
    print e
    raise RuntimeError('Unable to open connection with Hornby Elite Controller')

def connection_close():
  '''
  This function must be called once by the automation script to close the serial port opened by a previous 
    connectio_open call.
 
    example:
       connection_close()
  '''
  global ser
  # check to see if ser has been intialized by open
  if not ser:
    raise RuntimeError('Connection cannot be closed because it has not been opened') 
  try:
   ser.close()
  except EnvironmentError as e:
    print e 
    raise RuntimeError('Unable to close connection with Hornby Elite Controller')

def set_debug(arg):
  '''
   The automation script can call set_debug(True) to print the data transmitted and received to and from the
   DCC controller.
   Call set_debug(False) to stop printing diagnostic information to the console. 
  '''
  global debug
  debug =arg

def parity(message):
  '''
   Internal function (should not be called directly by the automation script) to add a Error Detection  byte to the
   message transmitted to the DCC controller. This byte is formed using an X-Or-linkage of all prededing bytes
   in the message.
   
  '''
  lrc = 0
  for b in message:
    lrc ^= b
  message.append(lrc)

def send(message):
  '''
   Internal function (should not ne called directly by the automation script) to send a message to the DCC controller
   and receive a reply.
   The function will look for a reply which starts with a ENQ (0x05). If this is not received, the message will be 
   re-transmitted to a maximum of 5 times.  
  '''
  ok = False
  trys = 1
  while (not ok and trys < 5) :
    ser.write(message)
    if debug :
      print 'trys = %d send:' % (trys) , 
      for byte in message:print(hex(byte)) ,
    time.sleep(.1)
    if debug :
      print ' receive: ',     
    while ser.inWaiting() > 0 :
      enq = ser.read()
      if debug :
        print enq.encode('hex') ,  
      if enq == '05'.decode('hex') : 
        ok = True
    if debug :
      print 
    trys += 1

class Train(object):
  '''
   The class describing a train object. 
   A train object is associated with each train to be controlled.
  '''
  def __init__(self,address):
    '''
   The class constructor must be called with one parameter containg the train address.
   Example:
          t1 = Train(3)
    '''
    self.address = address
    self.group = [0,0,0]

  def throttle(self,speed,direction):
    '''
   This method controls the train's throttle.
   The two parameters are:
   speed 0 - 127  where 0 = stop
   direction 0 - FORWARD
             1 - REVERSE
   For imformation about the message sent by this method refer to the XpressNet protocol:
     'Locomotive speed and direction operations'
   example:
   t1.throttle(15,FORWARD)  # move train forward with a speed of 15 steps
   t1.throttle(0,FORWARD)   # stop train      
    '''
    message = bytearray('E400000000'.decode('hex'))
    message[1] = 0x13   #128 speed steps
    struct.pack_into(">H",message,2,self.address)
    message[4] = speed
    if direction == FORWARD : message[4] |= 0x80
    elif direction == REVERSE : message[4] &= 0x7F
    parity(message)
    send (message)

  def function(self,num,switch):
    '''
   This method controls the train's functions e.g. lights and sound.
   The use of functions depends on the decoder fitted to the train.
   For imformation about the message sent by this method refer to the XpressNet protocol:
     'Function operation instructions'
   The two parameters are:
   num - Function number 0 - 12
   switch - 0 - OFF
            1 - ON
   example:
    t1.function(0,ON)  # switch function 0 on
    t1.function(0,OFF) # switch function 0 off      
    '''
    # function table columns
    # 0 = group 0 - 2
    # 1 = group code 0x20, 0x21, 0x22
    # 2 = on mask 
    # 3 = off mask
    function_table = [[0,0x20,0x10,0xEF], \
                      [0,0x20,0x01,0xFE], \
                      [0,0x20,0x02,0xFD], \
                      [0,0x20,0x04,0xFB], \
                      [0,0x20,0x08,0xF7], \
                      [1,0x21,0x01,0xFE], \
                      [1,0x21,0x02,0xFD], \
                      [1,0x21,0x04,0xFB], \
                      [1,0x21,0x08,0xF7], \
                      [2,0x22,0x01,0xFE], \
                      [2,0x22,0x02,0xFD], \
                      [2,0x22,0x04,0xFB], \
                      [2,0x22,0x08,0xF7], \
                     ]
    if num >= len(function_table):
      raise RuntimeError('Invaild function') 
    message = bytearray('E400000000'.decode('hex')) 
    message[1] = function_table[num][1]
    if switch == ON :
      self.group[function_table[num][0]] |= function_table[num][2]
    elif switch == OFF :
      self.group[function_table[num][0]] &= function_table[num][3]
    else :
      raise RuntimeError('Invalid switch on function')  
    message[4] = self.group[function_table[num][0]]
    struct.pack_into(">H",message,2,self.address)
    parity(message)
    send(message)

class Accessory(object):
  '''
   The class describing a accessory object.
   A accessory object is associated with each accessory to be controlled.
  '''   
  def __init__(self,address,offset):
    '''
   The class constructor must be called with two parameters.
   parameter 1 = the address of the accessory 0 - 255
   parameter 2 = the sub address of the accessory device
    For further information about specifying the second parameter, refer to accessory controller documentation and
    the Xpressnet protocol : Accessory Decoder operation request,   
   Example:
          a1 = Accessory(0,2)
    '''
    self.address = address
    self.offset = offset
  def activate(self):
    '''
    Method to activate (switch) an accessory
    Example:
         a1.activate()
    '''
    message = bytearray('520000'.decode('hex'))
    message[1] = self.address
    message[2] = self.offset
    message[2] |= 0x80  # switch MSB on
    message[2] |= 0x01  # switch LSB on
    parity(message)
    send(message)
  def deactivate(self):
    '''
     Method to deactivate (switch) an accessory
     Example:
         a1.deactivate()
    '''
    message = bytearray('520000'.decode('hex'))
    message[1] = self.address
    message[2] = self.offset
    message[2] |= 0x80 # switch MSB on
    message[2] &= 0xFE # switch LSB off
    parity(message)
    send(message)
    

