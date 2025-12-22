@echo off

echo Stopping port-forward processes...
REM Find all kubectl port-forward processes and terminate them
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq kubectl.exe" /v ^| findstr /i "port-forward"') do (
    echo Killing process ID %%i
    taskkill /PID %%i /F >nul 2>&1
)

echo Stopping cluster containers
docker stop mock-cloud-control-plane mock-cloud-worker

echo Stoppping registry
docker stop registry

echo Cluster stopped
pause
