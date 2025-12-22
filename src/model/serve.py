#!/usr/bin/env python3
import torch
import csv
import os
from datetime import datetime
import pathlib
import asyncio
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM


# Fix dual import for relative path for cluster vs dev container
try:
    from .performance_test_generator import PerformanceTestGenerator
except ImportError:
    from performance_test_generator import PerformanceTestGenerator

# Fix cluster path
BASE_DIR = pathlib.Path(__file__).parent
MODEL_PATH = BASE_DIR / "models" / "student" / "cpa"

# paths for export feature
EXPORT_DIR = BASE_DIR / "exported_results"
EXPORT_FILE = EXPORT_DIR / "analysis_result.csv"

# create directory for results
os.makedirs(EXPORT_DIR, exist_ok=True)

# initialize csv export file wit headers
if not EXPORT_FILE.exists():
    with open(EXPORT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'code', 'complexity', 'execution_time_ms'])
# ---------------------------

MAX_INPUT_LENGTH = 512

print(f"Loading model from: {MODEL_PATH}")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH, use_fast=True, local_files_only=True
)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH, torch_dtype=torch.float16, local_files_only=True
)
torch.backends.cudnn.benchmark = True
model.to(device)
model.eval()
# model = torch.compile(model) # torch.compile() causes asyncio deadlock
 
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# Warmup
print("Warming up model...")
warmup = tokenizer("warmup", return_tensors="pt", padding=True)
warmup = {k: v.to(device) for k, v in warmup.items()}
with torch.inference_mode():
    _ = model.generate(
        warmup["input_ids"],
        attention_mask=warmup["attention_mask"],
        max_new_tokens=1,
        do_sample=False,
        use_cache=True,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id
    )
print("Model ready.")

app = FastAPI()
test_generator = PerformanceTestGenerator()

# Request schemas
class CodeRequest(BaseModel):
    code: str
    complexity: str = ""

def save_results(code: str, complexity: str, execution_time: float = 0.0):
    """ Save analysis result to CSV file for analysis export featyre - non-blocking"""
    try:
        with open(EXPORT_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            timestamp = datetime.now().strftime('%Y=%m-%d %H:%M:%S')
            code = code.replace('\n', '\\n').replace('\r', '')
            writer.writerow([timestamp, code, complexity, execution_time])
    except Exception as e:
        print(f"[WARNING] Failed to save result to CSV file: {e}")

def run_analysis(code_snippet: str) -> dict:

    prompt = (
        f"Analyze the following Python function and respond ONLY with its Big-O time complexity:\n\n"
        f"{code_snippet}\nComplexity:"
    )

    try:
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=MAX_INPUT_LENGTH,
            padding=True
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.inference_mode():
            output_ids = model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_new_tokens=16,
                do_sample=False,
                use_cache=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )

        decoded = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        complexity = decoded[len(prompt):].strip().split("\n")[0]

        save_results(code_snippet, complexity)
        return {"complexity": complexity}

    except Exception as e:
        print(f"[ERROR] {e}")
        raise e

def run_generate_test(code_snippet: str, complexity_hint: str) -> dict:
    try:
        if not complexity_hint:
            result_json = run_analysis(code_snippet)
            complexity_hint = result_json.get("complexity", "O(unknown)")

        test_file_content = test_generator.generate_test_file(code_snippet, complexity_hint)
        if not test_file_content:
            raise ValueError("Failed to generate test file. Ensure the code contains a valid function definition.")

        func_info = test_generator.extract_function_info(code_snippet)
        function_name = func_info['name'] if func_info else "unknown"

        return {
            "test_file": test_file_content,
            "complexity": complexity_hint,
            "function_name": function_name,
            "message": f"Performance test generated for {function_name} with complexity {complexity_hint}"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e


@app.post("/analyze")
def analyze(req: CodeRequest):  # sync
    code_snippet = req.code.strip()
    if not code_snippet:
        raise HTTPException(status_code=400, detail="Missing 'code' field")

    if device.type == 'cuda':
        # No async or hb on gpu
        print("Using Fast (GPU) inference") # Only on dev container
        try:
            result = run_analysis(code_snippet)
            return result
        except Exception as e:
            print(f"[ERROR] {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    else:
        # Slow inference fix: Hearbeat by streaming spaces to maintain connection
        print("Using Slow (CPU) inference with heartbeats") # Kind does not support gpu cluster
        
        async def analysis_generator():
            loop = asyncio.get_event_loop()
            analysis_task = loop.run_in_executor(None, run_analysis, code_snippet)
            
            try:
                while True:
                    try:
                        # Pulse
                        result = await asyncio.wait_for(asyncio.shield(analysis_task), timeout=15.0)
                        yield json.dumps(result)
                        break
                    except asyncio.TimeoutError:
                        yield " "
            except Exception as e:
                print(f"[ERROR] {e}")
                error_response = {"detail": str(e)}
                yield json.dumps(error_response)

        return StreamingResponse(analysis_generator(), media_type="application/json")



@app.post("/generate-test")
def generate_test(req: CodeRequest):
    code_snippet = req.code.strip()
    complexity_hint = req.complexity.strip()

    if not code_snippet:
        raise HTTPException(status_code=400, detail="Missing 'code' field")
    
    # GPU vs CPU split path for tests
    if device.type == 'cuda':
        print("Using Fast (GPU) inference")
        try:
            result = run_generate_test(code_snippet, complexity_hint)
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            print(f"[ERROR] {e}")
            raise HTTPException(status_code=500, detail=str(e))
            
    else:
        print("Using Slow (CPU) inference with heartbeats")
        
        async def test_generator_stream():
            loop = asyncio.get_event_loop()
            test_task = loop.run_in_executor(None, run_generate_test, code_snippet, complexity_hint)
            
            try:
                while True:
                    try:
                        result = await asyncio.wait_for(asyncio.shield(test_task), timeout=15.0)
                        yield json.dumps(result)
                        break 
                    except asyncio.TimeoutError:
                        yield " "
            except ValueError as e:
                error_response = {"detail": str(e)}
                yield json.dumps(error_response)
            except Exception as e:
                print(f"[ERROR] {e}")
                error_response = {"detail": str(e)}
                yield json.dumps(error_response)

        return StreamingResponse(test_generator_stream(), media_type="application/json")


@app.get("/health")
async def health():  # async since we ping periodically
    return {"status": "ok"}


# New endpoints for export feature
@app.get("/download-results")
async def download_results():
    """Downloads analysis results as CSV"""
    from fastapi.responses import FileResponse
    
    if not EXPORT_FILE.exists():
        raise HTTPException(status_code=404, detail="No results found")

    return FileResponse(
        path=str(EXPORT_FILE),
        media_type='text/csv',
        filename=f'cpa_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.post("/clear-results")
async def clear_results():
    """Clears all the saved results"""
    try:
        with open(EXPORT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'code', 'complexity', 'execution_time_ms'])
        return {"message": "Results cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=505, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Server running at http://0.0.0.0:5000")
    uvicorn.run(
        "model.serve:app",
        host="0.0.0.0",
        port=5000,
        log_level="info",
        reload=False,
        workers=1  # Cuda deadlocks with multiple workers in dev container
    )