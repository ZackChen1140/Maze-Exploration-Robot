import cv2
from picamera2 import Picamera2, Preview

def capture_image(picamera, interval=1):
    counter = 0
    while True:
        time.sleep(interval)
        picamera.capture_file(f"images/image_{counter}.jpg")
        counter += 1

def main():
    picamera = Picamera2()
    picamera.configure(picamera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    picamera.start()

    while True:
        im = picamera.capture_array()
        cv2.imshow("Camera", im)
        cv2.waitKey(1)

if __name__ == "__main__":
    main()