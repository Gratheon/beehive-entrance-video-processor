import os
import time
import datetime
import cv2
from uploader import upload_file_async

FPS = 30
WIDTH_PX = 640
HEIGHT_PX = 480

# enable GPU acceleration
cv2.CAP_GSTREAMER

# camera = cv2.VideoCapture(2)
camera = cv2.VideoCapture("/dev/video2", cv2.CAP_V4L2)


if (camera.isOpened() == False):  
    print("Error reading camera") 

camera.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH_PX)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT_PX)
camera.set(cv2.CAP_PROP_FPS, 30)

cv2.namedWindow("Preview", cv2.WINDOW_AUTOSIZE)

try:
    while True:
        timestamp = int(datetime.datetime.now().timestamp())
        output_file = f'./cam/{timestamp}.mp4'
        out = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'mp4v'), FPS, (WIDTH_PX, HEIGHT_PX))

        start_time = time.time()
        while True:
            ret, frame = camera.read()
            if not ret:
                print('breaking')
                break
            out.write(frame)
            cv2.imshow("Preview", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q') or time.time() - start_time >= 10:
                out.release()
                break

        upload_file_async(output_file)

except KeyboardInterrupt:
    print("Recording and uploading stopped by user")

finally:
    os.remove(output_file)
    camera.release()
    cv2.destroyAllWindows()
