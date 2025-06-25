import cv2
import os
import time
import sys

from multiprocessing import Process
import threading

import imutils
import shutil
import numpy as np
import assets
import camera_functions
import data_functions
from datetime import datetime

print("Hello World")

if os.path.exists('frame_cache'):
    shutil.rmtree('./frame_cache')
elif not os.path.exists('frame_cache'):
    os.makedirs('frame_cache')

if not os.path.exists('frame_cache'):
    os.makedirs('frame_cache')

if not os.path.exists('frame_video'):
    os.makedirs('frame_video')

if not os.path.exists('detection_s'):
    os.makedirs('detection_s')
    data_functions.new_json()

if not os.path.exists('detection_f'):
    os.makedirs('detection_f')

cam = assets.cam

currentFrame = 1
totalFrames = len(os.listdir('./frame_video'))
sequence = 1

##User Declared:
fpsLimit = 5
shotLimit = 1
waitTime = 0

print("Program Initialized")

while True:

    now = datetime.now()
    dtime = now.strftime("%H:%M:%S")
    ddate = now.strftime("%d/%m/%Y")

    if currentFrame == 1 and sequence >= shotLimit + 1:
        key = cv2.waitKey(1) & 0xFF
        ret, img = cam.read()

        sequence = 1

        cv2.imwrite('./frame_cache/frame_' + str(format(sequence, '03d')) + '.jpg', img)

        image = cv2.putText(img, dtime + " " + ddate, (420, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        cv2.imwrite('./frame_video/frame_' + str(format(totalFrames, '03d')) + '.jpg', image)

        cv2.imshow('Output', image)

        camera_functions.scanPlate(totalFrames)

        currentFrame += 1
        totalFrames += 1
        time.sleep(waitTime)

    elif currentFrame == 1:
        key = cv2.waitKey(1) & 0xFF
        ret, img = cam.read()

        cv2.imwrite('./frame_cache/frame_' + str(format(sequence, '03d')) + '.jpg', img)

        image = cv2.putText(img, dtime + " " + ddate, (420, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        cv2.imwrite('./frame_video/frame_' + str(format(totalFrames, '03d')) + '.jpg', image)

        cv2.imshow('Output', image)

        currentFrame += 1
        time.sleep(waitTime)

    elif 1 < currentFrame <= fpsLimit - 1:

        key = cv2.waitKey(1) & 0xFF
        ret, img = cam.read()

        cv2.imshow('Output', image)
        currentFrame += 1
        time.sleep(waitTime)

    elif currentFrame > fpsLimit - 1 and sequence <= shotLimit:

        key = cv2.waitKey(1) & 0xFF
        ret, img = cam.read()

        cv2.imshow('Output', image)
        currentFrame = 1
        sequence += 1
        time.sleep(waitTime)
