import RPi.GPIO as GPIO
import time

from AlphaBot2 import AlphaBot2

right_dic = {'left': 'front', 'front': 'right', 'right': 'back', 'back': 'left'}
left_dic = {'left': 'back', 'front': 'left', 'right': 'front', 'back': 'right'}

TRIG = 22
ECHO = 27
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

	if Distance() > 40:
		update_req_dic.update({cDire: True})

	TurnLeft(0.3)
    
	if Distance() > 40:
		update_req_dic.update({left_dic.get(cDire): True})

	TurnRight(0.6)
    
	if Distance() > 40:
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

	

if __name__=='__main__':
	# for Ultrasonic

	# set up
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(TRIG,GPIO.OUT,initial=GPIO.LOW)
	GPIO.setup(ECHO,GPIO.IN)

	try:
		root = Node(None, None, None, None)
		current_node = root
		current_direction = 'front'
		while True:
			update_nodes(current_node, check_update_require(current_direction)) #有路就新增node
			current_direction = right_dic.get(current_direction) #每次檢查完最後一格方向是右邊
			if current_node.left != None:
				if current_direction == 'front':
					TurnLeft(0.3)
				elif current_direction == 'right':
					TurnLeft(0.6)
				elif current_direction == 'back':
					TurnRight(0.3)
                    
				GoForward(1)
                
				if current_node.front == None and current_node.right == None and current_node.back == None:
					current_node.left.right = None #若其他方向都沒路就不用再回來了
				current_node = current_node.left
				current_direction = 'left'
			elif current_node.front != None:
				if current_direction == 'left':
					TurnRight(0.3)
				elif current_direction == 'right':
					TurnLeft(0.3)
				elif current_direction == 'back':
					TurnRight(0.6)
                    
				GoForward(1)
                
				if current_node.left == None and current_node.right == None and current_node.back == None:
					current_node.front.back = None
				current_node = current_node.front
				current_direction = 'front'
			elif current_node.right != None:
				if current_direction == 'left':
					TurnRight(0.6)
				elif current_direction == 'front':
					TurnRight(0.3)
				elif current_direction == 'back':
					TurnLeft(0.3)
                    
				GoForward(1)
                
				if current_node.left == None and current_node.front == None and current_node.back == None:
					current_node.right.left = None
				current_node = current_node.right
				current_direction = 'right'
			elif current_node.back != None:
				if current_direction == 'left':
					TurnLeft(0.3)
				elif current_direction == 'front':
					TurnLeft(0.6)
				elif current_direction == 'right':
					TurnRight(0.3)
                    
				GoForward(1)
                
				if current_node.left == None and current_node.front == None and current_node.right == None:
					current_node.back.front = None
				current_node = current_node.back
				current_direction = 'back'
			else:

				break



	except KeyboardInterrupt:
		GPIO.cleanup()