'''
    Simple model railway control v1.0
    
    Author:  Peter Wallen 
    Created: 03/03/2013
    
    This python script demonstrates how a python script can be used as a
    web server to manage a web browser clients that controls a model train.
    The script use the web.py libray for server functionallity and 
    hornby.py to control the model train using a Hornby Elite DCC controller
     
'''
import web
import hornby

render = web.template.render('templates/')
urls = (
'/.*','control_panel'
) 
print '''
        Simple Model Railway Control Server
        -----------------------------------
      '''

app = web.application(urls,globals(),autoreload=False)
    
hornby.connection_open('/dev/ttyUSB1',9600)
t1 = hornby.Train(3)
a1 = hornby.Accessory(0,2)

class control_panel:
    def GET(self):
        return render.control_panel1('003 Class 108 DMU')

    def POST(self) :
        data = web.input()
        if data.id == 'forward' :
            t1.throttle(int(data.value),hornby.FORWARD)
        elif data.id == 'reverse' :
            t1.throttle(int(data.value),hornby.REVERSE)
        elif data.id == 'f0-on' :         #Lights
            t1.function(0,hornby.ON)
        elif data.id == 'f0-off' :
            t1.function(0,hornby.OFF)
        elif data.id == 'f1-on' :
            t1.function(1,hornby.ON)      #Sound
        elif data.id == 'f1-off' :
            t1.function(1,hornby.OFF) 
        elif data.id == 'f2' :
            t1.function(2,hornby.ON)      #Horn 1
            t1.function(2,hornby.OFF)
        elif data.id == 'f3' :
            t1.function(3,hornby.ON)      #Horn 2
            t1.function(3,hornby.OFF)
        elif data.id == 'f4' :
            t1.function(4,hornby.ON)      #Brake
            t1.function(4,hornby.OFF)
        elif data.id == 'f5' :
            t1.function(5,hornby.ON)      #Buzzer x 2
            t1.function(5,hornby.OFF)
        elif data.id == 'f6' :
            t1.function(6,hornby.ON)      #Buzzer x 1
            t1.function(6,hornby.OFF)
        elif data.id == 'f9' :
            t1.function(9,hornby.ON)      #Directional Gear Change
            t1.function(9,hornby.OFF)
        elif data.id == 'f10' :
            t1.function(10,hornby.ON)     #Guards Whistle
            t1.function(10,hornby.OFF)
        elif data.id == 'a1-on' : 
            a1.activate()                 #Signal Go
        elif data.id == 'a1-off' :
            a1.deactivate()               #Signal Stop 
        print data.id
        return 'id:' + data.id + ' value:' + data.value

if __name__ == "__main__":
    print 'press ctrl c to stop the program'
    app.run()
    # close the connection withthe Hornby Elite DCC controller    
    hornby.connection_close()
    print
    print 'program terminates'     