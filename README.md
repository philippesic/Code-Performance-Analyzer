# CPA

Building Image:

PC (For Training): `docker build -t cpa .`

Mac: `docker build --platform=linux/amd64 -t cpa .`

--

Build Container:

PC: `run_container_win.bat`

Mac: `run_container_mac.sh`

--

Reenter Container:

`docker start -ai cpa-dev`

Models:

Complexity Model: starcoder2:3b

Push: Run push_model
Pull: `cd models/student && git clone https://huggingface.co/philippesic/cpa`

Teacher: deepseek-coder-v2:7b
