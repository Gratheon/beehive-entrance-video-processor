start:
	mkdir -p tmp
	COMPOSE_PROJECT_NAME=gratheon docker compose -f docker-compose.dev.yml up --build
stop:
	COMPOSE_PROJECT_NAME=gratheon docker compose -f docker-compose.dev.yml down

dev:
	NATIVE=1 ENV_ID=dev go run main.go

build:
	@echo Building binary:
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
	go build \
		-a \
		-o beehive-entrance-video-processor \
		*.go