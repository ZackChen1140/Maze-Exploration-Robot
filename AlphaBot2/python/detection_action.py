import RPi.GPIO as GPIO
import time
from picamera2 import Picamera2, Preview
from AlphaBot2 import AlphaBot2
from PCA9685 import PCA9685
import torch
import cv2

right_dic = {'left': 'front', 'front': 'right', 'right': 'back', 'back': 'left'}
left_dic = {'left': 'back', 'front': 'left', 'right': 'front', 'back': 'right'}

TRIG = 22
ECHO = 27
rigAng = 0.3
flatAng = 0.5
Ab = AlphaBot2()

def GoForward(degree):
	Ab.forward()
	time.sleep(degree)
	Ab.stop()
	time.sleep(0.5)

def TurnRight(degree):
	Ab.right()
	time.sleep(degree)
	Ab.stop()
	time.sleep(0.5)
 
def TurnLeft(degree):
	Ab.left()
	time.sleep(degree)
	Ab.stop()
	time.sleep(0.5) 

def detection():
	im = picamera.capture_array()
	results = model(im)
	detected_classes = results.pandas().xyxy[0]['name'].tolist()
	if 'sports ball' in detected_classes:
		Ab.Buffer_ON()
		time.sleep(10)
		Ab.Buffer_OFF()
		return True
	else:
		return False

class Node(object):
	def __init__(self, left=None, front=None, right=None, back=None):
		self.left = left
		self.front = front
		self.right = right
		self.back = back

def capture_image(picamera, interval=1):
    counter = 0
    while True:
        time.sleep(interval)
        picamera.capture_file(f"images/image_{counter}.jpg")
        counter += 1

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

def check_update_require(cDire):

	update_req_dic = {'left': False, 'front': False, 'right': False, 'back': False}
	if detection():
		return dict()
	if Distance() > 35:
		update_req_dic.update({cDire: True})

	TurnLeft(rigAng)
	if detection():
		return dict()
	if Distance() > 35:
		update_req_dic.update({left_dic.get(cDire): True})

	TurnRight(flatAng)
	if detection():
		return dict()
	if Distance() > 35:
		update_req_dic.update({right_dic.get(cDire): True})

	return update_req_dic


def update_nodes(node, update_req_dic):
	
	if update_req_dic.get('left'):
		node.left = Node(left=None, front=None, right=node, back=None)
	if update_req_dic.get('front'):
		node.front = Node(left=None, front=None, right=None, back=node)
	if update_req_dic.get('right'):
		node.right = Node(left=node, front=None, right=None, back=None)
	if update_req_dic.get('back'):
		node.back = Node(left=None, front=node, right=None, back=None)

picamera = Picamera2()
picamera.configure(picamera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picamera.start()
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)    

if __name__=='__main__':
	# for Ultrasonic

	# set up
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(TRIG,GPIO.OUT,initial=GPIO.LOW)
	GPIO.setup(ECHO,GPIO.IN)

	pwm = PCA9685(0x40, debug=True)
	pwm.setPWMFreq(50)
	pwm.setServoPulse(2,2500)
	pwm.setServoPulse(0,1300)

	try:
		root = Node(None, None, None, None)
		current_node = root
		current_direction = 'front'
		while True:
			update_dict = check_update_require(current_direction)
			if update_dict == dict():
				break
			update_nodes(current_node, update_dict) #有路就新增node
			current_direction = right_dic.get(current_direction) #每次檢查完最後一格方向是右邊
			if current_node.left != None:
				if current_direction == 'front':
					TurnLeft(rigAng)
				elif current_direction == 'right':
					TurnLeft(flatAng)
				elif current_direction == 'back':
					TurnRight(rigAng)
                    
				GoForward(1.3)
                
				if current_node.front == None and current_node.right == None and current_node.back == None:
					current_node.left.right = None #若其他方向都沒路就不用再回來了
				current_node = current_node.left
				current_direction = 'left'
			elif current_node.front != None:
				if current_direction == 'left':
					TurnRight(rigAng)
				elif current_direction == 'right':
					TurnLeft(rigAng)
				elif current_direction == 'back':
					TurnRight(flatAng)
                    
				GoForward(1.3)
                
				if current_node.left == None and current_node.right == None and current_node.back == None:
					current_node.front.back = None
				current_node = current_node.front
				current_direction = 'front'
			elif current_node.right != None:
				if current_direction == 'left':
					TurnRight(flatAng)
				elif current_direction == 'front':
					TurnRight(rigAng)
				elif current_direction == 'back':
					TurnLeft(rigAng)
                    
				GoForward(1.3)
                
				if current_node.left == None and current_node.front == None and current_node.back == None:
					current_node.right.left = None
				current_node = current_node.right
				current_direction = 'right'
			elif current_node.back != None:
				if current_direction == 'left':
					TurnLeft(rigAng)
				elif current_direction == 'front':
					TurnLeft(flatAng)
				elif current_direction == 'right':
					TurnRight(rigAng)
                    
				GoForward(1.3)
                
				if current_node.left == None and current_node.front == None and current_node.right == None:
					current_node.back.front = None
				current_node = current_node.back
				current_direction = 'back'
			else:

				break



	except KeyboardInterrupt:
		GPIO.cleanup()
