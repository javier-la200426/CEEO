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

stop_loop = False

#defining functions to paste into spike
sensor_code = """

import device
import motor

def big_motor_print(port_num):
    print("big_motor", port_num)
    return 1 #change this
    
def color_sensor_print(port_num):
    print("color sensor", port_num)
    return 1 #change this
    
def distance_sensor_print(port_num):
    print("distance sensor", port_num)
    return 1 #change this
    
def force_sensor_print(port_num):
    print("force sensor", port_num)
    return 1 #change this
    
def light_matrix_print(port_num):
    print("light matrix", port_num)
    return 1 #change this
    
def small_motor_print(port_num):
    print("small motor", port_num)
    return 1 #change this
    
def medium_motor_print(port_num):
    print("medium motor", port_num)
    return motor.relative_position(port_num)

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
        if terminal.connected:
            connect.innerText = 'disconnect'
        print("Before paste")
        #await terminal.paste(sensor_code, 'hidden')
        await terminal.paste(sensor_code, 'hidden')
        print("After paste")

        #call sensor function

def on_sensor_info(event):  

    #turn off repl to prevent user from interfering with my repl sensor code
    document.getElementById('repl').style.display = 'none'

    
    #two lines below should go in while loop (checks every time the port info)
    await terminal.eval(execute_code, 'hidden')
    port_info_array = await terminal.eval("""port_info
                        """, 'hidden')
#execute code for thisL 
# [(1, 0, 61), (0, 0, 0), (1, 2, 63), (1, 3, 48), (1, 4, 62), (1, 5, 64)]

    stop_loop = False
    # Add event listener for user input
    #event handler when user types in keyboard
    counter = 0
    while counter != 3 and not stop_loop:
        #iterating over tuples/ports
        for t in port_info_array:
            if t[0] == 1: #if something is connected to port
                #call corresponding funcitons with corresponding ports
                #t[2] is function/device id & t[1] is port #
                if stop_loop:
                    break;
                number = await terminal.eval(f"""
                    number = function_dict[{t[2]}]({t[1]})
                    number
                    
                """, 'hidden')

                #now display number, device (t[2]), and port t[1]
                #instead of returning #, return array of tuple
                
                print(number)
        time.sleep(1)
        counter = counter + 1
    print("Back_HERE: ", port_info_array)
    #terminal.buffer = "welkfjhwelkfjw"
    #jav (starting sensor readings)
   # good_code = sensor_code.replace('\n', '\r\n')
    #print("HERE")
    #await terminal.board.eval(sensor_code, hidden=False)
   # await terminal.send_get(sensor_code, '>>>', 5, 100)
                
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

connect.onclick = on_connect
download.onclick = on_load
sensors.onclick = on_sensor_info

terminal = ampy.Ampy(SPIKE)
terminal.disconnect_callback = on_disconnect #defined for when physical or coded disconnection happens
#terminal.newData_callback = on_data_jav
