import RPi.GPIO as GPIO
import time
from picamera2 import Picamera2, Preview
from AlphaBot2 import AlphaBot2
import torch
import cv2

right_dic = {'left': 'front', 'front': 'right', 'right': 'back', 'back': 'left'}
left_dic = {'left': 'back', 'front': 'left', 'right': 'front', 'back': 'right'}

TRIG = 22
ECHO = 27
lrigAng = 1.1
rrigAng = 1.1
lflatAng = 1.1
rflatAng = 1.1
forwardTime = 1.4
wallDist = 40
Ab = AlphaBot2(fspeed=20,tspeed=10)

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
	if 'cup' in detected_classes:
		Ab.Buffer_ON()
		Ab.right()
		print("Find the cup!!")
		time.sleep(4.2)
		Ab.stop()
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
		self.checked = False

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
	if Distance() > wallDist:
		print('front')
		update_req_dic.update({cDire: True})

	TurnLeft(lrigAng)
	if detection():
		return dict()
	if Distance() > wallDist:
		print('left')
		update_req_dic.update({left_dic.get(cDire): True})

	TurnRight(rflatAng)
	if detection():
		return dict()
	if Distance() > wallDist:
		print('right')
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
	node.checked = True

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

	try:
		root = Node(None, None, None, None)
		last_node = None
		current_node = root
		current_direction = 'front'
		while True:
			if not current_node.checked:
				update_dict = check_update_require(current_direction)
				if update_dict == dict():
					print('Target Object is found.')
					break
				update_nodes(current_node, update_dict) #有路就新增node
				current_direction = right_dic.get(current_direction) #每次檢查完最後一格方向是右邊
			if current_node.left != None:
				if current_direction == 'front':
					TurnLeft(lrigAng)
				elif current_direction == 'right':
					TurnLeft(lflatAng)
				elif current_direction == 'back':
					TurnRight(rrigAng)
                
				print('Go Left!')
				GoForward(forwardTime)
                
				last_node = current_node
				current_node = current_node.left
				if last_node.front == None and last_node.right == None and last_node.back == None:
					current_node.right = None #若其他方向都沒路就不用再回來了
				if current_node.right == None:
					print('delete node')
				
				current_direction = 'left'
			elif current_node.front != None:
				if current_direction == 'left':
					TurnRight(rrigAng)
				elif current_direction == 'right':
					TurnLeft(lrigAng)
				elif current_direction == 'back':
					TurnRight(rflatAng)
                
				print('Go Forward!')
				GoForward(forwardTime)
                
				last_node = current_node
				current_node = current_node.front
				if last_node.left == None and last_node.right == None and last_node.back == None:
					current_node.back = None
				if current_node.back == None:
					print('delete node')

				current_direction = 'front'
			elif current_node.right != None:
				if current_direction == 'left':
					TurnRight(rflatAng)
				elif current_direction == 'front':
					TurnRight(rrigAng)
				elif current_direction == 'back':
					TurnLeft(lrigAng)
                
				print('Go Right!')
				GoForward(forwardTime)
                
				last_node = current_node
				current_node = current_node.right
				if last_node.left == None and last_node.front == None and last_node.back == None:
					current_node.left = None
				if current_node.left == None:
					print('delete node')
				current_direction = 'right'
			elif current_node.back != None:
				if current_direction == 'left':
					TurnLeft(lrigAng)
				elif current_direction == 'front':
					TurnLeft(lflatAng)
				elif current_direction == 'right':
					TurnRight(rrigAng)
                
				print('Go Back!')
				GoForward(forwardTime)
                
				last_node = current_node
				current_node = current_node.back
				if last_node.left == None and last_node.front == None and last_node.right == None:
					current_node.front = None
				if current_node.front == None:
					print('delete node')
				
				current_direction = 'back'
			else:
				print('No any way!')
				break



	except KeyboardInterrupt:
		GPIO.cleanup()
