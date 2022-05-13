#!/usr/bin/env sh
set -e
IMAGE=us-central1-docker.pkg.dev/secretscout/images/bot

docker buildx build --platform linux/amd64 --push -t $IMAGE .
gcloud run deploy bot  --image $IMAGE:latest --project secretscout --region us-central1
