#!/usr/bin/env bash
# Script to build amd64 images and push to Docker Hub
set -euo pipefail

# Ensure the script runs from the project root directory
# This allows relative paths like 'docker/Dockerfile.server' to resolve correctly
cd "$(dirname "$0")/.."

# Load environment variables from .env if it exists
if [ -f .env ]; then
    set -a
    . .env
    set +a
fi

USERNAME="${DOCKER_USERNAME:-danielcyrus}"
PLATFORM="linux/amd64"
TAG="${IMAGE_TAG:-latest}"

echo "Checking Docker authentication..."
docker login

# Create and use a buildx builder if not already present
docker buildx create --use --name eyened-builder || docker buildx use eyened-builder

echo "Building and pushing for $PLATFORM (Tag: $TAG)..."

# Build and push Server
echo "==> Server"
docker buildx build --platform "$PLATFORM" -t "$USERNAME/eyened-server:$TAG" -f docker/Dockerfile.server --push . --provenance=false

# Build and push Client
echo "==> Client"
docker buildx build --platform "$PLATFORM" -t "$USERNAME/eyened-client:$TAG" -f docker/Dockerfile.client --push . --provenance=false

# Build and push Worker
echo "==> Worker"
docker buildx build --platform "$PLATFORM" -t "$USERNAME/eyened-worker:$TAG" -f docker/Dockerfile.worker --push . --provenance=false

echo "Successfully pushed all images to $USERNAME"