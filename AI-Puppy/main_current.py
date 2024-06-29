# https://xtermjs.org/docs/api/terminal/classes/terminal/#options
#https://pyscript.com/@agiammarchi/spike-ide-copy/latest
#BLE_CEEO_url = 'https://raw.githubusercontent.com/chrisbuerginrogers/SPIKE_Prime/main/BLE/BLE_CEEO.py'

from pyscript import document, window
import ampy
import restapi
import asyncio
import time

ARDUINO_NANO = 128
SPIKE = 256

stop_loop = False #indicates when to stop loop (u want it to stop when user has access to repl)
sensor = True #for switching between if and else statements (going from user repl to sensors)

#defining functions to paste into spike
sensor_code = """

import device
import motor
import color_sensor
import color

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
    print("color sensor", port_num)
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
    
    color_info[0] = my_color
    
    rgbi = color_sensor.rgbi(port_num)
    
    color_info[1] = rgbi[0] #red
    color_info[2] = rgbi[1] #green
    color_info[3] = rgbi[2] #blue
    
    color_info_tuple = tuple(color_info)
        
    #print("My-COlor: ", color_info_tuple)
    
    return color_info_tuple
    
def distance_sensor_print(port_num):
    print("distance sensor", port_num)
    return 1 #change this
    
def force_sensor_print(port_num):
    print("force sensor", port_num)
    return 1 #change this
    
def light_matrix_print(port_num):
    print("light matrix", port_num)
    return 1 #change this

#test this
def small_motor_print(port_num):
    print("small motor", port_num)
    abs_pos = motor.absolute_position(port_num)
    if (abs_pos < 0):
        abs_pos = abs_pos + 360
    return abs_pos

#absolute position goes like 0...179, -180, -179 = vals
#want 0...179, 180, 181,... 360 (then go back to 0)
#so return 360 + val
def medium_motor_print(port_num):
    print("medium motor", port_num)
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


"""
#code for getting port information in tuple form
#tuple = (1 if connected & recognized, port number, sensor_id)
execute_code = """
    port_info = [()] * 6
    for i in range(6):
        #for each port get the device Id
        current_port = i
        try:
            #below is line that will give you error (potentially)
            port_id = device.id(current_port) #this should be either 49, or 61 or 62 or... 65 #handle exception when not found
            # Call the corresponding function if the device ID is found
            if port_id in function_dict:
                #function_dict[port_id](i)
                port_info[i] = (1, i, port_id)
            else:
                #print(f"No function defined for device ID {port_id}")
                port_info[i] = (0,0,0)
        except OSError as e: #nothing connected to it
            # Means port does not have any sensor connected to it
            port_info[i] = (0,0,0)
            #print("YAA")
            #print(f"Port {current_port} error: {e}")
"""

#execute code for thisL 
# [(1, 0, 61), (0, 0, 0), (1, 2, 63), (1, 3, 48), (1, 4, 62), (1, 5, 64)]
#



# Function to handle user input event


def on_data_jav(chunk):
    #print("IN data_jav")
    #print("Start-chunk")
    print(chunk)
    #print("end-chunk")


    
def on_disconnect():
    connect.innerText = 'connect up'

def on_connect(event):
    if terminal.connected:
        connect.innerText = 'connect up'
        await terminal.board.disconnect()
    else:
        await terminal.board.connect('repl')
        document.getElementById('repl').style.display = 'none' #to prevent user from inputting during paste
        if terminal.connected:
            connect.innerText = 'disconnect'
        print("Before paste")
        #await terminal.paste(sensor_code, 'hidden')
        await terminal.paste(sensor_code, 'hidden')
        print("After paste")
        document.getElementById('repl').style.display = 'block' #allow user to input only after paste is done
        #terminal.terminal.attachCustomKeyEventHandler(on_user_input)
        #call sensor function

def display_repl(event):
    document.getElementById('repl').style.display = 'block'
    #terminal.setOption('disableStdin', True)  # Disable user input


#def on_user_input(event):
#    print("asdlkjfd;slkfj;l kjlk;sdjafl;kdsajf;l ksdjl;ksazjf")    


