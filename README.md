# CPA

Building Image:

PC (For Training): `docker build -t cpa .`

Mac: `docker build --platform=linux/amd64 -t cpa .`

Build Container:

PC: `docker run -it --name cpa-dev --gpus all -v $(pwd):/app -v ~/.cache/huggingface:/root/.cache/huggingface cpa bash`

Mac: `docker run -it --platform linux/amd64 --name cpa-dev -v $(pwd):/app -v ~/.cache/huggingface:/root/.cache/huggingface cpa bash`

Boot:

Boot container: `docker start -ai cpa-dev`
