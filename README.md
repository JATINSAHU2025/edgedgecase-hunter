# EdgeCase Hunter AI — MobileCLIP2-S2 backend

This backend preserves the Android app's `/classify` JSON contract and defaults to Apple's MobileCLIP2-S2 image-text model. The Dockerfile downloads the official checkpoint from Hugging Face during image creation and stores it at `/opt/model/mobileclip2_s2.pt`. When running outside Docker, the provider can download it on first use and cache it under `HF_HOME`.

## What it does

- Receives the photo captured by the existing Android camera flow.
- Compares the photo against a curated hardware-category vocabulary using MobileCLIP2-S2.
- Returns the best category plus four alternatives and a qualitative uncertainty estimate.
- Optionally ranks your own product reference images and returns SKU/brand/size/price metadata from a precomputed catalog index.
- Does not save uploaded photos.

**Important limitation:** this is zero-shot category matching, not exact SKU identification. Exact brand, dimensions, and product price require your own catalog images and metadata. The app's existing EfficientNet-Lite0 remains the offline fallback; this backend adds MobileCLIP2 to the online path. MobileCLIP2 is not embedded into the APK by this change.

## Add your own hardware catalog (recommended for accuracy)

Put reference images under `catalog/images/` and fill `catalog/products.csv` with columns `product_id,sku,name,category,brand,dimensions,price,image_path`. The `image_path` is relative to the catalog folder, e.g. `images/basin_001.jpg`. Use real product photos and include multiple views where available.

After installing the backend dependencies and making the model checkpoint available, build the image index from the backend directory:

```bash
python index_catalog.py --csv catalog/products.csv --root catalog --output catalog/catalog_embeddings.pt
```

Set `CATALOG_EMBEDDINGS_PATH=catalog/catalog_embeddings.pt` and redeploy/mount the catalog index with the backend. The API returns up to five `matches` with product metadata. A similarity score is a ranking score, not a probability; calibrate `CATALOG_MIN_SIMILARITY` using a held-out set of real camera photos before relying on matches. If no catalog index is present, the backend continues with general hardware-category matching.

## Run / deploy

Use Docker; the image installs Apple's official `ml-mobileclip` implementation and the required OpenCLIP MobileCLIP2 patch. The Docker build downloads the official 398 MB `mobileclip2_s2.pt` checkpoint into the image, so the build needs outbound access to Hugging Face. The deployed image is correspondingly large; choose a host with enough disk and RAM.

Required environment variables:

```env
VISION_PROVIDER=mobileclip2
EDGECASE_ACCESS_TOKEN=use-a-long-random-token
RATE_LIMIT_REQUESTS_PER_MINUTE=12
CATALOG_EMBEDDINGS_PATH=catalog/catalog_embeddings.pt
CATALOG_MIN_SIMILARITY=0.20
```

Build and run:

```bash
docker build -t edgecase-mobileclip2 .
docker run --rm -p 8080:8080 \
  -e VISION_PROVIDER=mobileclip2 \
  -e EDGECASE_ACCESS_TOKEN='your-long-random-token' \
  -v edgecase-hf-cache:/opt/hf-cache edgecase-mobileclip2
```

Check `GET /health` with `Authorization: Bearer <token>`. The app endpoint is `POST /classify` with `imageBase64` and `mimeType`, as before.

### Optional Gemini fallback

Set `VISION_PROVIDER=gemini` and `GEMINI_API_KEY` to use the previous Gemini-based backend instead. Do not put provider keys in the Android app.

## Resource note

MobileCLIP2 uses PyTorch on CPU in this Docker setup. Model initialization and the first request take longer than later requests. Choose a backend host with enough RAM for PyTorch and the model; a very small free server may be unsuitable. No accuracy percentage is claimed for your hardware catalog until it is tested on real held-out photos.
