import os
import time
import datetime
import cv2
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

FPS = 30
WIDTH_PX = 1280
HEIGHT_PX = 720

# Set CUDA backend for OpenCV
cv2.cuda.setDevice(0)  # Specify GPU device
cv2.cuda.printCudaDeviceInfo(0)  # Print CUDA device info

camera = cv2.VideoCapture(0)

if (camera.isOpened() == False):  
    print("Error reading camera") 

camera.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH_PX)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT_PX)
cv2.namedWindow("Preview", cv2.WINDOW_NORMAL)

try:
    while True:
        timestamp = int(datetime.datetime.now().timestamp())
        output_file = f'./cam/{timestamp}.mp4'
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_file, fourcc, FPS, frameSize=(WIDTH_PX, HEIGHT_PX))

        start_time = time.time()
        while True:
            ret, frame = camera.read()
            if not ret:
                print('breaking')
                break
            frameBGR = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            # Convert to GPU Mat
            gpu_frame = cv2.cuda_GpuMat()
            gpu_frame.upload(frameBGR)
            # Write GPU Mat to video file
            out.write(cv2.cuda.cvtColor(gpu_frame, cv2.COLOR_BGR2RGB).download())
            cv2.imshow("Preview", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q') or time.time() - start_time >= 10:
                out.release()
                break
        

except KeyboardInterrupt:
    print("Recording and uploading stopped by user")

finally:
    camera.release()
    cv2.destroyAllWindows()

def upload():
    # Prepare multipart/form-data request
    url = 'https://video.gratheon.com/graphql'
    headers = {
        'Authorization': 'Bearer YOUR_ACCESS_TOKEN'
    }
    payload = {
        'query': (
            'mutation UploadVideo($file: Upload!, $boxId: ID!) {'
            '  uploadGateVideo(file: $file, boxId: $boxId)'
            '}'
        ),
        'variables': {
            'boxId': '123'  # Replace with the actual box ID
        }
    }
    files = {
        'file': (output_file, open(output_file, 'rb'), 'video/mp4')  # Adjust content type if needed
    }
    multipart_data = MultipartEncoder(fields=files, boundary='----MyBoundary')

    # Make multipart/form-data request
    response = requests.post(url, headers=headers, data=multipart_data,
                                params=payload, timeout=30, allow_redirects=True)

    if response.status_code == 200:
        print("Video uploaded successfully")
        os.remove(output_file)
    else:
        print("Error uploading video:", response.status_code)
