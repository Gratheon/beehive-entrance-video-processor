import json
import os
import time
import datetime
import cv2
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

def upload(output_file: str):
    # Make multipart/form-data request
    response = requests.post(
        'https://video.gratheon.com/graphql', 
        headers={
            'Authorization': 'Bearer ...' # generate token in https://app.gratheon.com/account
        }, 
        data={
            "operations": json.dumps({
                'query': (
                    'mutation UploadVideo($file: Upload!, $boxId: ID!) {'
                    '  uploadGateVideo(file: $file, boxId: $boxId)'
                    '}'
                ),
                'variables': {
                    'file': None,
                    'boxId': '248'  # Replace with the actual box ID, take it from the URL of the beehive view with gate selected
                }
            }),
            "map": json.dumps({ "0": ["variables.file"] })
        },
        files = {
            "0": open(output_file, 'rb'), # Adjust content type if needed
        },
        timeout=120, 
        allow_redirects=True
    )

    if response.status_code == 200:
        print("Video uploaded successfully")
    else:
        print("Error uploading video:", response.status_code)
        
    print(response.text)



FPS = 30
WIDTH_PX = 640
HEIGHT_PX = 480

# enable GPU acceleration
cv2.CAP_GSTREAMER

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
        out = cv2.VideoWriter(output_file, fourcc, FPS, (WIDTH_PX, HEIGHT_PX))

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

        upload(output_file)

        # remove file after uploading, you can leave it if you want a local cache
        # but you need enough storage to not run out of space
        os.remove(output_file)

except KeyboardInterrupt:
    print("Recording and uploading stopped by user")

finally:
    os.remove(output_file)
    camera.release()
    cv2.destroyAllWindows()
