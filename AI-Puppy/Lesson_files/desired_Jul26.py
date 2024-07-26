
import my_globals
from pyscript import document, window
import my_gif

#display custom code in editor, give delay on autoscroll function to ensure all new content has loaded
def print_custom_terminal(string):
    document.getElementById('customTerminalMessage').innerHTML += string + " <br>"
    window.setTimeout(window.scrollTerminalToBottom, 0)

##**END-CODE**# sfjflk \n
#(this is when find_print_statemetns should be called)1st print \n
def find_print_statements(buffer):
    statements = []
    start_index = 0
    while start_index < len(buffer):
        end_new_line_index = buffer.find("\n", start_index)
        if end_new_line_index == -1:
            break
        statement = buffer[start_index:end_new_line_index]
        statements.append(statement)
        start_index = end_new_line_index + 1
    return statements

def process_chunks(chunk):
    my_globals.javi_buffer += chunk
    #print("BUFFER:",javi_buffer)
    
    if not my_globals.found_key:
        key_index = my_globals.javi_buffer.find("#**END-CODE**#")
        if key_index == -1: #if not found
            last_newline_pos = my_globals.javi_buffer.rfind("\n")
            if last_newline_pos != -1: #if new line is found
                my_globals.javi_buffer = my_globals.javi_buffer[last_newline_pos + 1:] #look for things after new line
        else:
            print("FOUND)")
            my_globals.found_key = True
            start_point = my_globals.javi_buffer.find("\n", key_index)
            my_globals.javi_buffer = my_globals.javi_buffer[start_point + 1:] #start at key index
    
    if my_globals.found_key:
        print_statements = find_print_statements(my_globals.javi_buffer)
        if print_statements:
            for statement in print_statements:
                #print(f"Extracted print statement: {statement.strip()}")
                print_statement = statement.strip()
                #print("SISENOR: ", print_statement)
                print_custom_terminal(print_statement) #print to print terminal

                #add custom repsonses on error here!
                if print_statement.find("OSError:") != -1:
                    print_custom_terminal("Make sure your devices are plugged into the proper ports!")

                my_gif.get_gif(my_globals.current_gif_dictionary, print_statement)

            
            last_newline_pos = my_globals.javi_buffer.rfind("\n")
            if last_newline_pos != -1:
                my_globals.javi_buffer = my_globals.javi_buffer[last_newline_pos + 1:]
    
    return my_globals.javi_buffer

found_port_info = False
#retrieved_port_info = ""
javi_sensor_buffer = ""

def on_data_jav(chunk):
    global javi_sensor_buffer
    # print("ON-DATA: ", chunk)
    
    # print("IN BUFFER", my_globals.javi_buffer)
    my_globals.javi_buffer = process_chunks(chunk)
    javi_sensor_buffer = get_port_info(chunk)
    #print(javi_sensor_buffer)





def get_port_info(chunk):
    
    global found_port_info, javi_sensor_buffer
    javi_sensor_buffer += chunk
    
    if not found_port_info:
        #find port_info and delete uselss stuff if not found
        key_index = javi_sensor_buffer.find("port_info")
        if key_index == -1: #if not found port_info
            last_newline_pos = javi_sensor_buffer.rfind("\n")
            if last_newline_pos != -1: #if new line is foundm (which it shouuld be)
                javi_sensor_buffer = javi_sensor_buffer[last_newline_pos + 1:] #look for things after new line
        else:
            #I have found port_info (get stuff that is printed out right after)
            found_port_info = True
            start_point = javi_sensor_buffer.find("\n", key_index) #find new_line after port_info
            javi_sensor_buffer = javi_sensor_buffer[start_point + 1:] #start looking at key index (after port_info)
    else:
        #If found, get the port_info
        if found_port_info:
            #retrieved_port_info +=
            end_new_line_index = javi_sensor_buffer.find("\n") #find next new line
            if end_new_line_index == -1:
                print("port_info_not_found")
            else:
                port_info = javi_sensor_buffer[:end_new_line_index]
                print("PORT_INFO_JAV: ", port_info)
                found_port_info = False
                my_globals.javi_buffer = my_globals.javi_buffer[end_new_line_index + 1:] #reset buffer
            

    
    return javi_sensor_buffer





#display custom code in editor, give delay on autoscroll function to ensure all new content has loaded
def print_custom_terminal(string):
    my_globals.custom_terminal_ele.innerHTML += string + " <br>"
    window.setTimeout(window.scrollTerminalToBottom, 0)


execute_code = """
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

#**PORT_INFO_INCOMING**#
port_info


"""

