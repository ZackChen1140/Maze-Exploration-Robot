import RPi.GPIO as GPIO
import time
from AlphaBot2 import AlphaBot2
from picamera2 import Picamera2, Preview
import torch
import cv2
from rpi_ws281x import Adafruit_NeoPixel, Color

Ab = AlphaBot2()

#ultrasonic sensors

TRIG = 22  
ECHO = 27

# LED strip configuration:
LED_COUNT      = 4      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(TRIG,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(ECHO,GPIO.IN)

def Distance():
	GPIO.output(TRIG,GPIO.HIGH)
	time.sleep(0.000015)
	GPIO.output(TRIG,GPIO.LOW)
	while not GPIO.input(ECHO):
		pass
	t1 = time.time()
	while GPIO.input(ECHO):
		pass
	t2 = time.time()
	return (t2-t1)*34000/2

def capture_image(picamera, interval=1):
    counter = 0
    while True:
        time.sleep(interval)
        picamera.capture_file(f"images/image_{counter}.jpg")
        counter += 1

class Stack: 
    def __init__(self): 
        self.elements = [] 
    
    def push(self, data): 
        self.elements.append(data) 
        return data 
    
    def pop(self): 
        return self.elements.pop() 
        
    def peek(self): 
        return self.elements[-1] 
        
    def get_stack(self):
        return self.elements

    def is_empty(self):
        return self.size == 0

# 1 - forward
# 2 - right
# 3 - left
# 4 - back
Stack = Stack()
Stack.push(1) # first element is forward (1)
distance = 20

#Maze Solver algorithm with the space mapping, space mapping is reffered to the parts which are using the stack
def MazeSolver(zastavica):
        if zastavica == 1 : # it means it's going back from the loop
                element_out_of_stack = stack.pop()
        time.sleep(1)
        print("10cm forward")

        im = picamera.capture_array()
        results = model(im)
        detected_classes = results.pandas().xyxy[0]['name'].tolist()

        if 'cup' in detected_classes:
                Ab.right()
                time.sleep(4.2)
                Ab.stop()
                print("Find the cup!!")

        Ab.forward()
        time.sleep(1) # 0.7 second or 10cm forward
        Ab.stop()
        time.sleep(1) # 1 second robot not moving

        Distance_Front = Distance() # calculating distance from the obstacle infront 
        print("Distance_Front = %0.2f cm" % Distance_Front)

        if Distance_Front > 100: # if the distance is higher than 200cm, it means it's the end of the labyrinth 
                Ab.stop() 
                print("Finish!! Getting out of the maze is successful")
                return 0
        else: # keep going
                Ab.right() # robot is turning 90 degrees to the right because of the ultrasonic sensors
                time.sleep(0.3)
                Ab.stop()
                time.sleep(1) # 1 second robot not moving

                Distance_Right = Distance() ##calculating distance from the obstacle on the right
                print("Distance_Right = %0.2f cm" % Distance_Right)

                if Distance_Right >= distance: # if there is no wall at the right side, go there, to the east 
                        last_element = Stack.peek()
                        time.sleep(1)
                        if zastavica == 0 :
                               Stack.push(2)
                        elif element_out_of_stack == 2 :
                               Stack.push(3)
                        else : # if the flag is equal to 1, push 'left'
                               Stack.push(1)

                        zastavica = 0 # not going the same way anymore
                        print("No wall on the right, go right")
                        return MazeSolver(zastavica)
                
                if (25 <= Distance_Front <= 100) :
                        Ab.left() # robot is turning 90 degrees to the left, to the north
                        time.sleep(0.3)
                        Ab.stop()
                        time.sleep(1) # 1 second robot not moving

                        if zastavica == 0 :
                                print("Forward")
                                Stack.push(1)
                                return MazeSolver(zastavica)
                        
                else :
                        
                        Ab.left() # robot is turning 90 degrees to the left, to the north
                        time.sleep(0.6)
                        Ab.stop()
                        time.sleep(1) # 1 second robot not moving

                        Distance_Left = Distance()# calculating distance from the obstacle on the left
                        print("Distance_Left = %0.2f cm" %Distance_Left)
                        if Distance_Left >= distance: # if there is no wall at the left, turn left
                                Stack.push(3)
                                time.sleep(1)
                                print("No wall on the left, go left")
                                return MazeSolver(zastavica)
                        elif ((Distance_Left <= distance ) and (Distance_Front <= distance) and (Distance_Right <= distance)): # if there are walls from all 3 sides, turn back
                                zastavica = 0
                                print("Turn back")
                                Ab.left() 
                                time.sleep(0.5) 
                                return MazeSolver(zastavica)
                 

               



#
#
# creating new stack, beacause we need the last element from the original stack to become the first element so we can run the maze again with those directions	

def New_stack():
        Stack_new = Stack()
        while Stack.notEmpty() != 0:
                direction = Stack.pop()
                Stack_new.push(direction)
        print("Correct directions for the maze are: ")
        print(Stack_new.get_stack())


#
#
# Function when putting the robot on the start again and running all the way to the goal of the labyrinth but only with the right directions
def MazeSolverSecondTurn():
        if Stack.notEmpty() != 0:
                direction = Stack_new.pop()
                print("The remaining directions until reaching the destination: ")
                print(Stack_new.get_stack())
                if smjer == 1:
                        Ab.forward()
                        time.sleep(1)
                elif direction == 2:
                        Ab.right()
                        time.sleep(0.3)
                        Ab.stop()
                        time.sleep(2)
                        Ab.forward()
                        time.sleep(1)
                elif direction == 3:
                        Ab.left()
                        time.sleep(0.3)
                        Ab.stop()
                        time.sleep(2)
                        Ab.forward()
                        time.sleep(1)
        else:
                print("Finish!!")

picamera = Picamera2()
picamera.configure(picamera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picamera.start()
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)                

try:      
        function = MazeSolver(0)
        time.sleep(10)
        function2 = New_stack()
        time.sleep(10)
        function3= MazeSolverSecondTurn()

except KeyboardInterrupt:
        GPIO.cleanup()
