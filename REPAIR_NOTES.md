# Repair notes — EdgeCase Hunter AI

## Changes made in this source package

1. Restored `android.permission.INTERNET` and declared network-state permission. The original manifest contained a manifest-merger instruction removing `INTERNET`.
2. Replaced the always-unconfigured online-provider selection with an HTTPS client that can be configured in-app and reports useful timeout, DNS, TLS, authentication, rate-limit and backend errors.
3. Added an optional FastAPI backend that keeps the Gemini API key server-side, uses the current Gemini Interactions REST API, normalizes output into the Android result schema, checks input MIME signatures and sizes, and avoids persisting image files.
4. Added endpoint/token fields and a connection test in Settings. Online mode remains opt-in.
5. Bounds camera/gallery images to reduce memory usage; closes CameraX `ImageProxy` in a `finally` block; checks null image decodes; handles memory errors more clearly; fixes the camera-switch preview surface.
6. Avoids treating the online model's qualitative result as a fake calibrated percentage; online alternatives do not display invented numeric confidence values.
7. Removed the computer-specific JDK path from `gradle.properties` and excluded `local.properties`/APKs from the repair source package.
8. Fixed the raised central camera button in bottom navigation: it is now a sibling of the clipped navigation Surface, the parent reserves space for the whole 60dp control, tab widths are balanced, and navigation-bar insets are respected.
9. Incremented Android `versionCode` to 2 and `versionName` to 1.0.1 for the next build.

## Validation performed

- Backend Python files compile with `py_compile`.
- Six backend validation/unit tests passed locally.
- Kotlin source was run through the Kotlin compiler parser; no Kotlin syntax/“expecting” errors were reported, but semantic Android compilation cannot be validated without the Android and Compose dependency classpaths.
- The Android APK was **not rebuilt or run in this environment**. This runtime does not have an Android SDK/platform installed, and external downloads are unavailable here. The APK inside the user's source archive is not included in the repaired-source ZIP and must not be treated as an updated build.

## Required remaining steps

1. Build in Android Studio or on a Windows machine with JDK 17+ and Android SDK platform 35: `gradlew.bat testDebugUnitTest assembleDebug`.
2. Install the *newly built* APK and test camera/gallery capture, offline classification, history and crash stability on the actual phone.
3. Deploy `backend/` over public HTTPS and configure server-side `GEMINI_API_KEY` and `EDGECASE_ACCESS_TOKEN`.
4. In app Settings, configure the backend base URL and matching demo token, run the connection test, and only then try online identification.
5. Test with real images such as a washbasin, tap, valve and common household objects; exact naming is not guaranteed by either model.

The demo token design is intended only for private testing. A public app requires proper authentication, quotas/rate limits and abuse monitoring.
