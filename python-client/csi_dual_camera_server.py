import os
import cv2
import threading
import numpy as np
import datetime
import time
from uploader import upload


class CSI_Camera:
    def __init__(self):
        self.video_capture = None
        self.frame = None
        self.grabbed = False
        self.read_thread = None
        self.read_lock = threading.Lock()
        self.running = False

    def open(self, gstreamer_pipeline_string):
        try:
            self.video_capture = cv2.VideoCapture(
                gstreamer_pipeline_string, cv2.CAP_GSTREAMER
            )
            self.grabbed, self.frame = self.video_capture.read()

        except RuntimeError:
            self.video_capture = None
            print("Unable to open camera")
            print("Pipeline: " + gstreamer_pipeline_string)


    def start(self):
        if self.running:
            print('Video capturing is already running')
            return None
        if self.video_capture != None:
            self.running = True
            self.read_thread = threading.Thread(target=self.updateCamera)
            self.read_thread.start()
        return self

    def stop(self):
        self.running = False
        self.read_thread.join()
        self.read_thread = None

    def updateCamera(self):
        while self.running:
            try:
                grabbed, frame = self.video_capture.read()
                with self.read_lock:
                    self.grabbed = grabbed
                    self.frame = frame
            except RuntimeError:
                print("Could not read image from camera")

    def read(self):
        with self.read_lock:
            frame = self.frame.copy()
            grabbed = self.grabbed
        return grabbed, frame

    def release(self):
        if self.video_capture != None:
            self.video_capture.release()
            self.video_capture = None
        if self.read_thread != None:
            self.read_thread.join()


def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1920,
    capture_height=1080,
    display_width=1920,
    display_height=1080,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

FPS = 30
WIDTH_PX = 640 # 960 # 640 # 1920
HEIGHT_PX = 360 # 540 # 480 # 1080
VIDEO_FILE_MAX_DURATION_SEC = 10

def run_cameras():
    window_title = "Dual CSI Cameras"
    left_camera = CSI_Camera()
    left_camera.open(
        gstreamer_pipeline(
            sensor_id=0,
            capture_width=1920,
            capture_height=1080,
            flip_method=0,
            framerate=FPS,
            display_width=WIDTH_PX, #960,
            display_height=HEIGHT_PX, #540,
        )
    )
    left_camera.start()

    right_camera = CSI_Camera()
    right_camera.open(
        gstreamer_pipeline(
            sensor_id=1,
            capture_width=1920,
            capture_height=1080,
            flip_method=0,
            display_width=WIDTH_PX,
            display_height=HEIGHT_PX,
        )
    )
    right_camera.start()

    if left_camera.video_capture.isOpened() and right_camera.video_capture.isOpened():    
        cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)

        try:
            # video writing loop
            while True:
                timestamp = int(datetime.datetime.now().timestamp())
                output_file = f'/home/gratheon/Desktop/gratheon/python-client/cam/{timestamp}.mp4'

                writer = cv2.VideoWriter(
                    f'appsrc ! video/x-raw, format=BGR ! videoconvert ! x264enc tune=zerolatency bitrate=3000 speed-preset=superfast ! video/x-h264, stream-format=byte-stream ! h264parse ! mp4mux ! filesink location={output_file}',
                      cv2.CAP_GSTREAMER, 0, FPS,(WIDTH_PX,HEIGHT_PX))

                if not writer.isOpened():
                    print("Failed to open output")
                    exit()

                start_time = time.time()

                # camera reading loop
                while True:
                    _, left_image = left_camera.read()
                    _, right_image = right_camera.read()
                    camera_images = np.hstack((left_image, right_image)) 


                    if left_image is None:
                        break

                    writer.write(left_image)

                    if cv2.getWindowProperty(window_title, cv2.WND_PROP_AUTOSIZE) >= 0:
                        cv2.imshow(window_title, camera_images)
                    else:
                        break

                    isVideoLengthReached = time.time() - start_time >= VIDEO_FILE_MAX_DURATION_SEC

                    # exit on escape or q
                    if cv2.waitKey(30) & 0xFF == 27 or cv2.waitKey(1) & 0xFF == ord('q') or isVideoLengthReached:
                        writer.release()
                        break

                upload(output_file)

                # remove file after uploading, you can leave it if you want a local cache
                # but you need enough storage to not run out of space
                os.remove(output_file)
        finally:

            left_camera.stop()
            left_camera.release()
            right_camera.stop()
            right_camera.release()
        cv2.destroyAllWindows()
    else:
        print("Error: Unable to open both cameras")
        left_camera.stop()
        left_camera.release()
        right_camera.stop()
        right_camera.release()


if __name__ == "__main__":
    run_cameras()
