#Edited by: Javier Laveaga
#NOTE: if you do not want to check if the file was properly downloaded, calll download with 
# check = False (last parameter). This will speed up the download process 

#Purpose: To load the raw files provided as links (below) into the spike prime 
# (checks to see if files were correctly uploaded)
# Note: To edit which files to upload, go down to urls and edit dictionary accordingly

import myserial, ampy
import asyncio
from pyscript import window, document, display, when
import pyodide_http, json
pyodide_http.patch_all()
import requests

mycode = document.getElementById("codeToSend")
s = myserial.serial()
myserial.Terminal(s)
files = ampy.campy(s,'serialTerminal','status')
overlay = document.getElementById('background')
dialogBox = document.getElementById('dialog')
dialog_end = document.getElementById('success_message')
#jav
status_progress = document.getElementById('status')  # Get the progress bar element
status_text = document.getElementById('dialog_text')  # Get the status text element
#jav
async def connectIt(event):  # callback when they hit the connect button
    if not s.connected:
        await s.connect(event)
    else:
        window.alert('Processor not connected')
    
async def sendIt(event):  # callback when they hit the connect button
    if not s.connected:
        window.alert('Processor not connected')
        return
    code = mycode.value
    payload = '\x05' + code.replace('\n','\r\n') + '\x04'
    s.send(payload)
        
async def CtrlC(event):
    if s.connected:
        s.send('\x03')
        #javier testing code for quick check if it correctly uploaded
        #file_size_int, hash_int = await files.upload("Jav_test_other.py")
        #print("file_size_up: ", file_size_int)
        #print("Hash_up: ", hash_int)
        
        
        
    else:
        window.alert('Processor not connected')

async def Okbtn(event):
    dialog_end.style.display = 'none'
    overlay.style.display = 'none'
    

    
    
#midi fast by itself

#BLE_MIDI_url = 'https://raw.githubusercontent.com/chrisbuerginrogers/SPIKE_Prime/main/BLE/BLE_MIDI.py'
#urls = {'BLE_CEEO.py': BLE_CEEO_url}


#Jav_test_url = 'https://raw.githubusercontent.com/javier-la200426/CEEO/main/test_jav.py'
#jav_test_3 = 'https://raw.githubusercontent.com/javier-la200426/CEEO/main/jav_test_other.py'
#BLE_CEEO_url = 'https://raw.githubusercontent.com/chrisbuerginrogers/SPIKE_Prime/main/BLE/BLE_CEEO.py'
#urls = {'BLE_CEEO.py': BLE_CEEO_url, 'BLE_MIDI.py': BLE_MIDI_url }
Jav_test_other_url = 'https://raw.githubusercontent.com/javier-la200426/CEEO/main/jav_test_other.py'
urls = {'Jav_test_other.py': Jav_test_other_url}

def update_status(message):
    if status_text:
        status_text.innerHTML = f"<p>{message}</p>"  # Update status text
    if status_progress:
        status_progress.value += 25  # Example: Increment progress bar value

async def loadFile(event):
    if s.connected:
        failure = False #indicates whether or not All files loaded 
        print('SIMON')
        #the keys are BLE_CEEO.py and BLE_MIDI.py
        overlay.style.display = 'block'
        for key,url in urls.items():
            dialogBox.style.display = 'block'
            reply = requests.get(url) #fetch file content
            if reply.status_code == 200: #successful
                print('loading file')
                print(f'Loading file: {key}')
                file = reply.text #file content (correctly fetched)
                #dowloading the file into the robot
                status = await files.download(key,file) #status just checks sizes are equal
                if not status: #dowloaded file does not match uploaded file
                    window.alert(f"Failed to load {key}")  #uncommment this
                    print("HERE")
                    failure = True
                else:
                    print(status) #we want that to be true, indicating file properly downloaded
                    
                #s.send("Hello")
            else:
                failure = True
                window.alert('Failed to find the URL for MIDI files')
            dialogBox.style.display = 'none'
        if not failure: #if it succeeds
            dialog_end.style.display = 'block'
            #pass
        else: #if it fails
            overlay.style.display = 'none'
            pass
    else:
        window.alert('Processor not connected')

   
