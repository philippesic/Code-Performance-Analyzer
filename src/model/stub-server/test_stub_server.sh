#!/bin/bash
echo "Pinging localhost:5000/analyze..."
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "for i in range(n):\n    print(i)"}'

echo "Pinging localhost:5000/health..."
curl http://localhost:5000/health
