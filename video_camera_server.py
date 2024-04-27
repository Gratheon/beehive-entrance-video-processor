import os
import time
import cv2
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
cv2.namedWindow("Preview", cv2.WINDOW_NORMAL)

try:
    while True:
        output_file = f'./tmp/video_{time.time()}.mp4'  # Use .mp4 extension
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Specify codec for MP4
        out = cv2.VideoWriter(output_file, fourcc, 20.0, (640, 480))

        start_time = time.time()
        while time.time() - start_time < 10:
            ret, frame = camera.read()
            if ret:
                cv2.imshow("Preview", frame)
                out.write(frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        out.release()

        # upload()

except KeyboardInterrupt:
    print("Recording and uploading stopped by user")

finally:
    cv2.destroyAllWindows()
    camera.close()

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
