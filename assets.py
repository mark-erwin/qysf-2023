import cv2
import numpy as np

cam = cv2.VideoCapture(0)

platecascade = cv2.CascadeClassifier('assets/haarcascade_qatar_plate_number.xml')
registry = 'assets/registry.json'
cam_context = 'assets/camera_metadata.json'
