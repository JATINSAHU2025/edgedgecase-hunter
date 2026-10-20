# Accurate Camera Recognition — Implementation Status

## Implemented in this source package
- Preserved the existing Android camera capture and result-screen flow.
- Added an optional `CatalogMatch` model to the Android app.
- The online client parses catalog match records from `/classify`.
- The Similar tab displays product name, SKU, brand, dimensions, stored price, and raw visual similarity when returned by the backend.
- Added MobileCLIP2-S2 catalog image retrieval to the backend.
- Added `backend/catalog/products.csv` as a catalog template and `backend/index_catalog.py` to generate image embeddings.
- Multiple reference images for the same product are deduplicated in search results.
- Without a catalog index, the service still returns zero-shot hardware-category matches.
- Added server-side exception logging for MobileCLIP2 failures without exposing internal details to app clients.

## Required setup by you
1. Put your actual reference photos in `backend/catalog/images/`.
2. Fill `backend/catalog/products.csv` with product IDs, SKUs, names, image paths, and any available metadata.
3. Build the index using `python index_catalog.py --csv catalog/products.csv --root catalog --output catalog/catalog_embeddings.pt` from the backend directory after model dependencies/checkpoint are installed.
4. Configure `CATALOG_EMBEDDINGS_PATH` and deploy the backend.
5. Configure the Android app's HTTPS endpoint and access token using the existing project settings/build configuration.

## Verification status
- Backend Python syntax checks: passed.
- Backend unit tests: passed in this environment.
- Android Gradle build: not run because this environment does not have the Android SDK configured and this package contains the Windows wrapper script only.
- Real MobileCLIP2 model inference: not run here because the ~398 MB checkpoint and the patched model runtime were not downloaded/installed in this environment.
- Catalog matching accuracy: not measured because no hardware catalog photos were provided.

## Important limitations
- Similarity values are ranking scores, not calibrated probabilities.
- The default `CATALOG_MIN_SIMILARITY=0.20` is only a starting point; calibrate it with a held-out set of camera photos.
- Exact product recognition requires your own catalog images and trustworthy product metadata.
- Offline mode remains the existing EfficientNet-Lite0 fallback. MobileCLIP2 is used by the online backend in this package; it is not yet bundled for on-device Android inference.
