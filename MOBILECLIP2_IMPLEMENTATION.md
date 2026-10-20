# MobileCLIP2 implementation status

## Integrated in this source package
- Existing Android camera and capture flow remains unchanged.
- Online `/classify` can use MobileCLIP2-S2 through the backend.
- The backend returns the same JSON fields consumed by the app.
- The Docker image downloads the model checkpoint during image creation; non-Docker runs may download it on first use.
- Existing EfficientNet-Lite0 remains the offline fallback.

## Not yet completed
- MobileCLIP2 is not embedded in the APK. Apple publishes PyTorch model checkpoints; direct Android deployment requires a tested export/runtime path.
- No hardware catalog was provided, so the backend currently ranks curated hardware labels rather than matching exact product SKUs from catalog image embeddings.
- This package has not been built with Android Gradle or tested on a physical device in this environment.

## Acceptance test
1. Deploy backend with `VISION_PROVIDER=mobileclip2` and a strong `EDGECASE_ACCESS_TOKEN`.
2. Confirm `/health` reports `providerConfigured: true` and `model: MobileCLIP2-S2`.
3. Open the existing app camera, capture a hardware photo, and run online identification.
4. Test at least 50 representative hardware photos and record top-1/top-5 results.
5. Disable network and verify the existing EfficientNet-Lite0 offline fallback still runs.


## Catalog-based recognition update
- Added optional catalog-image retrieval using MobileCLIP2 image embeddings.
- Added `backend/catalog/products.csv` template and `backend/index_catalog.py` to precompute image embeddings.
- `/classify` can now return up to five catalog candidates including SKU, brand, dimensions, price, and raw cosine similarity.
- Android parses and displays catalog matches in the Similar tab.
- The catalog is optional; without it the service falls back to zero-shot hardware-category ranking.
- The default similarity threshold is only a starting point and must be calibrated with held-out photos.
