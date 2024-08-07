#https://pyscript.com/@agiammarchi/spike-ide-copy/latest
#checking commit cover fix 

from pyscript import document
from pyscript.js_modules import file_library
import ampy
def init():
    #variables
    global sensor, stop_loop, ARDUINO_NANO, SPIKE, javi_buffer, found_key, physical_disconnect, proper_name_of_file, isRunning
    global current_gif_dictionary, lesson_num
    stop_loop = False #indicates when to stop loop (u want it to stop when user has access to repl)
    ARDUINO_NANO = 128
    SPIKE = 256
    javi_buffer = ""
    found_key = False
    current_gif_dictionary = {} 
    lesson_num = -1
    physical_disconnect = True
    isRunning = False

    proper_name_of_file = {
        1: "/flash/Main_Lesson1.py",
        2: "/flash/Main_Lesson2.py",
        3: "/flash/Main_Lesson3.py",
        4: "/flash/Main_Lesson4.py",
        5: "/flash/Main_Lesson5.py",
        6: "/flash/Main_Lesson6.py"
    }

    #elements
    global connect, download, path, sensors, custom_run_button, my_green_editor, file_list, progress_bar, custom_terminal_ele, percent_text, percent_div
    global save_btn, upload_file_btn, fileName, save_on_disconnect, yes_btn, no_btn
    save_btn = document.getElementById('save_button')
    connect = document.getElementById('connect-spike')
    download = document.getElementById('download-code')
    path    = document.getElementById('gitpath')
    sensors = document.getElementById('sensor_readings')
    custom_run_button = document.getElementById('custom-run-button')
    my_green_editor = document.getElementById('MPcode') #for editor
    progress_bar = document.getElementById('progress')
    #for list of files
    file_list = document.getElementById('files') #HEREE***
    custom_terminal_ele = document.getElementById('customTerminalMessage')
    percent_text = document.getElementById('progress-percent')
    percent_div = document.getElementById('progressDiv')
    upload_file_btn = document.getElementById('chooseFileButton')
    fileName = document.getElementById('fileRead') #not sure what fileName represents
    #nice_jav_button = document.getElementById('my-button-jav')
    save_on_disconnect = False
    yes_btn = document.getElementById('Yes-btn')
    no_btn = document.getElementById('No-btn')

    global found_port_info, javi_sensor_buffer, count_new_after_found, port_info_jav_arr
    #for sensor info
    found_port_info = False
    javi_sensor_buffer = ""
    count_new_after_found = 0 #newlines after founding it
    port_info_jav_arr = []

    

    #from pyscript.js_modules import file_library
    #JS-classes instances
    global saving_js_module
    saving_js_module = file_library.newFile()


  
    #terminal
    global terminal
    # terminal = ampy.Ampy(SPIKE, progress_bar)
    terminal = ampy.Ampy(SPIKE, progress_bar)