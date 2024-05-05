import json
import os
import time
import datetime
import cv2
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

def upload(output_file: str):
    # Retrieve environment variables
    bearer_token = os.getenv("API_TOKEN")
    box_id = os.getenv("BOX_ID")

    if not bearer_token or not box_id:
        print("Error: Please set the API_TOKEN and BOX_ID environment variables.")
        return

    # Make multipart/form-data request
    response = requests.post(
        'https://video.gratheon.com/graphql', 
        headers={
            'Authorization': f'Bearer {bearer_token}'
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
                    'boxId': box_id
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

