plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
}

val onlineEndpoint: String =
    (project.findProperty("ONLINE_CLASSIFIER_ENDPOINT") as String?)?.trim().orEmpty()
val onlineClientToken: String =
    (project.findProperty("ONLINE_CLASSIFIER_CLIENT_TOKEN") as String?)?.trim().orEmpty()
val onlineConfigured = onlineEndpoint.startsWith("https://", ignoreCase = true) && onlineClientToken.isNotBlank()

android {
    namespace = "com.edgecasehunter.ai"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.edgecasehunter.ai"
        minSdk = 26
        targetSdk = 35
        versionCode = 2
        versionName = "1.0.1"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables { useSupportLibrary = true }

        buildConfigField("boolean", "ONLINE_CLASSIFIER_ENABLED", onlineConfigured.toString())
        buildConfigField("String", "ONLINE_CLASSIFIER_ENDPOINT", "\"${onlineEndpoint.replace("\"", "")}\"")
        buildConfigField("String", "ONLINE_CLASSIFIER_CLIENT_TOKEN", "\"${onlineClientToken.replace("\"", "")}\"")
        buildConfigField("String", "MODEL_ASSET_NAME", "\"models/efficientnet_lite0_int8_2.tflite\"")
        buildConfigField("String", "MODEL_DISPLAY_NAME", "\"EfficientNet-Lite0 INT8 (ImageNet-1K)\"")
        buildConfigField(
            "String",
            "MODEL_SOURCE_URL",
            "\"https://storage.googleapis.com/download.tensorflow.org/models/tflite/task_library/image_classification/android/efficientnet_lite0_int8_2.tflite\""
        )
        buildConfigField("String", "MODEL_REVISION", "\"efficientnet_lite0_int8_2\"")
        buildConfigField("String", "MODEL_SHA256", "\"AA03E4017F54FD5C743BD397B0A3E136FAB0942F9C7CD715064A31CA3E4FC996\"")
        buildConfigField("int", "MODEL_INPUT_SIZE", "224")
        buildConfigField("int", "TOP_K", "5")

        ndk {
            abiFilters += listOf("armeabi-v7a", "arm64-v8a", "x86_64")
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.getByName("debug")
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
        debug {
            isDebuggable = true
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    buildFeatures {
        compose = true
        buildConfig = true
    }
    androidResources {
        noCompress += "tflite"
    }
    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
    testOptions {
        unitTests.isIncludeAndroidResources = false
    }
}

dependencies {
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.lifecycle.viewmodel.compose)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    implementation(libs.androidx.material.icons.extended)
    implementation(libs.androidx.camera.core)
    implementation(libs.androidx.camera.camera2)
    implementation(libs.androidx.camera.lifecycle)
    implementation(libs.androidx.camera.view)
    implementation(libs.mlkit.text.recognition)
    implementation(libs.mlkit.barcode.scanning)
    implementation(libs.kotlinx.coroutines.android)
    implementation(libs.tensorflow.lite.task.vision)
    implementation(libs.androidx.exifinterface)

    testImplementation(libs.junit)
    testImplementation("org.json:json:20240303")
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    debugImplementation(libs.androidx.ui.tooling)
}
