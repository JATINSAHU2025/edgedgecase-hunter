# Third-party notices

## EfficientNet-Lite0 TensorFlow Lite model

- Artifact: `efficientnet_lite0_int8_2.tflite`
- Bundled path: `app/src/main/assets/models/efficientnet_lite0_int8_2.tflite`
- Source URL: https://storage.googleapis.com/download.tensorflow.org/models/tflite/task_library/image_classification/android/efficientnet_lite0_int8_2.tflite
- Official Android example that downloads this file: https://github.com/tensorflow/examples/blob/master/lite/examples/image_classification/android/app/download_models.gradle
- Revision name: `efficientnet_lite0_int8_2`
- SHA-256: `AA03E4017F54FD5C743BD397B0A3E136FAB0942F9C7CD715064A31CA3E4FC996`
- Size: 5,434,493 bytes
- Labels: 1,000 ImageNet-1K class names from model metadata (`labels_without_background.txt`)
- License: Apache License 2.0 (TensorFlow / TensorFlow Lite model distribution)
- Dataset used to train the original model: ImageNet-1K. ImageNet itself is not redistributed in this app.

## TensorFlow Lite Task Vision

- Artifact: `org.tensorflow:tensorflow-lite-task-vision:0.4.4`
- License: Apache License 2.0

## Published ImageNet accuracy (not measured by this app)

From https://github.com/tensorflow/tpu/blob/master/models/official/efficientnet/lite/README.md
and https://blog.tensorflow.org/2020/03/higher-accuracy-on-vision-models-with-efficientnet-lite.html:

- EfficientNet-Lite0 FP32 ImageNet top-1: 75.1%
- EfficientNet-Lite0 INT8 ImageNet top-1: 74.4%
- Evaluation notes in that table: ImageNet, checkpoints containing FP and post-training quantized INT8 TFLite files; CPU/GPU/TPU latency measured on Pixel 4 with batch size 1 and 4 CPU threads.

This application does not re-run ImageNet validation and does not claim those numbers as a result of this APK.

## ImageNet-C

ImageNet-C (Hendrycks & Dietterich) is an optional external robustness benchmark. It is not bundled here. This app does not report ImageNet-C scores.

## AndroidX / Kotlin / JUnit

AndroidX libraries, Kotlin, and JUnit are used under their respective Apache 2.0 / EPL licenses as distributed by Google and JetBrains.
