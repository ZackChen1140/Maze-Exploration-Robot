import cv2
import time
from picamera2 import Picamera2, Preview
import torch

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
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

    while True:
        im = picamera.capture_array()
        #img = im[...,::-1] #bgr2rgb
        results = model(im)
        
        results.print()

        #results.save()
        results.render()
        # result0_path = results.files[0]
        # result_img = cv2.imread(result0_path)
        result_bgr = results.imgs[0][...,::-1] #bgr2rgb

        cv2.imshow("Result", result_bgr)
        cv2.waitKey(1)



if __name__ == "__main__":
    main()