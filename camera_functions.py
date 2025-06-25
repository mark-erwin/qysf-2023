import cv2
import os
import time
import sys

from multiprocessing import Process
import threading

import imutils
import shutil
import numpy as np
import easyocr
import assets
import data_functions

platecascade = assets.platecascade
minArea = 0
minsize = 0
allowlist = '0123456789'
violations = []

frameCacheName = 'frames/frame_cache/cache.jpg'
successFrameName = 'frames/detection_s/frame_'
failFrameName = 'frames/detection_f/frame_'

def scanPlate(scans):


    image = cv2.imread(frameCacheName)
    cv2.imshow("Output", image)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # convert to grayscale
    gray = cv2.bilateralFilter(gray, 11, 17, 17)  # Blur to reduce noise

    numberPlates = platecascade.detectMultiScale(gray, 1.05, 3)

    for (x, y, w, h) in numberPlates:
        area = w * h
        if area > minArea:

            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            Cropped = gray[y:y + h, x:x + w]

            reader = easyocr.Reader(['en'])
            result = reader.readtext(Cropped, allowlist=allowlist, min_size=minsize, mag_ratio=3)

            scanned = False

            for i in range(0, len(result)):
                if result[i][2] >= 0.7 and len(str(result[i][1])) >= 4:
                    plate = str(result[i][1])
                    confidence = str(format(result[i][2], '.2%'))
                    filename = successFrameName + str(format(scans, '03d')) + '.jpg'
                    text_result = (plate + ' - ' + confidence)

                    imgResult = cv2.putText(image, text_result, (30, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0),
                                            2)
                    print(text_result)

                    cv2.imwrite(filename, imgResult)
                    cv2.imshow("Result", imgResult)

                    data_functions.check_violation(plate, confidence, filename)

                    scanned = True
                    break

                if not scanned:
                    plate = str(result[i][1])
                    confidence = str(format(result[i][2], '.2%'))
                    filename = failFrameName + str(format(scans, '03d')) + '.jpg'
                    text_result = (plate + ' - ' + confidence)

                    imgResult = cv2.putText(image, text_result, (30, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0),2)

                    cv2.imwrite(filename, imgResult)

        else:
            print("No Number Plate")



cv2.waitKey(0)

cv2.destroyAllWindows()
