'''*********************************************************************************************************************
     **
     **  Smart Trolley - To develop Aruco-PICAM based scanning system for mall in order to expedite billing process.
     **
     **  Written By:    Akash Vishwas Londhe 
     **  Written On:    October 2019 - November 2019
     **  Last Updated:  December 2019 - Akash Vishwas Londhe
     **
     **  This File May Be Modified And Re-Distributed Freely. 
     **  Original File Content written by Akash Vishwas Londhe
     **  
 *********************************************************************************************************************'''

# import required packages

import MySQLdb
import cv2
import cv2.aruco as aruco
import picamera
from picamera.array import PiRGBArray
import time
import RPi.GPIO as GPIO     # Importing RPi library to use the GPIO pins
from time import sleep      # Importing sleep from time library to add delay in code
import csv

# initial initialization

servo_pin = 21      # Initializing the GPIO 21 for servo motor i.e GPIO.BOARD=40
buzzer_pin = 20     # Initializing the GPIO 20 for buzzer i.e GPIO.BOARD=38

# Here user and password are related with my mobile hotspot
# While db, host, port related with database

db=MySQLdb.connect(user='pi',passwd='coolakash',db='mydb',host='localhost',port=3306)
cursor=db.cursor()

GPIO.setmode(GPIO.BCM)          # We are using the BCM pin numbering
GPIO.setup(servo_pin, GPIO.OUT)     # Declaring GPIO 21 as output pin
GPIO.setup(buzzer_pin, GPIO.OUT)     # Declaring GPIO 20 as output pin

pwm = GPIO.PWM(servo_pin, 50)     # Created PWM channel at 50Hz frequency

pwm.start(2.5) # to initialize it with 0 angle as in this case duty cycle of servo varying from 2.5-12
#pwm.start(0)

# global declaration of variable

global weightOfElement
global angleOfElement
global previousWeight
global pwm

ID=0

billDetail = []


# function to find Aruco ID from scanned image

def findArucoID(image):
    
    aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
    parameters = aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(
    image, aruco_dict, parameters=parameters)
    
    aruco.drawDetectedMarkers(image, corners, ids)
    aruco.drawDetectedMarkers(image, rejectedImgPoints, borderColor=(100, 0, 240))
    
    cv2.imshow('', image)
    cv2.waitKey(1)
    cv2.destroyAllWindows()
    
    if ids==None:
        
        return False
    
    else:
        
        global ID
        ID=ids[0]
        return True



# function to rotate servo motor

def rotateServo(angle):

    print(angle)
    duty = angle / 18 + 2
    
    GPIO.output(servo_pin, True)
    pwm.ChangeDutyCycle(duty)
    sleep(2)
    pwm.ChangeDutyCycle(2.5)
    sleep(1)
    GPIO.output(servo_pin,False)
    pwm.ChangeDutyCycle(0)



# function to check weight of newly scanned element

def checkWeight(weight):
    
    print(weight)



# function to retrieve element details from database

def elementDetail():
    
    cursor.execute("""SELECT * FROM Info WHERE 1""");
    result=cursor.fetchall()
    global ID
    
    for row in result:
        
        if row[0] == ID :
            
            s=row[1] , row[2]
            print(s)
            
            global billDetail
            billDetail.append(s)
            
            with open('Bill.csv', 'a') as newFile:
                newFileWriter = csv.writer(newFile)
                newFileWriter.writerow([row[1],row[2]])
        
            weightOfElement=row[3]
            angleOfElement=row[4]
            modified_count=row[5]
            
            GPIO.output(buzzer_pin,True)
            sleep(1)
            GPIO.output(buzzer_pin,False)
            
            rotateServo(angleOfElement)
            checkWeight(weightOfElement)

            
    modified_count=modified_count-1
    sql= "update Info set Count = %s where Aruco_Code = %s;"
    cursor.execute(sql, (modified_count, ID))
    # set ID to 0
    ID=0



# main function

def main():
    
    with open('Bill.csv',mode='w')as csv_file:
        
        fieldnames=['Element Name','Price']
        writer=csv.DictWriter(csv_file,fieldnames=fieldnames)
        writer.writeheader()
                
    try:
        
        with picamera.PiCamera() as camera:
            
            camera.resolution=(1280,720)
            while True:
                
                rawCapture = PiRGBArray(camera)
                # allow the camera to warmup
                time.sleep(0.1)
                camera.start_preview()
                # grab an image from the camera
                camera.capture(rawCapture, format="bgr")
                #to convert array into image
                image = rawCapture.array
                camera.stop_preview()
                
                global ID
                
                if findArucoID(image):
                    
                    print("Marker ID is", ID)
                    elementDetail() 
                
                #cv2.waitKey(1000)
                #cv2.destroyAllWindows()
                #elementDetail(ID)
                    
    except KeyboardInterrupt:
        
            pass

if __name__ == "__main__":
    
        main()
