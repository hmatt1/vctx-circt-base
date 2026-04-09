#!/usr/bin/env bash
set -euo pipefail

IMAGE_TAG="${IMAGE_TAG:-circt-hello-base:latest}"

docker build \
  -f docker/base/Dockerfile \
  -t "$IMAGE_TAG" \
  .

echo "Built $IMAGE_TAG"
