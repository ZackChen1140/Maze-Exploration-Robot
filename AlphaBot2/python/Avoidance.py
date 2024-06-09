import RPi.GPIO as GPIO
import time
from AlphaBot2 import AlphaBot2

# for Ultrasonic
TRIG = 22
ECHO = 27

# for infrared rays
DR = 16
DL = 19

Ab = AlphaBot2(fspeed=20,tspeed=10)

# set up
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(DR,GPIO.IN,GPIO.PUD_UP)
GPIO.setup(DL,GPIO.IN,GPIO.PUD_UP)
GPIO.setup(TRIG, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(ECHO, GPIO.IN)

# Measure distance
def Distance():
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.000015)
    GPIO.output(TRIG, GPIO.LOW)
    while not GPIO.input(ECHO):
        pass
    t1 = time.time()
    while GPIO.input(ECHO):
        pass
    t2 = time.time()
    return (t2 - t1) * 34000 / 2


try:
    while True:
        Dist = Distance()
        DR_status = GPIO.input(DR)
        DL_status = GPIO.input(DL)
        print("Distance = %0.2f cm" % Dist)
        
        if Dist <= 20:
            Ab.Buffer_ON()
            if DL_status == 0 :
                Ab.left()
                print("Turn left")
            elif DR_status == 0:
                Ab.right()
                print("Turn right")
            else :
                Ab.left()
            time.sleep(0.3)
            Ab.Buffer_OFF()
            Ab.stop()
            
            
        else:
            Ab.forward()
        time.sleep(0.02)


except KeyboardInterrupt:
	GPIO.cleanup()
