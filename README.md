# CPA

Building Image:

PC (For Training): `docker build -t cpa .`

Mac: `docker build --platform=linux/amd64 -t cpa .`

Build Container:

PC (Powershell NOT BASH): `docker rm -f cpa-dev
docker run -it --name cpa-dev --gpus all ^
  -v "%cd%":/app ^
  -v "%USERPROFILE%\.cache\huggingface":/root/.cache/huggingface ^
  -w /app ^
  cpa bash
`

Mac: `docker rm -f cpa-dev &&  docker run -it --platform linux/amd64 --name cpa-dev -v $(pwd):/app -v ~/.cache/huggingface:/root/.cache/huggingface cpa bash`

Models:

Complexity Model: starcoder2:3b

Push: Run push_model
Pull: `cd models/student && git clone https://huggingface.co/philippesic/cpa`

Teacher: deepseek-coder-v2:7b
