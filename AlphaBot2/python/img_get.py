import time
import threading
from picamera2 import Picamera2, Preview

def capture_image(picamera, interval=1):
    counter = 0
    while True:
        time.sleep(interval)
        picamera.capture_file(f"images/image_{counter}.jpg")
        counter += 1

def main():
    picamera = Picamera2()
    video_config = picamera.create_video_configuration(main={"size": (1920, 1080)})
    picamera.configure(video_config)

    picamera.start_preview(Preview.QTGL)
    
    # Start the image capture thread
    capture_thread = threading.Thread(target=capture_image, args=(picamera,))
    capture_thread.start()

    # Start recording video
    picamera.start_recording("video.h264")

    # Record for 10 seconds
    time.sleep(10)

    # Stop recording video
    picamera.stop_recording()
    picamera.stop_preview()

    # Ensure the capture thread is stopped (optional)
    capture_thread.join()

if __name__ == "__main__":
    main()
