FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080 HF_HOME=/opt/hf-cache PIP_NO_CACHE_DIR=1 MOBILECLIP2_CHECKPOINT=/opt/model/mobileclip2_s2.pt CATALOG_EMBEDDINGS_PATH=/app/catalog/catalog_embeddings.pt
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
# Install CPU-only PyTorch to avoid pulling CUDA libraries into a small API container.
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch torchvision && \
    pip install --no-cache-dir -r requirements.txt
# Install Apple's MobileCLIP2 implementation with a compatible OpenCLIP version.

RUN git clone --depth 1 https://github.com/apple-aiml-research/ml-mobileclip.git /opt/ml-mobileclip && \
    git clone --depth 1 https://github.com/mlfoundations/open_clip.git /opt/open_clip && \
    cd /opt/open_clip && \
    git apply /opt/ml-mobileclip/mobileclip2/open_clip_inference_only.patch && \
    cp -r /opt/ml-mobileclip/mobileclip2/* /opt/open_clip/src/open_clip/ && \
    pip install --no-cache-dir -e /opt/open_clip && \
    pip install --no-cache-dir -e /opt/ml-mobileclip && \
    pip install --no-cache-dir git+https://github.com/huggingface/pytorch-image-models

# Bake the 398 MB official checkpoint into the backend image so the first app request does not need to download it.
RUN mkdir -p /opt/model && python -c "from huggingface_hub import hf_hub_download; import shutil; p=hf_hub_download(repo_id='apple/MobileCLIP2-S2', filename='mobileclip2_s2.pt'); shutil.copy2(p, '/opt/model/mobileclip2_s2.pt')"
COPY main.py mobileclip2_provider.py index_catalog.py ./
COPY catalog ./catalog
EXPOSE 8080
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
