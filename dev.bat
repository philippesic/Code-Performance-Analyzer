@echo off
setlocal

set "IMAGE_NAME=cpa-dev:latest"
set "HOST_PORT=5000"
set "CONTAINER_PORT=5000"

echo Checking for image '%IMAGE_NAME%'...

REM Check if image exists
docker image inspect %IMAGE_NAME% >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Image not found. Building now
    docker build -t %IMAGE_NAME% .
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Docker build failed
        goto end
    )
    echo Image built successfully
) else (
    echo Image found
)

echo Container port %CONTAINER_PORT% will be available at http://127.0.0.1:%HOST_PORT%
echo Type 'exit' to leave the container
echo.

REM IMPORTANT: The --gpus all flag is for NVIDIA GPUs
REM If you do not have an NVIDIA GPU, REMOVE the '--gpus all' part of the command below
docker run -it --rm -p %HOST_PORT%:%CONTAINER_PORT% -v "%cd%\src:/app/src" --gpus all --entrypoint /bin/bash %IMAGE_NAME%

:end
echo.
pause