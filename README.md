smrc
====

Simple model railway control for the Raspberry Pi

For background information and setup notes see:

http://www.peterwallen.talktalk.net/My_Pi/Projects/Entries/2012/10/24_Model_Railway_Automation.html

The project consists of the following python scripts:

hornby.py - encapsulates functions of the Hornby Elite DCC Controller.

heSensor.py - encapsulates hardware to detect the location of trains using  hall-effect sensors.

smra1.py - a simple automation script demonstrating the use of hornby.py and heSensor.py.

smrc1.py - a web server that allows a browser to control model trains using hornby.py.

Notes for using smrc1.py

This script requires 2 directories 'templates' and 'static'.
templates - contains the html. 
static - contains resources required by the html. The example html uses a number of jquery libraries and these should downloaded and saved in this directory. For further information see templates/control_panel1



