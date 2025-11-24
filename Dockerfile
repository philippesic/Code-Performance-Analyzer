# ========================
# Base image: NVIDIA PyTorch
# ========================
FROM pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime

ENV DEBIAN_FRONTEND=noninteractive

# ========================
# System dependencies (minimal)
# ========================
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl wget ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ========================
# Working directory
# ========================
WORKDIR /app

# ========================
# Install Python dependencies first (better caching)
# ========================
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ========================
# Hugging Face cache configuration
# ========================
ENV HF_HOME=/root/.cache/huggingface
ENV TRANSFORMERS_CACHE=/root/.cache/huggingface/transformers
ENV HF_HUB_DISABLE_SYMLINKS_WARNING=1

# ========================
# Copy project source
# ========================
COPY src/ src/

# ---- ADD THIS LINE ----
RUN echo "--- START serve.py ---" && cat src/model/serve.py && echo "--- END serve.py ---"
# -----------------------
# ========================
# Environment variables
# ========================
ENV PYTHONPATH=/app/src
ENV CUDA_VISIBLE_DEVICES=0
ENV PORT=5000

# ========================
# Expose port
# ========================
EXPOSE 5000

# ========================
# Create non-root user
# ========================
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# ========================
# Healthcheck endpoint
# ========================
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s CMD curl -f http://localhost:5000/health || exit 1

# ========================
# Default command: Uvicorn production-ready
# ========================
CMD ["uvicorn", "model.serve:app", "--host", "0.0.0.0", "--port", "5000", "--workers", "2", "--timeout-keep-alive", "3600", "--log-level", "info"]
