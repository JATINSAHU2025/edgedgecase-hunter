# Hardware catalog images

Place clear product reference photos under `catalog/images/`. Each row in `products.csv` must have a unique product_id, product name, and image_path relative to the `catalog/` folder (for example `images/basin_001.jpg`). Other columns are optional: sku, category, brand, dimensions, price.

Use multiple rows for multiple reference photos of the same SKU if you have different views; use the same product_id/SKU and a different image_path. The index will keep each reference image as an individual candidate, so consolidate duplicates in your catalog workflow if desired.

From the backend directory, after the MobileCLIP2 dependencies and checkpoint are available, run:

```bash
python index_catalog.py --csv catalog/products.csv --root catalog --output catalog/catalog_embeddings.pt
```

Then set `CATALOG_EMBEDDINGS_PATH=catalog/catalog_embeddings.pt`. Similarity is a ranking score, not a probability. Calibrate `CATALOG_MIN_SIMILARITY` with held-out photos before using results for billing.
