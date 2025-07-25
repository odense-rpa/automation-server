#!/bin/bash
# Build Playwright worker image

echo "Building Playwright worker image..."
docker build --target worker-playwright -t automation-server-worker-playwright:0.2.0 .
echo "Playwright worker image built successfully!"
echo "Tagged as: automation-server-worker-playwright:0.2.0"