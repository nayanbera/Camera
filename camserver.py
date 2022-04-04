# run this program on each RPi to send a labelled image stream
import socket
import time
import imagezmq
import cv2

sender = imagezmq.ImageSender(connect_to='tcp://164.54.162.64:5555')
#sender = imagezmq.ImageSender(connect_to='tcp://*:5555',REQ_REP=False)
rpi_name = socket.gethostname() # send RPi hostname with each image
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
while True:  # send images as stream until Ctrl-C
    ret, image = cam.read()
    reply=sender.send_image(rpi_name, image)
    print(reply)