import device
import motor
import color_sensor
import color
import distance_sensor
import force_sensor
import time #delete this
import asyncio


#test this
def big_motor_print(port_num):
    print("big_motor", port_num)
    abs_pos = motor.absolute_position(port_num)
    if (abs_pos < 0):
        abs_pos = abs_pos + 360
    return abs_pos

#color.RED = 1
#9 colors:
''' 
Table 1:

Red - 1
Green - 2
Blue - 3
Magenta - 4
Yellow 5
Orange - 6
Azure - 7 
Black - 8
White - 9

'''
#returns tuple with (color from table 1, r, g , b)
def color_sensor_print(port_num):
    #print("color sensor", port_num)
    color_info = [-1,-1,-1,-1] #tuple with, color, r,g,b values 
    #variable I will use to identify color based on Table 1
    my_color = -1 #if not color is detected
    sensor_color = color_sensor.color(port_num) #color that sensor detects
    if sensor_color is color.RED:
        my_color = 1
    elif sensor_color is color.GREEN:
        my_color = 2
    elif sensor_color is color.BLUE:
        my_color = 3
    elif sensor_color is color.MAGENTA:
        my_color = 4
    elif sensor_color is color.YELLOW:
        my_color = 5
    elif sensor_color is color.ORANGE:
        my_color = 6
    elif sensor_color is color.AZURE:
        my_color = 7
    elif sensor_color is color.BLACK:
        my_color = 8
    elif sensor_color is color.WHITE:
        my_color = 9

    return my_color
    
def distance_sensor_print(port_num):
    #print("distance sensor", port_num)
    return distance_sensor.distance(port_num)
    
def force_sensor_print(port_num):
    #print("force sensor", port_num)
    return force_sensor.force(port_num)
    
    
def light_matrix_print(port_num):
    #print("light matrix", port_num)
    return 1 #change this

#test this
def small_motor_print(port_num):
    #print("small motor", port_num)
    abs_pos = motor.absolute_position(port_num)
    if (abs_pos < 0):
        abs_pos = abs_pos + 360
    return abs_pos

#absolute position goes like 0...179, -180, -179 = vals
#want 0...179, 180, 181,... 360 (then go back to 0)
#so return 360 + val
def medium_motor_print(port_num):
    #print("medium motor", port_num)
    abs_pos = motor.absolute_position(port_num)
    if (abs_pos < 0):
        abs_pos = abs_pos + 360
    return abs_pos

function_dict = {
    48: medium_motor_print,
    49: big_motor_print,
    61: color_sensor_print,
    62: distance_sensor_print,
    63: force_sensor_print,
    64: light_matrix_print,
    65: small_motor_print
}

port_info = [()] * 6

#execute code

start_time = time.time()
current_time = start_time

async def sensor_loop_jav():
    while True:
        for i in range(6):
            #for each port get the device Id
            current_port = i
            try:
                #below is line that will give you error (potentially)
                port_id = device.id(current_port) #this should be either 49, or 61 or 62 or... 65 #handle exception when not found
                # Call the corresponding function if the device ID is found
                if port_id in function_dict:
                    number = function_dict[port_id](i)
                    port_info[i] = (1, i, port_id, number)
                else:
                    #print(f"No function defined for device ID {port_id}")
                    port_info[i] = (0,0,0,0)
            except OSError as e: #nothing connected to it
                # Means port does not have any sensor connected to it
                port_info[i] = (0,0,0,0)
                #print("YAA")
                #print(f"Port {current_port} error: {e}")
        print(port_info)
        await asyncio.sleep(1) 
'''      
async def test_loop():
    while True:
        print("running_code")
        await asyncio.sleep(1) 
'''
# Simulate blocking I/O-bound code
def blocking_code():
    while True:
        #print("Blocking operation")
        # Perform blocking I/O-bound tasks here
        # For example, reading a large file
        input("Please enter something: ")
        time.sleep(1)

async def run_blocking_code():
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, blocking_code)


    
async def main():
    task1 = asyncio.create_task(sensor_loop_jav())
    task2 = asyncio.create_task(run_blocking_code())
    await asyncio.gather(task1, task2)

asyncio.run(main())


