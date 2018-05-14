#!/bin/bash
set -e

docker login -e $DOCKER_EMAIL -u $DOCKER_USER -p $DOCKER_PASS

docker build -f docker/Dockerfile --pull -t "pcoip-pool-manager:latest"

docker tag "pcoip-pool-manager:latest" "srsly4/pcoip-pool-manager:latest"
docker push "srsly4/pcoip-pool-manager:latest"
echo "Push finished!"