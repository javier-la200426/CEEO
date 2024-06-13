# https://github.com/scientifichackers/ampy/blob/master/ampy/files.py#L216
import myserial
import asyncio
import binascii, textwrap
from pyscript import document

BUFFER_SIZE = 256 #depends on device (same with await asyncio.sleep)

class SerialError(BaseException):
    pass

class campy():
    def __init__(self, serial, terminal_name = 'serialTerminal', status_name = 'status', verbose = False):
        self.serial = serial
        self.verbose = verbose
        self.view = document.getElementById(terminal_name)
        self.status = document.getElementById(status_name)
        self.old = 0

    def printIt(self, payload):
        if self.verbose:
            print(payload)

    def flush(self):
        self.old = len(self.view.innerText)

    def is_any(self):
        return len(self.view.innerText) - self.old

    def readIt(self,min_len):
        if len(self.view.innerText)-self.old >= min_len:
            new = (self.view.innerText[self.old:self.old+min_len])
            self.old = self.old + min_len
            return new
        return ''

    async def read_until(self, min_len, ending, timeout = 1):
        data = self.readIt(min_len)
        timeout_count = 0
        while True:
            #print(ending) #ending is OK
            if data.endswith(ending):
                #self.printIt(data) #prints bunch of numbers
                #print("YAYYAAYAYAAYAYA")
                break
            elif self.is_any() > 0:
                new_data = self.readIt(1)
                #if ending == '>': #only for uploading call
                   # print("ARRIBA ESP")
                   # print(f"Read new data: {new_data}")
                data = data + new_data
                #print(f"Current data: {data}")
                timeout_count = 0
            else:
                timeout_count += 1
                if timeout is not None and timeout_count >= 10 * timeout: #used to be 100 *
                    self.printIt('timeout')
                    #self.printIt(ending)
                    #self.printIt(data) #not ending with OK
                    break
                
                await asyncio.sleep(0.01)     
        return data


    async def send_get(self, payload, expected, tries = 1):
        for retry in range(0, tries): 
            self.serial.send(payload, eol = False) 
            #self.printIt(f'Sent: {repr(payload)} (Try: {retry+1}/{tries})')
            #self.printIt('Sent:'+str(payload))
            
            data = await self.read_until(1, expected)
           # print(expected) prints OK
            #print("YAAAAGAHAH")
            #self.printIt(f'Received: {repr(data)}')
    
            if data.endswith(expected):
                #self.printIt(f'Success: Read {repr(data)}')
                #self.printIt('Read: ' + repr(data))
                return True
        raise SerialError('no raw mode')
    #writes data to the file
    async def run_line(self, command):
        for i in range(0, len(command), 256):
            self.serial.send(command[i:min(i + 256, len(command))],eol=False)
            await asyncio.sleep(0)
        print('done writing')
        await self.send_get('\x04','OK',1) #**Changed this from 1 to 2. Worksishfor Alvek
                    
    async def go_raw(self):
        self.serial.send('\r\x03', eol = False)
        await asyncio.sleep(0.1)
        self.serial.send('\x03', eol = False)
        await asyncio.sleep(0.1)
        self.flush()

        await self.send_get('\r\x01', 'raw REPL; CTRL-B to exit\n>', 5)
        print('in raw')
        await self.send_get('\x04', 'soft reboot\n', 1)
        print('rebooted')
        await asyncio.sleep(0.5)
        self.serial.send('\x03', eol=False)
        await asyncio.sleep(0.1)
        await self.send_get('\x03', 'raw REPL; CTRL-B to exit\n', 1)

    def close_raw(self):
        self.serial.send('\r\x02', eol=False) # ctrl-B: enter friendly REPL
        
    async def send_code(self, filename, data):
        await self.run_line("f = open('%s', 'wb')"%(filename))
        size = len(data)
        # Loop through and write a buffer size chunk of data at a time.
        dt = 90*BUFFER_SIZE/size
        print('delta t')
        print(dt)
        for i in range(0, size, BUFFER_SIZE):
            chunk_size = min(BUFFER_SIZE, size - i)
            chunk = repr(data[i : i + chunk_size])
            #print(f"Sending chunk: {chunk}")
            await self.run_line("f.write(%s)"%(chunk)) 
            self.status.value += dt
        await self.run_line("f.close()")

    async def download(self, filename, data, check = True):
        og_file_size = len(data.encode()) #original file size
        print("Original_file_size: ", og_file_size)
        #exit(1)
        self.status.value = 5
        start = len(self.view.innerText)
        await self.go_raw()
        #print("SUMMAMA") #gets here
        
        self.status.value = 10
        #send code to processor
        await self.send_code(filename, data) #problem is here (for Alvik)
        self.close_raw()
        print('downloaded')
        if check:
            #check sizes are the same
            file_size_int =  await self.upload(filename)
            print("in_payload_line")
            #print(payload) 
            print("data_encode:")
            print(data.encode())
            return (og_file_size == file_size_int)
        else:
            return True      

    #upload is 
    async def upload(self, filename):
        file_size_int = 0
        command = """
        import os
        for i in os.ilistdir():
            if(i[0] == '%s'): #gets name of file that was uploaded
                print(i[3]) #gets file size
        """%(filename) 
        await self.go_raw() #goes raw b/c it is about to talk to device
        try: 
            print('sending out request for file')
            await self.run_line(textwrap.dedent(command)) #sends command over
            print('file sent')
            out_str = await self.read_until(1, '>') # Reads output after executing command, which should be a number
            print("AFTER OUT")
            print('got it')
        except SerialError as ex:
            # Check if this is an OSError #2, i.e. file doesn't exist and
            # rethrow it as something more descriptive.
            try:
                message = ex.args[2].decode("utf-8")
                if message.find("OSError") != -1 and message.find("2") != -1:
                    raise RuntimeError("No such file: {0}".format(filename))
                else:
                    raise ex
            except UnicodeDecodeError:
                raise ex
        self.close_raw()
        out_str = out_str[:-1] #gets rid of arrow > in output (the file size)
        try:
            file_size_int = int(out_str)
            print(file_size_int)
            print("here")
        except ValueError:
            print(f"{out_str} is not a valid integer.")

        

        #exit(0)
        #print(binascii.unhexlify(out_str))
        return file_size_int #this is the file size of file that is in device
