# Get MobileCLIP2 working (online mode)

MobileCLIP2 runs on the **backend server**, not inside the APK. The APK's offline
mode is EfficientNet-Lite0 (ImageNet) only.

## 1. Deploy the backend
**Render (uses render.yaml in this repo)**
1. Go to render.com > New > Blueprint > pick this GitHub repo.
2. Deploy. The first build is slow (it downloads a ~398 MB model).
3. Open the service > Environment, copy the value of `EDGECASE_ACCESS_TOKEN`.

Note: the free 512 MB plan will probably run out of memory with MobileCLIP2-S2.
Use a paid plan, or Hugging Face Spaces (Docker) with 16 GB RAM on the free tier.

## 2. Check it
Open `https://YOUR-URL/health`. You should see `"providerConfigured": true`
and `"model": "MobileCLIP2-S2"`.

## 3. Connect the app
App > Settings > enter the backend URL (https) and the token > run the
connection test > turn on online mode. The phone needs internet.

## 4. Add your products (optional, for exact SKU matches)
1. Put photos in `catalog/images/`.
2. Fill `catalog/products.csv` (product_id, name, image_path, ...).
3. Run: `python index_catalog.py --csv catalog/products.csv --root catalog --output catalog/catalog_embeddings.pt`
4. Redeploy.

## Clean up committed junk (run in the repo folder)
```
git rm --cached *.pyc
git add .gitignore
git commit -m "Remove compiled files"
git push
```
