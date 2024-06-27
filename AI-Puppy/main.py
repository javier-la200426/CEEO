# main.py -- put your code here!
import hub, utime, color
import force_sensor as fs
import distance_sensor as ds
import color_sensor as cs
from hub import port, button, light_matrix, sound, light
import time
import device
'''
Iterate through all ports,

    Get the ID from individual port

        Map it to a value
        (keys are ID's and values are function pointers)
        Call corresponding function

We have 6 ports A-F
where hub.port.A = 0
... numbered 0-5
'''
#Defining dictionary for each sensor/motor
def big_motor_print(port_num):
    print("big_motor", port_num)
    
def color_sensor_print(port_num):
    print("color sensor", port_num)
    
def distance_sensor_print(port_num):
    print("distance sensor", port_num)
    
def force_sensor_print(port_num):
    print("force sensor", port_num)
    
def light_matrix_print(port_num):
    print("light matrix", port_num)
    
def small_motor_print(port_num):
    print("small motor", port_num)
    
def medium_motor_print(port_num):
    print("medium motor", port_num)

#these functions print values of each sensor, motor, etc...
#creating dictonary where key is device ID, and value is corresponding function
function_dict = {
    48: medium_motor_print,
    49: big_motor_print,
    61: color_sensor_print,
    62: distance_sensor_print,
    63: force_sensor_print,
    64: light_matrix_print,
    65: small_motor_print
}

#Iterating over 6 ports (0 to 5
for i in range(6):
    #for each port get the device Id
    current_port = i
    try:
        port_id = device.id(current_port) #this should be either 49, or 61 or 62 or... 65 #handle exception when not found
        # Call the corresponding function if the device ID is found
        if port_id in function_dict:
            function_dict[port_id](i)
        else:
            print(f"No function defined for device ID {port_id}")
    except OSError as e:
        # Means port does not have any sensor connected to it
        print("YAA")
        print(f"Port {current_port} error: {e}")
        
    


'''
List ID's
import device
device.id(hub.port.A) # or B,C,...

Light Matrix = 64
Force Sensor = 63
Distance sensor = 62 
Color sensor = 61

Big Motor = 49
Small Motor = 65



'''
