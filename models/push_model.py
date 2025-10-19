from huggingface_hub import HfApi
api = HfApi()
api.upload_folder(
    folder_path="models/student",
    repo_id="philippesic/cpa",
    repo_type="model"
)
