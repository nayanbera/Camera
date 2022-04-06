# Camera Server-Client using imageZMQ

Installation
------------
Install the software in both the home directory of Pi server computer through github:
```
git install https://github.com/nayanbera/Camera.git
```
Install the same software in the client computer using the same command.

Running
-------
Change the path within the bin/start_camserver file, if necessary

Make the start_remote_server executable by running this command:
```
chmod a+x start_remote_server
```
First start the remote server through the client machine using:
```
./start_remote_server username@server_ip_OR_hostname client_ip
```
For example, running a usb camera with raspberry Pi computer run the following to start 
the remote server from your client computer as
```
./start_remote_server pi@chemmat-pi106 164.54.162.64
```
Run the client using:
```
python Camera_Client.py
```