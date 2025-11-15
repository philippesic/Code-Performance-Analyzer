serve.py:

1: Serve the model over htp by running serve.py as a detatched process `nohup python src/serve.py > server.log 2>&1 &`
2: Ping over htp. Using curl:
`curl -X POST http://127.0.0.1:5000/analyze -H "Content-Type: application/json" -d '{"code": "def loop(n):\n for i in range(n): pass"}'`

Extension team ping through your code and function snapshots

3: Returns a json object like:
`{"complexity":"O(n)"}`

4: Kill the server via `kill <pid>`

Notes:

Inference will take a LONG time, like minutes. I'm working on improvements, but this will do for our demo.
Port mapping is setup for use within the container, so you'll probably get an error pinging through another shell.



source files:

# todo