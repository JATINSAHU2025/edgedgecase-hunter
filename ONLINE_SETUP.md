# Online recognition and catalog setup

This project uses MobileCLIP2-S2 in the backend by default. The Android app sends a captured image to the configured HTTPS `/classify` endpoint only when online recognition is enabled. The backend keeps the model and any provider credentials on the server.

## 1. Deploy the backend

Follow [`backend/README.md`](backend/README.md). The standard setup uses Docker and requires:

- `VISION_PROVIDER=mobileclip2`
- `EDGECASE_ACCESS_TOKEN` set to a long random token
- A host with enough RAM, disk, and outbound access to download/run the approximately 398 MB MobileCLIP2-S2 checkpoint during image build

The backend uses CPU inference by default. First model initialization and CPU inference may take time. Do not assume the service is ready until `/health` responds successfully and a real `/classify` request has been tested.

## 2. Add product reference photos for better precision

General category recognition can identify likely objects but cannot guarantee exact SKU, dimensions, or price. To search your actual products, populate `backend/catalog/products.csv` and `backend/catalog/images/`, then generate `catalog_embeddings.pt` with `backend/index_catalog.py`. Detailed instructions are in [`backend/README.md`](backend/README.md).

## 3. Build and install the Android app

From PowerShell in the Android project root:

```powershell
.\gradlew.bat testDebugUnitTest assembleDebug
```

If that succeeds, install `app\build\outputs\apk\debug\app-debug.apk` on your phone. This source ZIP does not include a newly built APK.

## 4. Configure the app

1. Get the public HTTPS backend base URL.
2. Open EdgeCase Hunter AI → Settings → Online Vision Provider.
3. Enter the backend base URL and the exact same `EDGECASE_ACCESS_TOKEN` configured on the server.
4. Save the settings and test the backend connection.
5. Enable online identification and scan a product.

The app appends `/classify`; the connection check uses `/health`. HTTP 502/503 responses should be diagnosed from the server logs, especially during model initialization.

## Security

The demo access token stored by the Android app is not a production secret. Keep provider credentials on the server. Public deployments need user authentication, quotas, rate limiting, abuse monitoring, and careful handling of uploaded images.

## Offline behavior

Offline recognition remains available through EfficientNet-Lite0 / ImageNet-1K. MobileCLIP2-S2 is used by the online backend in this package and is not yet bundled for on-device Android inference.
