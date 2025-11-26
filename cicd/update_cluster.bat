@echo off
echo.
echo   Updating Kubernetes Cluster Safely
echo.

set IMAGE_NAME=cpa-dev
set DEPLOYMENT=cpa-dev
set CLUSTER_NAME=mock-cloud
set TAG=latest

REM Clean old images in volumes so you don't use 1400gb of space like me
echo Cleaning up unused Docker artifacts
docker system prune -af --volumes
if %ERRORLEVEL% neq 0 echo Warning: Docker prune encountered issues

echo Building Docker image: %IMAGE_NAME%:%TAG%
docker build -t %IMAGE_NAME%:%TAG% .
if %ERRORLEVEL% neq 0 goto error

echo Loading image into cluster: %CLUSTER_NAME% (may take a few a LONG time)
kind load docker-image %IMAGE_NAME%:%TAG% --name %CLUSTER_NAME%
if %ERRORLEVEL% neq 0 goto error

for /F "tokens=*" %%i in ('docker ps -q --filter "name=%CLUSTER_NAME%-"') do (
    docker exec %%i /bin/sh -c "docker image prune -af > /dev/null 2>&1"
)

echo Restarting deployment: %DEPLOYMENT%
kubectl rollout restart deployment/%DEPLOYMENT%
if %ERRORLEVEL% neq 0 goto error

echo.
echo Pods are starting
pause
exit /b 0

:error
echo.
echo Something went wrong! Check the output above for details
pause
exit /b 1
