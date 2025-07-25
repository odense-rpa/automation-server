#!/bin/bash
# Build standard worker image

echo "Building standard worker image..."
docker build --target worker -t automation-server-worker:0.2.0 .
echo "Standard worker image built successfully!"
echo "Tagged as: automation-server-worker:0.2.0"