#!/bin/bash
set -e

echo "[INFO] Stopping and removing existing container (if any)..."
docker rm -f cpa-dev >/dev/null 2>&1 || true

echo "[INFO] Starting new container..."
docker run -it --platform linux/amd64 \
  --name cpa-dev \
  -v "$(pwd)":/app \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -w /app \
  -e HF_HOME=/root/.cache/huggingface \
  cpa bash
