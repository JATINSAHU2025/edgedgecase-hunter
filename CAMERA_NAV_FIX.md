# Camera navigation icon clipping fix

## What changed

- Moved the raised Scan/camera action out of the navigation `Surface` and into an unclipped parent `Box`.
- Reserved 82dp for the whole bottom-navigation composition; the bar strip is 72dp high and sits 10dp below the top so the raised 60dp camera button is fully contained by the parent.
- Added `navigationBarsPadding()` to respect Android system navigation insets.
- Made four destination items share the remaining width evenly while preserving the centered Scan action.
- Kept a 60dp tap target and accessibility content description for Scan.
- Incremented Android version to `1.0.1` / versionCode `2` so the fixed build can be installed as an update when signing matches.

## Verification status

Source-level structure was inspected. The camera action is no longer offset outside the 72dp `Surface`, where Surface clipping could cut it off. A real APK build and device screenshot test are still required to verify appearance on the target phone.
