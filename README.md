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
./start_remote_server
```
Run the client using:
```
python Camera_Client.py
```