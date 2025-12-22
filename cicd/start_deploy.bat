@echo off

echo Starting registry
docker start registry 2>nul || (
    echo Registry not found, createing new
    docker run -d -p 5000:5000 --restart=always --name registry registry:2
)

echo Starting cluster
kind get clusters | findstr /i mock-cloud >nul
if %ERRORLEVEL%==0 (
    echo Cluster exists, starting containers
    docker start mock-cloud-control-plane mock-cloud-worker
) else (
    echo Cluster not found, creating new cluster
    kind create cluster --config kind-config.yaml --name mock-cloud
)

echo Checking image (Note image updates must be done manually vio update_cluster.bat)
docker image inspect localhost:5000/cpa-dev:latest >nul 2>&1
if %ERRORLEVEL%==0 (
    echo Image exists, skipping rebuild
) else (
    echo Image not found, building and pushing
    docker build -t cpa-dev:latest .
    docker tag cpa-dev:latest localhost:5000/cpa-dev:latest
    docker push localhost:5000/cpa-dev:latest
)

echo Deploying
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

echo Waiting for pod
kubectl wait --for=condition=ready pod -l app=cpa-dev --timeout=120s

echo Starting port-forward
start /B cmd /c kubectl port-forward svc/cpa-dev 5000:5000


echo Ready, you can now access http://127.0.0.1:5000
pause
