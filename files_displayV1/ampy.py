# https://github.com/scientifichackers/ampy/blob/master/ampy/files.py#L216
import myserial
import asyncio
import binascii, textwrap
from pyscript import document
from pyscript import window, display #display to be able to call dispplay
import os
import sys
import js # to use javascrip but it doesnt work
import json
#from pyscript import Canvas

BUFFER_SIZE = 512 #used to be 256 #depends on device (same with await asyncio.sleep)

#async def displayFiles(files):
    # This function is implemented in JavaScript in index.html
 #   window.displayFiles(files)


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
            self.serial.send(payload, eol = False) #sending payload
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
                hash = (hash * 31 + byte) % (2**99)
            return hash
        
        def hashfile(file):
            BUF_SIZE = {BUFFER_SIZE}
            with open(file, 'rb') as f:
                hash = 0
                while True:
                    data = f.read(BUF_SIZE)
                    if not data:
                        break
                    hash = (hash * 31 + simple_hash(data)) % (2**99)
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



    async def display_files_pyscript(self, files):
        # Create a new PostScript document
        canvas = Canvas()
    
        # Define initial coordinates for drawing
        x_start = 50
        y_start = 700
        line_height = 30  # Adjust as needed for spacing between lines
    
        # Set up fonts and other properties
        canvas.set_font("Helvetica", 12)
    
        # Header
        canvas.text(x_start, y_start, "Files Information", align="center")
    
        # Display each file's information
        y_position = y_start - line_height  # Start position for file entries
        for filename, info in files.items():
            y_position -= line_height  # Move to the next line
            canvas.text(x_start, y_position, f"File: {filename}")
            y_position -= line_height
            canvas.text(x_start, y_position, f"Size: {info[0]} bytes")
            y_position -= line_height
            canvas.text(x_start, y_position, f"Inode: {info[1]}")
            y_position -= line_height
            canvas.text(x_start, y_position, f"File Size: {info[2]}")
            y_position -= line_height  # Space between entries

    async def List_files(self):
        print("hola")
        #Send command over to microprocessor
        command_0 = """
            import os
            import sys
            #print each file and its information
            for i in os.ilistdir():
                #data is sparated by '>'
                print(i[0], end = '>') #filename
                print(i[1], end = '>') #directory is 16384 and file is 32768
                print(i[2], end = '>') #inode of file
                print(i[3], end = '>') #file size
        """

        await self.go_raw() #goes raw b/c it is about to talk to device
        try: 
            print('sending out request for file')
            await self.run_line(textwrap.dedent(command_0)) #sends command over
            print('file sent')
            #read output and store information in a dictionary 
            my_files = await self.store_file_info() #putting file info into dictionary
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
        #do something with the my_files dictionary (display this information)
        #await document.getElementById(displayFiles(my_files))
        print(my_files)
        #display(my_files)
        #javascript function cannot take in a python object (in this case a dictionary)
        #does we convert object to string usin json.
        #we pass string to javascript function
        await js.displayFiles(json.dumps(my_files))
    

    """
    Stores files and their info into a dictionary 

    Parameters:
    - None. Expects some serial output with the '>' character after each 
        data piece

    Returns:
    - A dictionary with the info in the file

    Behavior:
    - Iterates over all the files, storing each name, whether it is a directory,
        or file, the inode, and the file size

    Raises:
    - No exceptions are raised under normal circumstances.
    """
    async def store_file_info(self):
        #read output and store information in a dictionary 
        counter = 0
        current_key = ""
        my_files = {} #key is filename and value is a list with 3 things
        #3 things: directory or file, inode, and file size 
        while True:
            #print("1")
            data_piece = await self.read_until(1, '>', timeout = 50) # Reads output after executing command, which should be a number
            if (data_piece == ">"):
                print("EXITIING")
                break
            data_piece = data_piece[:-1] #getting rid of '>'
            #store file info here
            
            #store key 
            if (counter == 0):
                #store as key 
                current_key = data_piece
                my_files[current_key] = []
            else:
                my_files[current_key].append(data_piece)
                #append to current key 
            counter = counter + 1
            if (counter == 4):
                counter = 0 #get ready for next key 
            
            #print("New:", data_piece)
        return my_files
 
        
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
