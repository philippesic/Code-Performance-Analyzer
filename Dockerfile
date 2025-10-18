# ========================
# Base image: NVIDIA PyTorch
# ========================
FROM pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime

# Prevent interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive

# ========================
# System dependencies
# ========================
RUN apt-get update && apt-get install -y \
    git curl wget vim build-essential python3-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# ========================
# Python dependencies
# ========================
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ========================
# Hugging Face setup
# ========================
ENV HF_HOME=/root/.cache/huggingface
ENV TRANSFORMERS_CACHE=/root/.cache/huggingface/transformers
ENV HF_HUB_DISABLE_SYMLINKS_WARNING=1
# optionally mount a volume for persistent cache

# ========================
# Copy project source
# ========================
COPY src/ src/
COPY data/ data/
COPY models/ models/

# ========================
# Default environment
# ========================
ENV PYTHONPATH=/app/src
ENV CUDA_VISIBLE_DEVICES=0

# ========================
# Default command
# ========================
CMD ["bash"]
