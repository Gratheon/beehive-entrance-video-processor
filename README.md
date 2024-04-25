# beehive-entrance-video-processor
Beehive entrance video processing service. Manages video inferencing. Can be deployed on edge

## URLs
- localhost:8400

## Architecture

### Edge Inference
```mermaid
flowchart LR
	subgraph Edge
 	models-bee-detector[<a href="https://github.com/Gratheon/models-bee-detector">models-bee-detector</a>] --> beehive-entrance-video-processor
	end
	
	subgraph Cloud
	 beehive-entrance-video-processor --"send edge-inference results"--> telemetry-api[<a href="https://github.com/Gratheon/telemetry-api">telemetry-api</a>]
	end
```

### Video chunk upload for observation & playback
See video_camera_server.py
```mermaid
flowchart LR
	beehive-entrance-video-processor --"upload video chunk"--> gate-video-stream
```

### Distributed GPU inference assistance
```mermaid
flowchart LR

	subgraph Edge
	beehive-entrance-video-processor --"inference unprocessed file" --> models-gate-tracker
	end

	subgraph Cloud
	beehive-entrance-video-processor --"get next unprocessed video segment"--> gate-video-stream
	beehive-entrance-video-processor --"send inference results"--> gate-video-stream -- "store results long-term" --> mysql
	
	end
```



### Installation
```
pip3 install picamera requests requests_toolbelt
```