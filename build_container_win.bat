@echo off
echo [INFO] Stopping and removing existing container (if any)...
docker rm -f cpa-dev >nul 2>&1

echo [INFO] Starting new container...
docker run -it --name cpa-dev --gpus all ^
  -v "%cd%":/app ^
  -v "%USERPROFILE%\.cache\huggingface":/root/.cache/huggingface ^
  -w /app ^
  -p 5000:5000 ^
  -e HF_HOME=/root/.cache/huggingface ^
  cpa bash
