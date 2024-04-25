import os
import time
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import picamera

# Configure the camera
camera = picamera.PiCamera()
camera.resolution = (640, 480)  # Adjust resolution as needed

# Start the camera preview
camera.start_preview()

try:
    while True:
        # Record video
        output_file = f'video_{time.time()}.h264'  # Use .h264 extension
        camera.start_recording(output_file)
        camera.wait_recording(5)  # Record for 5 seconds
        camera.stop_recording()

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

except KeyboardInterrupt:
    print("Recording and uploading stopped by user")

finally:
    camera.stop_preview()  # Stop the camera preview
    camera.close()
