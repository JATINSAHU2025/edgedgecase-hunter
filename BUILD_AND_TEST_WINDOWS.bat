@echo off
setlocal
cd /d "%~dp0"
echo ================================================
echo EdgeCase Hunter AI - test and build debug APK
echo ================================================
echo.
echo Requirements: JDK 17+ and Android SDK Platform 35.
echo Android Studio should be closed if it is currently locking Gradle files.
echo.
call gradlew.bat testDebugUnitTest assembleDebug
if errorlevel 1 goto failed
if not exist "app\build\outputs\apk\debug\app-debug.apk" goto missing
 echo.
echo SUCCESS. Debug APK:
echo %CD%\app\build\outputs\apk\debug\app-debug.apk
echo.
pause
exit /b 0
:missing
echo Gradle completed but the APK file was not found at the expected path.
pause
exit /b 2
:failed
echo.
echo BUILD FAILED. Copy the first Gradle error and the final 50 lines of output for diagnosis.
pause
exit /b 1
