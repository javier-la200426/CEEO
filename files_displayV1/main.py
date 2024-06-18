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
        await files.List_files()
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
    else:
        window.alert('Processor not connected')


#async def List_files():
#    if s.connected:
#        pass
#        #call list_files function
#    else:
#        window.alert('Processor not connected')
    

def update_status(message):
    if status_text:
        status_text.innerHTML = f"<p>{message}</p>"  # Update status text
    if status_progress:
        status_progress.value += 25  # Example: Increment progress bar value

