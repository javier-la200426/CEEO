
import my_globals
from pyscript import document, window
import my_gif
import time


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


def on_data_jav(chunk):
    # print("ON-DATA: ", chunk)
    
    # print("IN BUFFER", my_globals.javi_buffer)
    my_globals.javi_buffer = process_chunks(chunk)
    get_port_info(chunk)
    #print(my_globals.javi_sensor_buffer)





def get_port_info(chunk):
    
    my_globals.javi_sensor_buffer += chunk
    
    if not my_globals.found_port_info:
        #find port_info and delete uselss stuff if not found
        key_index = my_globals.javi_sensor_buffer.find("#**PORT_INFO_INCOMING**#")
        if key_index == -1: #if not found port_info
            last_newline_pos = my_globals.javi_sensor_buffer.rfind("\n")
            if last_newline_pos != -1: #if new line is foundm (which it shouuld be)
                my_globals.javi_sensor_buffer = my_globals.javi_sensor_buffer[last_newline_pos + 1:] #look for things after new line
        else:
            #I have found port_info (get stuff that is printed out right after)
            my_globals.found_port_info = True
            start_point = my_globals.javi_sensor_buffer.find("\n", key_index) #find new_line after port_info
            my_globals.javi_sensor_buffer = my_globals.javi_sensor_buffer[start_point + 1:] #start looking at key index (after port_info)
    else:
        #If found, get the port_info
        if my_globals.found_port_info:
            #retrieved_port_info +=
            end_new_line_index = my_globals.javi_sensor_buffer.find("\n", 0) #find next new line
            #if new line is found
            if end_new_line_index != -1: #if you find new line
                my_globals.count_new_after_found = my_globals.count_new_after_found + 1 #increase count
                if (my_globals.count_new_after_found == 2):
                    port_info_str = my_globals.javi_sensor_buffer[:end_new_line_index]
                    my_globals.port_info_jav_arr = convert_to_list(port_info_str)
                    #asyncio.sleep(1)
                    #print("MY-LIST: ", port_info_str)
                    #print("MY-LIST: ", port_info_list[0])

                    #print("PORT_INFO_JAV: ", port_info)
                    #print("Hello")
                    #print("Primera: ", port_info[0])
                    my_globals.found_port_info = False
                    my_globals.count_new_after_found = 0
                
                my_globals.javi_sensor_buffer = my_globals.javi_sensor_buffer[end_new_line_index + 1:] #clear buffer



                
            
def convert_to_list(port_info_str):
    # Strip the outer brackets
    stripped_str = port_info_str.strip("[]")
    
    # Initialize an empty list to store the result
    port_info_list = []
    
    # Split the string into individual segments representing elements
    segment_strs = stripped_str.split("), (")
    
    # Process each segment string
    for segment_str in segment_strs:
        # Remove leading and trailing parentheses and carriage returns
        cleaned_segment_str = segment_str.strip("() \r\n")
        
        # Split the string into individual elements
        elements = cleaned_segment_str.split(", ")
        
        # Append the list of elements to the result list
        port_info_list.append(elements)
    #print("ARRAY: ", port_info_list )
    return port_info_list

   #time.sleep(4)





    






#display custom code in editor, give delay on autoscroll function to ensure all new content has loaded
def print_custom_terminal(string):
    my_globals.custom_terminal_ele.innerHTML += string + " <br>"
    window.setTimeout(window.scrollTerminalToBottom, 0)


