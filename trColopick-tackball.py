#packages for the Colorpicker HSV
import urllib
import cv2
from win32api import GetSystemMetrics
import urllib.request
from PIL import Image
import colorsys

# import the necessary packages for the tracker
from collections import deque
import numpy as np
import argparse
import imutils

#arduinoCommunicate
import time
from time import sleep
import struct
import os
from serial import Serial

import threading

#json
import json
import yaml

#the [x, y] for each right-click event will be stored here => dit word niet gebruikt. Wij gaan de coordinaten direct gebruiken als er geclicked word
# right_clicks = list()

#variables arduino
arduinoPort = 'COM5' # USB port address for the Arduino
arduinoBaud = '115200' # Baud for serial communication
arduinoWaitTime = 3 # The length of time Python wait before attemping to issue commands to the Arduino
coordinates = ()
data = 0
AmountLeds = 144;
MaxX = 600;
MaxY = 450;
factor = MaxX/AmountLeds;

# camera
camera = cv2.VideoCapture(0)
#init arduino
ser = Serial(arduinoPort, arduinoBaud, timeout=0)

# image
# cv2.namedWindow('image', cv2.WINDOW_NORMAL)
# cv2.resizeWindow('image', window_width, window_height)
# TODO REMOVE het bovenstaande?

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

pts = deque(maxlen=args["buffer"])

def getValues() :
    global coordinates
    charCoordinates = json.dumps(coordinates)
    unicode_str = charCoordinates.encode('ascii')
    print(ser)
    ser.write(unicode_str)

    # arduinoData = ser.readline().decode("utf-8", "replace")
    # print (arduinoData)

def callback(value):
    pass

def setup_trackbars(range_filter):
    cv2.namedWindow("Trackbars", 0)

    for i in ["MIN", "MAX"]:
        v = 0 if i == "MIN" else 255

        for j in range_filter:
            cv2.createTrackbar("%s_%s" % (j, i), "Trackbars", v, 255, callback)

setup_trackbars('HSV')

def get_trackbar_values(range_filter):
    values = []

    for i in ["MIN", "MAX"]:
        for j in range_filter:
            v = cv2.getTrackbarPos("%s_%s" % (j, i), "Trackbars")
            values.append(v)

    return values

def set_trackbar_values(hmin, smin, vmin, hmax ,smax ,vmax , range_filter):
    values = [hmin, smin, vmin, hmax ,smax ,vmax]
    index = 0
    for i in ["MIN", "MAX"]:
        for j in range_filter:
            v = cv2.setTrackbarPos("%s_%s" % (j, i), "Trackbars", values[index])
            index += 1

def update_hsv_image(hsvImg , mouseClick, h, s, v):
    frame_to_thresh = cv2.cvtColor(hsvImg, cv2.COLOR_BGR2HSV)
    global greenLower
    global greenUpper
    if mouseClick:
        treshhold = 20
        hmin, smin, vmin, hmax, smax, vmax = h-treshhold, s-treshhold, v-treshhold, h+treshhold, s+treshhold, v+treshhold
        set_trackbar_values(hmin, smin, vmin, hmax, smax, vmax, 'HSV')
        thresh = cv2.inRange(frame_to_thresh, (hmin, smin, vmin), (hmax, smax, vmax))
        greenLower = (hmin, smin, vmin)
        greenUpper = (hmax, smax, vmax)
    else:
        v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values('HSV')
        thresh = cv2.inRange(frame_to_thresh, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))
        greenLower = (v1_min, v2_min, v3_min)
        greenUpper = (v1_max, v2_max, v3_max)
    cv2.imshow("Thresh", thresh )

#this function will be called whenever the mouse is right-clicked
def mouse_callback(event, x, y, flags, params):

    #right-click event value is 2
    if event == 2:
        # global right_clicks
        # right_clicks.append([x, y])

        #store the coordinates of the right-click event
        cv2_rgb = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        pil_im = Image.fromarray(cv2_rgb)
        # rgb_im = pil_im.convert('RGB')
        r, g, b = pil_im.getpixel((x,y))
        print('rgb(', r ,',', g,',', b,')')
        h,s,v = colorsys.rgb_to_hsv(r/255.,g/255.,b/255.)

        hdat = (int(h*255.))
        sdat = (int(s*255.))
        vdat = (int(v*255.))
        # h, s,v = colorsys.rgb_to_hsv(0.2, 0.4, 0.4)
        print('hsv(', hdat ,',', sdat,',', vdat,')')
        update_hsv_image(image, True, hdat, sdat, vdat)

while True:
    if 'greenLower' in globals():
        pass
    else:
		# You can set these HSV-min and HSV-max to the range you want to track when the script starts.
        greenLower = (22,0,234)
        greenUpper = (62,164,255)
        h,s,v = greenLower
        hm,sm,vm = greenUpper
        set_trackbar_values(h, s, v ,hm ,sm , vm, 'HSV')

    # Colorpicker
    ret, image  = camera.read()
    update_hsv_image(image, False, 0 ,0 ,0)
    cv2.setMouseCallback('image', mouse_callback)
    # cv2.imshow('image', image)

    # tracker
    # grab the current frame
    # (grabbed, frame)  = camera.read()
	# if we are viewing a video and we did not grab a frame,
	# then we have reached the end of the video
    if args.get("video") and not ret:
        break

	# resize the frame, blur it, and convert it to the HSV
	# color space
    # image = imutils.resize(image, width=600)

	# blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask

    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # cv2.imshow("mask", mask )
    # find contours in the mask and initialize the current
	# (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None

	# only proceed if at least one contour was found
    if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)

		# you can use this coordinates to do anything. it is the center of what you want to track F.E. send them to an arduino ;)
        coordinates = {"x":  round(x/factor) , "y":  round(y)}
		# print(coordinates)
        thr = threading.Thread(target=getValues, args=(), kwargs={})
        thr.start() # will run "foo"
        thr.is_alive() # will return whether foo is running currently
        thr.join() # will wait till "foo" is done
        # getValues(coordinates)

        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		# only proceed if the radius meets a minimum size
        if radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
            cv2.circle(image, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
            cv2.circle(image, center, 5, (0, 0, 255), -1)

	# update the points queue
    pts.appendleft(center)
	# loop over the set of tracked points
    for i in range(1, len(pts)):
		# if either of the tracked points are None, ignore
		# them
        if pts[i - 1] is None or pts[i] is None:
            continue

		# otherwise, compute the thickness of the line and
		# draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(image, pts[i - 1], pts[i], (0, 0, 255), thickness)

	# show the frame to our screen
    cv2.imshow("image", image)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("r"):
        ser.write(b'q')
        print('resetq')

    if cv2.waitKey(1) & 0xFF is ord('q'):
        camera.release()
        cv2.destroyAllWindows()
        break
