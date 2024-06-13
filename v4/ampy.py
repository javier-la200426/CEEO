# https://github.com/scientifichackers/ampy/blob/master/ampy/files.py#L216
import myserial
import asyncio
import binascii, textwrap
from pyscript import document
from pyscript import window
import os
import sys

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
                    window.alert('Timeout in read_until')
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

#chunk is acting like data in the other command2

    """
    Computes a hash value for a chunk of text.

    Parameters:
    - chunk: A string representing a chunk of text.

    Returns:
    - An integer representing the computed hash value.

    Behavior:
    - Converts the input chunk into bytes using UTF-8 encoding.
    - Iterates over each byte in the chunk and computes a hash value using the formula
      (hash_value * 31 + byte) % (2**32).
    - Returns the computed hash value as an integer.

    Raises:
    - No exceptions are raised under normal circumstances.
    """
    async def simple_hash_3(self, chunk):
        hash_value = 0
        for byte in chunk:
            hash_value = (hash_value * 31 + byte) % (2**32)
        return hash_value

    """
    Computes a cumulative hash value for all text data.

    Parameters:
    - all_text: A string containing the entire text data to be hashed.

    Returns:
    - An integer representing the computed hash value for all_text.

    Behavior:
    - Converts the entire all_text string into bytes using UTF-8 encoding.
    - Iterates over the bytes in chunks of BUFFER_SIZE.
    - For each chunk, computes a hash value using await self.simple_hash_3(chunk).
    - Accumulates the hash value using the formula (hash_value * 31 + await self.simple_hash_3(chunk)) % (2**32).
    - Returns the final computed hash value as an integer.

    Raises:
    - No exceptions are raised under normal circumstances.
    """
    async def hashfile(self, all_text):
        bytes_data = all_text.encode('utf-8')
        hash_value = 0
        
        for chunk_start in range(0, len(bytes_data), BUFFER_SIZE):
            chunk_end = min(chunk_start + BUFFER_SIZE, len(bytes_data))
            chunk = bytes_data[chunk_start:chunk_end]
            hash_value = (hash_value * 31 + await self.simple_hash_3(chunk)) % (2**32)
        
        return hash_value

    async def download(self, filename, data, check = True):
        
        og_file_size = len(data.encode()) #original file size
        print("Original_file_size: ", og_file_size)

        #getting hash string for original file
        og_hash = await self.hashfile(data)
        print("IN DOWNLOAD HASH")
        print(og_hash)

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
            file_size_int, hash_upload =  await self.upload(filename)
            print("upload_file_size: ", file_size_int)
            print("upload_hash_str: ", hash_upload )
            
            #print("in_payload_line")
            #print(payload) 
            #print("data_encode:")
            #print(data.encode())
            return ((og_file_size == file_size_int) & (og_hash == hash_upload)) #modify this
        else:
            return True    


    #Sends a command to processor, and returns an output
    async def send_command(self, command):
        await self.go_raw() #goes raw b/c it is about to talk to device
        try: 
            print('sending out request for file')
            await self.run_line(textwrap.dedent(command)) #sends command over
            print('file sent')
            #needs more time here because for command_2 it takes some time to read in 
            #10 worked as well
            out_str = await self.read_until(1, '>', timeout = 50) # Reads output after executing command, which should be a number
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
        return out_str

    
    #upload is 
    async def upload(self, filename):

        #getting file size
        file_size_int = 0 #initializing so that it can be accessed outside of scope
        command_1 = """
        import os
        import sys
        for i in os.ilistdir():
            if(i[0] == '%s'): #gets name of file that was uploaded
                print(i[3]) #gets file size
        """%(filename) 

        out_str = await self.send_command(command_1) #file_size
        out_str = out_str[:-1] #gets rid of arrow > in output (the file size)
        try:
            file_size_int = int(out_str)
            print(file_size_int)
            print("here")
        except ValueError:
            print(f"{out_str} is not a valid integer.")
            window.alert('Could not obtain file size')

        #getting hash version of data
        command_2 = f"""
        import os
        import sys
        
        def simple_hash(data): #2
            hash = 0
            for byte in data:
                hash = (hash * 31 + byte) % (2**32)
            return hash
        
        def hashfile(file):
            BUF_SIZE = {BUFFER_SIZE}
            with open(file, 'rb') as f:
                hash = 0
                while True:
                    data = f.read(BUF_SIZE)
                    if not data:
                        break
                    hash = (hash * 31 + simple_hash(data)) % (2**32)
            return hash
        
        hash_str = hashfile('{filename}')
        print(hash_str)
        """

        out_str2 = await self.send_command(command_2) #hash_thing
        out_str2 = out_str2[:-1] #gets rid of arrow > in output (the file size)
        print("alsdjk;jasfl;kdsj", out_str2)
        #exit(1)
        try:
            hash_int = int(out_str2)
            print('Hash:', hash_int)
            #exit(1)
            print("here")
        except ValueError:
            print(f"{out_str2} is not a valid hash string.")
            window.alert('Could not obtain hash string')
        #exit(0)
        #print(binascii.unhexlify(out_str))
        return file_size_int, hash_int  #this is the file size of file that is in device
 
        
'''

command = """
        import os
        import sys
        import hashlib
        
        def hashfile(file):
        	BUF_SIZE = '%d'
        	sha256 = hashlib.sha256()
        	with open(file, 'rb') as f:
        		while True:
        			data = f.read(BUF_SIZE)
        			if not data:
        				break
        			sha256.update(data)
        	return sha256.hexdigest()
        hash_str = hashfile('%s')
        print(hash_str)
        
    

        
        for i in os.ilistdir():
            if(i[0] == '%s'): #gets name of file that was uploaded
                print(i[3]) #gets file size
        """%(filename, BUFFER_SIZE) 


'''

'''

import sys
import hashlib


def hashfile(file):

	# A arbitrary (but fixed) buffer 
	# size (change accordingly)
	# 65536 = 65536 bytes = 64 kilobytes 
	BUF_SIZE = 65536

	# Initializing the sha256() method
	sha256 = hashlib.sha256()

	# Opening the file provided as
	# the first commandline argument
	with open(file, 'rb') as f:
		
		while True:
			
			# reading data = BUF_SIZE from
			# the file and saving it in a
			# variable
			data = f.read(BUF_SIZE)

			# True if eof = 1
			if not data:
				break
	
			# Passing that data to that sh256 hash
			# function (updating the function with
			# that data)
			sha256.update(data)

	
	# sha256.hexdigest() hashes all the input
	# data passed to the sha256() via sha256.update()
	# Acts as a finalize method, after which
	# all the input data gets hashed hexdigest()
	# hashes the data, and returns the output
	# in hexadecimal format
	return sha256.hexdigest()

# Calling hashfile() function to obtain hashes
# of the files, and saving the result
# in a variable
f1_hash = hashfile(sys.argv[1])
f2_hash = hashfile(sys.argv[2])

# Doing primitive string comparison to 
# check whether the two hashes match or not
if f1_hash == f2_hash:
	print("Both files are same")
	print(f"Hash: {f1_hash}")

else:
	print("Files are different!")
	print(f"Hash of File 1: {f1_hash}")
	print(f"Hash of File 2: {f2_hash}")



'''
