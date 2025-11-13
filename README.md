# CPA

Test Model: `python src/complexity.py <code>`

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

Teacher: deepseek-coder-v2:16b

Push: Run push_model
Pull: `cd models/student && git clone https://huggingface.co/philippesic/cpa`

## INTEGRATION (Juan):
For integration I created a stub server that serves the same response as the backend does, this way I avoid waiting times and downloading the whole fine-tuned model on my laptop. This is not to be used in reality. 
- To finish integrating, **update the `API_BASE_URL` constant in `./code-performance-analyzer/src/extension.ts` to the url of the backend server.**

## Running the frontend:
To run the frontend:
1. Setup and run the backend.
2. In the `./code-performance-analyzer` directory, run: `npm run compile`.
3. In visual studio open `./code-performance-analyzer/src/extension.ts`.
4. In visual studio, press F5 or trigger the "Debug: Start Debugging" while having the `extension.ts` file open. Visual studio will open a new window in the `test-code-performance-analyzer` directory, with the extension loaded in the environment.
5. Trigger the commands you want in the new debug window, there is a sample python function to quickly test the outputs.