#sensor_info and get terminal in same button
def on_sensor_info(event):  
    global sensor
    global stop_loop
    #print("STOP-LOOP", stop_loop)

    stop_loop = False
    if sensor: #means you want to display sensors
        sensor = False #so that on next click it displays terminal
        #turn off repl to prevent user from interfering with my repl sensor code
        document.getElementById('repl').style.display = 'none'
        sensors.innerText = 'Get Terminal'
    #execute code for thisL 
    # [(1, 0, 61), (0, 0, 0), (1, 2, 63), (1, 3, 48), (1, 4, 62), (1, 5, 64)]
        #stop_loop = False
        # Add event listener for user input
        #event handler when user types in keyboard
        #counter = 0
        print("STOP-LOOP", stop_loop)
        while not stop_loop:
              #two lines below should go in while loop (checks every time the port info)
            await terminal.eval(execute_code, 'hidden')
            port_info_array = await terminal.eval("""port_info
                                """, 'hidden')
            #clearing it every time (very important)
            sensor_info_html = ""  # Initialize HTML content for sensor info
            #iterating over tuples/ports
            for t in port_info_array:
                if t[0] == 1: #if something is connected to port
                    #call corresponding funcitons with corresponding ports
                    #t[2] is function/device id & t[1] is port #
                    if stop_loop:
                        break;
                    #number is tuple with some sort of sensor value
                    #if anything but color sensor (just display 1 value)
                        #then 
                    number = await terminal.eval(f"""
                        number = function_dict[{t[2]}]({t[1]})
                        number
                        
                    """, 'hidden')
                    #if it is the color sensor process number as a tuple
                    #where tuple is (color from table 1, r, g , b)
                    if (t[2] == 61):
                        #print("SIUU")
                        #pass
                        color_info = number
                        color_detected = ["Red", "Green", "Blue", "Magenta", "Yellow", "Orange", "Azure", "Black", "White", "Unknown"]
                        color_name = color_detected[color_info[0] - 1] if 0 < color_info[0] <= len(color_detected) else "Unknown"
                        sensor_info_html += f"""
                            <div class="sensor-info-item">
                                <span>Number: {color_info} (Color: {color_name})</span>
                                <span>Device: {t[2]}</span>
                                <span>Port: {t[1]}</span>
                            </div>
                        """
                    else:
                        sensor_info_html += f"""
                            <div class="sensor-info-item">
                                <span>Number: {number}</span>
                                <span>Device: {t[2]}</span>
                                <span>Port: {t[1]}</span>
                            </div>
                        """
            # Update the sensor info container with new HTML content
            document.getElementById('sensor-info').innerHTML = sensor_info_html
            #await asyncio.sleep(0.3)
                        #print("NAHH")
                        #t is just 1 number (display that number)
                        
                    #now display number, device (t[2]), and port t[1]
                    #instead of returning #, return array of tuple
                    
            #print("Number:", number)
            #time.sleep(1)
            #counter = counter + 1
        #print("Back_HERE: ", port_info_array)
    else: #go back to terminal
        stop_loop = True
        #asyncio.
        #time.sleep_ms(1000) #to allow while loop to finish current iteration
        #await asyncio.sleep(0.1)
        sensor = True #so that next time it hides repls
        sensors.innerText = 'Sensor Readings'
        document.getElementById('repl').style.display = 'block'

        #this code is kind of important.
        #if the user spams the button, it prevents erros by disabling button for a short time
        #so that if multiple clicks are made quickly, the same while loop below the if
        #statement is not called twice
        #this would result on calling eval again when the first eval call has not yet 
        #finished. (resulting in error: can't eval 2 things at once)
        sensor_button = document.getElementById('sensor_readings')
        sensor_button.disabled = True
        await asyncio.sleep(0.2)  # Wait for 2 seconds
        sensor_button.disabled = False  # Re-enable the button
       # document.getElementById('sensor_readings').style.display = 'block'
    

async def on_load(event):
    if terminal.connected:
        github = path.value
        name = github.split('/')[-1]
        print('path, name: ',github,name)
        reply = await restapi.get(github)
        status = await terminal.download(name,reply)
        if not status: 
            window.alert(f"Failed to load {name}")  
    else:
        window.alert('connect to a processor first')

connect = document.getElementById('connect-spike')
download = document.getElementById('download-code')
path    = document.getElementById('gitpath')
sensors = document.getElementById('sensor_readings')
#get_repl = document.getElementById('get_repl')

connect.onclick = on_connect
download.onclick = on_load
sensors.onclick = on_sensor_info
#get_repl.onclick = display_repl

terminal = ampy.Ampy(SPIKE)
terminal.disconnect_callback = on_disconnect #defined for when physical or coded disconnection happens
#terminal.newData_callback = on_data_jav
