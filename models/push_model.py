from huggingface_hub import HfApi, HfFolder, upload_folder
import os

def upload_model(local_model_dir, repo_id, commit_message="Upload StarCoder2 complexity model"):
    # Ensure auth token is available
    token = HfFolder.get_token()
    if token is None:
        raise RuntimeError("❌ No Hugging Face token found. Run `huggingface-cli login` first.")

    api = HfApi()

    print(f"📤 Uploading from: {local_model_dir}")
    print(f"📦 To Hugging Face repo: {repo_id}")

    # Create repo if it doesn’t exist
    try:
        api.create_repo(repo_id, token=token, exist_ok=True, private=False)
        print("✅ Repo ready.")
    except Exception as e:
        print(f"⚠️ Could not create repo: {e}")

    # Upload all model files
    upload_folder(
        folder_path=local_model_dir,
        repo_id=repo_id,
        token=token,
        path_in_repo="",
        commit_message=commit_message,
    )

    print("🎉 Upload complete!")

if __name__ == "__main__":
    LOCAL_MODEL_DIR = "models/student/base"
    REPO_ID = "philippesic/cpa"

    upload_model(LOCAL_MODEL_DIR, REPO_ID)
