@echo off
echo.
echo   Updating Kubernetes Cluster
echo.

set IMAGE_NAME=cpa-dev
set DEPLOYMENT=cpa-dev
set CONTAINER=cpa-dev
set TAG=latest
set CLUSTER_NAME=mock-cloud

echo Building Docker image
docker build -t %IMAGE_NAME%:%TAG% . 
REM --no-cache when building code only changes
if %ERRORLEVEL% neq 0 goto error

echo Loading image into Kind cluster (This will take a LONG time, do not exit)
kind load docker-image %IMAGE_NAME%:%TAG% --name %CLUSTER_NAME%
if %ERRORLEVEL% neq 0 goto error

echo Restarting cluster, port forwaring may mess up, so restart manually if needed
kubectl rollout restart deployment/%DEPLOYMENT%
if %ERRORLEVEL% neq 0 goto error

echo.
echo   Pods Starting
echo.
pause
exit /b 0

:error
echo.
echo Something went wrong!
echo Check the output above for details
pause
exit /b 1