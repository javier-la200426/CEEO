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
overlay = document.getElementById('background')
dialogBox = document.getElementById('dialog')
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

BLE_CEEO_url = 'https://raw.githubusercontent.com/chrisbuerginrogers/SPIKE_Prime/main/BLE/BLE_CEEO.py'
BLE_MIDI_url = 'https://raw.githubusercontent.com/chrisbuerginrogers/SPIKE_Prime/main/BLE/BLE_MIDI.py'
urls = {'BLE_CEEO.py': BLE_CEEO_url, 'BLE_MIDI.py': BLE_MIDI_url}
#Jav_test_url = 'https://raw.githubusercontent.com/javier-la200426/CEEO/main/test_jav.py'
#urls = {'test_jav.py': Jav_test_url}

async def loadFile(event):
    print('HERRRE')
    print('HERRRE')
    print('HERRRE')
    

    
    if s.connected:
        print('SIMON')
        overlay.style.display = 'block'
        dialogBox.style.display = 'block'
        #the keys are BLE_CEEO.py and BLE_MIDI.py
        for key,url in urls.items():
            reply = requests.get(url) #fetch file content
            if reply.status_code == 200: #successful
                print('loading file')
                print(f'Loading file: {key}')
                file = reply.text #file content (correctly fetched)
                #print(f'File content for {key}:')
                #print(file)
                #dowloading the file into the robot
                
                status,payload = await files.download(key,file)
                if not status:
                    window.alert(f"Failed to load {key}")
                
                #print("AQUIIII")
                #print("AQUIIII")
                #print("AQUIIII")
                #true status indicates that the original file we 
                #wanted to download to chip is the same as the file that is actually 
                #on chip (uploading: retrieving file from chip )
                print(status) #we want that to be true
            else:
                window.alert('Failed to find the URL for MIDI files')
        overlay.style.display = 'none'
        dialogBox.style.display = 'none'
    else:
        window.alert('Processor not connected')

