# EdgeCase Hunter AI

Android visual-identification app (source version 1.0.1) with:
- On-device EfficientNet-Lite0 INT8 / ImageNet-1K classification.
- On-device text recognition and barcode/QR scanning.
- Five-section Compose UI, in-app CameraX capture, and local scan library.
- Raised central camera action placed outside the navigation Surface to prevent top-edge clipping, with Android navigation-bar insets respected.
- Optional HTTPS online visual identification through the included FastAPI backend.

## Build the Android app

Requirements: JDK 17+ and Android SDK platform 35. From Windows PowerShell, in this project folder:

```powershell
.\gradlew.bat testDebugUnitTest assembleDebug
```

If the build succeeds, the debug APK is `app\build\outputs\apk\debug\app-debug.apk`. On Windows, you can also double-click `BUILD_AND_TEST_WINDOWS.bat` to run unit tests and build the APK.

`local.properties` is machine-specific and intentionally excluded. Open the project in Android Studio to create it, or configure `ANDROID_HOME`. Do not pin `org.gradle.java.home` to another computer's JDK path.

## Online identification

The previous source had the Android `INTERNET` permission explicitly removed and did not implement a real online provider. This repaired source restores network permission and implements an HTTPS client, connection diagnostics, compressed image upload, and a FastAPI backend.

**Online identification still requires deployment and configuration.** The included backend defaults to MobileCLIP2-S2. Build/deploy `backend/` over public HTTPS, configure `EDGECASE_ACCESS_TOKEN`, install this Android source, then open Settings and enter the backend base URL and matching demo access token. The app appends `/classify`; the health check uses `/health`. Test the connection before enabling online identification. Online is opt-in and uploads the selected photo only when the user enables that mode and starts identification.

For product-level matching, also add your own product reference images and metadata and build the catalog embedding index as described in [`backend/README.md`](backend/README.md). Without this catalog, MobileCLIP2 returns likely hardware categories rather than exact SKUs. See [`ONLINE_SETUP.md`](ONLINE_SETUP.md) for deployment details.

For a private demo, the app stores the backend URL and demo token in app-private preferences. This is not a production-grade authentication arrangement. A public app needs real user authentication, server-side quotas, rate limiting, abuse monitoring, and careful secret management.

## Accuracy limitations

EfficientNet-Lite0 is a fixed 1,000-class ImageNet classifier and remains the offline fallback. Online MobileCLIP2-S2 can compare photos with hardware-oriented text labels and, when you configure a catalog index, with your own product reference images. Adding image files to the app does not retrain EfficientNet. Similarity is a ranking score, not a calibrated probability; evaluate on held-out photos before using matches for billing.

## Important implementation notes

- Camera and gallery images are resized before classification/upload to reduce peak memory use.
- Camera capture closes the CameraX `ImageProxy` in a `finally` block and surfaces decode errors instead of silently failing.
- The Android app build and device behavior must still be verified on a machine with Android SDK/build tools; this source handoff does not include a newly built APK.
- Backend validation tests: `python -m unittest discover -s backend -p "test_*.py" -v`.

## Third-party licenses

See `THIRD_PARTY_NOTICES.md`.


## MobileCLIP2-S2 online recognition

The online backend defaults to Apple's MobileCLIP2-S2, ranks a hardware-oriented vocabulary, and optionally searches precomputed embeddings for your catalog photos. The Android Similar tab can display catalog product metadata returned by the backend. The existing EfficientNet-Lite0 still powers the offline path; this ZIP does not yet convert MobileCLIP2 into an Android-native model.
