cd /www/beehive-entrance-video-processor/
COMPOSE_PROJECT_NAME=gratheon docker-compose down

chown www:www-data -R /www/beehive-entrance-video-processor
sudo -H -u www bash -c 'cd /www/beehive-entrance-video-processor/' 
COMPOSE_PROJECT_NAME=gratheon docker-compose up -d --build