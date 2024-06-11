# https://github.com/scientifichackers/ampy/blob/master/ampy/files.py#L216
import myserial
import asyncio
import binascii, textwrap
from pyscript import document

BUFFER_SIZE = 256

class SerialError(BaseException):
    pass

class campy():
    def __init__(self, serial, terminal_name = 'serialTerminal', status_name = 'status', verbose = True):
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
                print("ALLOOOOOOOO")
                self.printIt(data)
                break
            elif self.is_any() > 0:
                new_data = self.readIt(1)
                data = data + new_data
                timeout_count = 0
            else:
                timeout_count += 1
                if timeout is not None and timeout_count >= 10 * timeout: #used to be 100 *
                    self.printIt('timeout')
                    self.printIt(ending)
                    self.printIt(data) #not ending with OK
                    break
                await asyncio.sleep(0.01)
        return data

    async def send_get(self, payload, expected, tries = 1):
        for retry in range(0, tries): 
            self.serial.send(payload, eol = False) 
            #Javi
            self.printIt(f'Sent: {repr(payload)} (Try: {retry+1}/{tries})')
            self.printIt('Sent:'+str(payload))
            data = await self.read_until(1, expected)
            self.printIt(f'Received: {repr(data)}')
    
            if data.endswith(expected):
                self.printIt(f'Success: Read {repr(data)}')
                self.printIt('Read: ' + repr(data))
                return True
        raise SerialError('no raw mode')
    #writes data to the file
    async def run_line(self, command):
        for i in range(0, len(command), 256):
            self.serial.send(command[i:min(i + 256, len(command))],eol=False)
            await asyncio.sleep(0)
        print('done writing')
        await self.send_get('\x04','OK',2) #**Changed this to 2 this is doing error
                    
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
            #Jav print("call_num:",i,'\n')
            print(f"Sending chunk: {chunk}")
            await self.run_line("f.write(%s)"%(chunk)) #0th iteration causes error
            self.status.value += dt
        await self.run_line("f.close()")

    async def download(self, filename, data, check = True):
        self.status.value = 5
        start = len(self.view.innerText)
        await self.go_raw()
        print("SUMMAMA") #gets here
        
        self.status.value = 10
        #send code to processor
        await self.send_code(filename, data) #problem is here.
        print("AAHAHAHAHAHAahdsfhdsfhH")
        self.close_raw()
        print('downloaded')
        if check:
            payload =  await self.upload(filename)
            return (data.encode() == payload), payload
        else:
            return True, None      
        
    async def upload(self, filename):
        command = """
        import sys
        import ubinascii
        with open('%s', 'rb') as infile:
            while True:
                result = infile.read(%d)
                if result == b'':
                    break
                len = sys.stdout.write(ubinascii.hexlify(result))
        """ % (filename, BUFFER_SIZE)
        await self.go_raw()
        try:
            print('sending out request for file')
            await self.run_line(textwrap.dedent(command))
            print('file sent')
            out = await self.read_until(1, '>')
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
        out = out[:-1]
        return binascii.unhexlify(out)
