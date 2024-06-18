#Edited by: Javier Laveaga
#NOTE: If any filename has the character '>' in it, the program will not
# work. So, do not have files with '>' in them. 
# The reason this happens is because the character '>' is used to 
# separate the filename, type, and size (used a as a separator)
# in command_0 under List_files
# Note also that the way I am reading info from the processor is by  
# outputting information. (Thus this requires outputting a separator to separate data)

#Alternative; change the SEPARATOR in ampy.py to some other weird character 
# will have timeout
import myserial, ampy
import asyncio
from pyscript import window, document, display, when
import pyodide_http, json
pyodide_http.patch_all()
import requests
from pyodide.ffi import create_proxy #so that my unused functions in python don't get deleted
import js
#so that I can use them in js

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

#Defines what to do after clicking a file
def fileClicked(filename):
    print("Yaa", filename)
    
async def connectIt(event):  # callback when they hit the connect button
    if not s.connected:
        await s.connect(event)
        await files.List_files()
        
        #get ready for opening files 
        #this enables js to call this function
        js.createObject(create_proxy(fileClicked), "fileClicked_js") #converting function to js function
        #create proxy used here so that fileClicked function is not destroyed. (unused functions in python get deleted)
        
        
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

