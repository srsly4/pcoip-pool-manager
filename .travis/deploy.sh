#!/bin/bash
set -e

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USER" --password-stdin

docker build -f docker/Dockerfile -t "pcoip-pool-manager:latest" .

docker tag "pcoip-pool-manager:latest" "srsly4/pcoip-pool-manager:latest"
docker push "srsly4/pcoip-pool-manager:latest"
echo "Push finished!"