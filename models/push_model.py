import os
import time
import shutil
from dotenv import load_dotenv
from huggingface_hub import HfApi, upload_folder

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN") # Write Token
if not HF_TOKEN:
    raise ValueError("Missing HF_TOKEN in .env file")


LOCAL_MODEL_DIR = "models/student/base"
TMP_MODEL_DIR = "/tmp/student_model" 
REPO_ID = "philippesic/cpa"


os.environ["HF_HOME"] = "/tmp/hf_home" # Create cache outside of docker mount
os.environ["HF_HUB_CACHE"] = "/tmp/hf_cache"


if os.path.exists(TMP_MODEL_DIR):
    shutil.rmtree(TMP_MODEL_DIR)
print(f"Copying model to {TMP_MODEL_DIR} ...")
shutil.copytree(LOCAL_MODEL_DIR, TMP_MODEL_DIR)

api = HfApi(token=HF_TOKEN)

for attempt in range(3):
    try:
        print(f"Attempt {attempt+1}: Uploading from {TMP_MODEL_DIR}")
        upload_folder(
            repo_id=REPO_ID,
            folder_path=TMP_MODEL_DIR,
            repo_type="model",
            token=HF_TOKEN,
            commit_message="Upload tuned model",
            run_as_future=False
        )
        print("Upload complete.")
        break
    except Exception as e:
        print(f"Upload failed (attempt {attempt+1}): {e}")
        time.sleep(10)
else:
    print("Upload failed after 3 attempts")
