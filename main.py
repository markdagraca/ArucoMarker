

import RPi.GPIO as GPIO
import numpy as np
import cv2
import cv2.aruco as aruco
import imutils
from imutils.video import VideoStream
from imutils.video import FPS
import time
from flask import Flask
import _thread as thread
from adafruit_motorkit import MotorKit
from flask_cors import CORS

robot = MotorKit()
robot.motor1.throttle = 0
robot.motor2.throttle = 0


 


def getdistance():
    from Bluetin_Echo import Echo

    # Define GPIO pin constants.
    TRIGGER_PIN = 23
    ECHO_PIN = 24
    # Initialise Sensor with pins, speed of sound.
    speed_of_sound = 315
    echo = Echo(TRIGGER_PIN, ECHO_PIN, speed_of_sound)
    # Measure Distance 5 times, return average.
    samples = 2
    # Take multiple measurements.

    return echo.read('cm', samples)


data = 'foo'
app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
manual=True
@app.route("/manualflip")
def manualflip():
    manual=not manual
    return manual
def checkIfInManual():
    return manual

@app.route("/")
def main():
    return data
@app.route('/left')
def left():
    if checkIfInManual:
        robot.motor1.throttle=1
     robot.motor2.throttle =1
@app.route('/right')
def right():
    if checkIfInManual:
        robot.motor1.throttle=1
        robot.motor2.throttle =1
@app.route('/front')
def front():
    if checkIfInManual:
        robot.motor1.throttle=1
        robot.motor2.throttle =-1
@app.route('/back')
def back():
    if checkIfInManual:
        robot.motor1.throttle=-1
        robot.motor2.throttle =1
@app.route('/stop')
def stop():
    if checkIfInManual:
        robot.motor1.throttle=0
        robot.motor2.throttle=0
@app.route('/joystick')

def joystick():
    if checkIfInManual:
        x = float(request.args.get('x'))
        y = float(request.args.get('y'))
        #motor 2 left motor 1 right
        motor2=y-x
        motor1=y+x
        if(motor2>100):
            motor2=100
        if(motor1>100):
            motor1=100
    


        robot.motor1.throttle=-motor1/100
        robot.motor2.throttle=motor2/100
        print(x/100-y/100)
        return "IT worked"


def flaskThread():
    app.run(host='0.0.0.0', port=80)


if __name__ == '__main__':

    thread.start_new_thread(flaskThread, ())

vs = VideoStream(src=0).start()
time.sleep(1)

fps = FPS().start()
initBB = 0
lastSuccess = time.time()
left = 0
right = 0
width = 500


def move(x,distance):
    l = (x-width/2)/(width/2)
    r = -l
    global right
    global left
    if abs(l) < 0.3:
        if(distance<20):
            l +=- 0.45
            r +=-0.45
            print("go backwards DANGER!!!!")
        elif(distance<30):
            l=0
            r=0

        else:
            l += 0.5
            r += 0.5
            print("going straight")
    

    right = r/3
    left = l/3
    print("x:" + str(x))
    print("Left:"+str(left))
    print("Right: "+str(right))

    robot.motor1.throttle = left
    robot.motor2.throttle = right


prevtime = time.time()
sensortime=time.time()
inital = True
currentdistance = getdistance()
while not checkIfInManual:
    if time.time()-prevtime > 1/30:

        frame = vs.read()
        frame = imutils.rotate(frame, 180)
        if frame is None:
            break
        frame = imutils.resize(frame, width=width)
        (H, W) = frame.shape[:2]

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
        parameters = aruco.DetectorParameters_create()
        corners, ids, rejectedImgPoints = aruco.detectMarkers(
            gray, aruco_dict, parameters=parameters)
        frame = aruco.drawDetectedMarkers(frame.copy(), corners, ids)


        fps.update()
        fps.stop()
        info = [
            ("FPS", "{:.2f}".format(fps.fps()))
        ]
        for (i, (k, v)) in enumerate(info):
            text = "{}: {}".format(k, v)
            cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        if(len(corners) > 0):
            if inital:
                robot.motor1.throttle = 0
                robot.motor2.throttle = 0
            inital = False
            _corner = corners[0][0]
            _centerY = int((_corner[0][1] + _corner[2][1]) / 2)
            _centerX = int((_corner[0][0] + _corner[2][0]) / 2)
            cv2.circle(frame, (_centerX, _centerY), 5, (255, 255, 255), 5)
            move(_centerX,currentdistance)
        elif inital:
            robot.motor1.throttle = 1 / 6
            robot.motor2.throttle = -1 / 6
        elif currentdistance<20:
            robot.motor1.throttle = -1 / 5.5
            robot.motor2.throttle = -1 /5.5
        else:

            left = 0
            right = 0
            robot.motor1.throttle = left
            robot.motor2.throttle = right

        cv2.line(frame, (0, int((H/2))), (W, int(H/2)),
                 (0, 0, 0), 2)  # horizontal
        cv2.line(frame, (int((W / 2)), 0),
                 (int(W / 2), H), (0, 0, 0), 2)  # vertical
        # cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        prevtime = time.time()
    else:
        if time.time()-sensortime > 1/15:
            currentdistance = getdistance()
            print("Current distance",currentdistance)
            sensortime=time.time()

