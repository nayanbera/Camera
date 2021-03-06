# run this program on each RPi to send a labelled image stream
import socket
import time
import imagezmq
import cv2
import sys

ip=sys.argv[1]

sender = imagezmq.ImageSender(connect_to='tcp://'+ip+':5555')
#sender = imagezmq.ImageSender(connect_to='tcp://*:5555',REQ_REP=False)
rpi_name = socket.gethostname() # send RPi hostname with each image
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
print('Connected successfully to %s(%s)'%(rpi_name, ip))
print('Waiting for the response from %s'%rpi_name)
while True:  # send images as stream until Ctrl-C
    ret, image = cam.read()
    reply=sender.send_image(rpi_name, image)
    print(reply)