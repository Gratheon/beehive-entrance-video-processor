FROM node:16-alpine

# Install FFmpeg v5
RUN apk add --no-cache ffmpeg

WORKDIR /app

COPY . /app/
RUN npm install
RUN npm run build

EXPOSE 8900
EXPOSE 8950

# CMD ["npm", "run", "start"]
CMD ["node", "/app/app/gate-video-stream.js"]