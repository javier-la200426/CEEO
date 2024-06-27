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
'''
#Defining dictionary for each sensor/motor
def big_motor_print():
    print("big_motor")
def color_sensor_print():
    print("color sensor")
def distance_sensor_print():
    print("distance sensor")
def force_sensor_print():
    print("force sensor")
def light_matrix_print():
    print("light matrix")
def small_motor_print():
    print("small motor")

#these functions print values of each sensor, motor, etc...
#creating dictonary where key is device ID, and value is corresponding function
function_dict = {
    49: big_motor_print,
    61: color_sensor_print,
    62: distance_sensor_print,
    63: force_sensor_print,
    64: light_matrix_print,
    65: small_motor_print
}

    
function_dict[65]()


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


