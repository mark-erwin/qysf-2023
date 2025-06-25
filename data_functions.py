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
import json
from datetime import datetime
import email_functions


file = 'frames/detection_s/data.json'

registry = assets.registry
cam_context = assets.cam_context

plate = {"plates": []}

def new_json():
    with open(file, 'w') as json_file:
        json.dump(plate, json_file, indent=4)

def write_json(new_data):
    with open(file,'r+') as json_file:
        file_data = json.load(json_file)
        file_data["plates"].append(new_data)
        json_file.seek(0)
        json.dump(file_data, json_file, indent = 4)

def write_result(i, confidence, filename, violation, loc, ddate, dtime):
    
    with open(cam_context, "r") as cam_file:
        cam = json.load(cam_file)
        cam_data = cam["Camera Metadata"]

    camtype = cam_data[0]["Type"]
    
    with open(file, 'a+') as json_file:
        
        if camtype == "Government":
            
            results = {"Registration": i,
                       "Violations": violation,
                       "Date": ddate,
                       "Time": dtime,
                       "Location": loc,
                       "Confidence": confidence,
                       "file_path": filename}
            
        elif camtype == "Private":
            
            results = {"Registration": i["Plate"],
                       "Violations": violation,
                       "Date": ddate,
                       "Time": dtime,
                       "Location": loc,
                       "Confidence": confidence,
                       "file_path": filename}
        
        write_json(results)

def check_violation(plate, confidence, filename):
    
    now = datetime.now()
    dtime = now.strftime("%H:%M:%S")
    ddate = now.strftime("%d/%m/%Y")

    registered = False
    licensevalid = False
    qidvalid = False
    
    no_entry = False
    no_parking = False
    disabled = False
        
    violations = [] 
        
    with open(registry, "r") as reg_file:
        reg = json.load(reg_file)
        reg_data = reg["registered"]
    
    with open(cam_context, "r") as cam_file:
        cam = json.load(cam_file)
        cam_data = cam["Camera Metadata"]

    camtype = cam_data[0]["Type"]
    context = cam_data[0]["Context"]
    auth = cam_data[0]["Authorized"]
    loc = cam_data[0]["Location"]
    
    if camtype == "Government":
        
        for i in reg_data:
            if plate == i["Plate"]:
                registered = True

                if datetime.strptime(i["QID Expiry"], "%d/%m/%Y").date() > datetime.strptime(ddate, "%d/%m/%Y").date():
                    qidvalid = True
                    
                if datetime.strptime(i["License Validity"], "%d/%m/%Y").date() > datetime.strptime(ddate, "%d/%m/%Y").date():
                    licensevalid = True
                break

        for b in context:
            if b == "Disabled Parking" and i["Disabled"] == "False":
                disabled = True
            if b == "No Entry":
                no_entry = True
            if b == "No Parking":
                no_parking = True
        
        for a in auth:
            if plate == a:
                no_entry = False
                no_parking = False
                disabled = False
                break
                
        if registered == False:
            violations.append("Unregistered")
            licensevalid = True
            qidvalid = True
            i = {"Plate":plate}
        
        if licensevalid == False:
            violations.append("License Expired")
            
        if qidvalid == False:
            violations.append("QID Expired")
        
        if no_entry == True:
            violations.append("No Entry")

        if no_parking == True:
            violations.append("No Parking")

        if disabled == True:
            violations.append("Disabled Parking")
    
    elif camtype == "Private":
        
        for i in reg_data:
            if plate == i["Plate"]:
                registered = True
                break
                   
        for b in context:
            if b == "Disabled Parking" and i["Disabled"] == "False":
                disabled = True
            if b == "No Entry":
                no_entry = True
            if b == "No Parking":
                no_parking = True
        
        for a in auth:
            if plate == a:
                no_entry = False
                no_parking = False
                disabled = False
                break
                
        if registered == False:
            violations.append("Unregistered")
            i = {"Plate":plate}
   
        if no_entry == True:
            violations.append("No Entry")

        if no_parking == True:
            violations.append("No Parking")

        if disabled == True:
            violations.append("Disabled Parking")

        
    write_result(i, confidence, filename, violations, loc, ddate, dtime)
    
    if violations:
        email_functions.send_alert(i, plate, confidence, filename, violations, loc, ddate, dtime)


        
    
    
        
    