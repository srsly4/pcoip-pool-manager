#!/bin/bash
set -e

pip install --user awscli
export PATH=$PATH:$HOME/.local/bin

docker login --username=$DOCKER_LOGIN --password=$DOCKER_PASSWORD

docker build -f docker/Dockerfile --pull -t "pcoip-pool-manager:latest"

docker tag "pcoip-pool-manager:latest" "srsly4/pcoip-pool-manager:latest"
docker push "srsly4/pcoip-pool-manager:latest"
echo "Push finished!"