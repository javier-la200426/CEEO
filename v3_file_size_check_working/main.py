#Edited by: Javier Laveaga
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
#overlay = document.getElementById('background')
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
        
def CtrlC(event):
    if s.connected:
        s.send('\x03')
    else:
        window.alert('Processor not connected')

async def Okbtn(event):
    dialog_end.style.display = 'none'
    overlay.style.display = 'none'
    

    
    
#midi fast by itself

BLE_CEEO_url = 'https://raw.githubusercontent.com/chrisbuerginrogers/SPIKE_Prime/main/BLE/BLE_CEEO.py'
BLE_MIDI_url = 'https://raw.githubusercontent.com/chrisbuerginrogers/SPIKE_Prime/main/BLE/BLE_MIDI.py'
urls = {'BLE_CEEO.py': BLE_CEEO_url, 'BLE_MIDI_url': BLE_MIDI_url }


#Jav_test_url = 'https://raw.githubusercontent.com/javier-la200426/CEEO/main/test_jav.py'
#Jav_test_other_url = 'https://raw.githubusercontent.com/javier-la200426/CEEO/main/jav_test_other.py'
#jav_test_3 = 'https://raw.githubusercontent.com/javier-la200426/CEEO/main/jav_test_other.py'
#urls = {'test_jav.py': Jav_test_url}

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
        #overlay.style.display = 'block'
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
            #overlay.style.display = 'none'
            pass
    else:
        window.alert('Processor not connected')

   
