#!/bin/bash
# Build standard worker image

echo "Building standard worker image..."
docker build --target worker -t automation-server-worker:0.3.1 .
echo "Standard worker image built successfully!"
echo "Tagged as: automation-server-worker:0.3.1"