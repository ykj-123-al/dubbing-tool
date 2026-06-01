[app]
# ==============================================
# Dubbing Tool - Android APK Build Config
# Buildozer + Kivy 2.3.1
# ==============================================

# ---- Basic Info ----
title = DubbingTool
package.name = dubbingtool
package.domain = com.tts.dubbing
source.dir = .
version = 1.0.0

# ---- Entry Point ----
main.py = main.py

# ---- Included Files ----
source.include_exts = py,png,jpg,jpeg,kv,atlas,wav,mp3,ttf,otf

# ---- Python Dependencies ----
requirements = python3,kivy==2.3.1,kivymd==1.2.0,edge-tts==7.2.8,python-docx==1.1.2,requests==2.32.0,Pillow==11.0.0,aiohttp==3.10.0

# ---- Screen Orientation ----
orientation = portrait
fullscreen = 0

# ---- Android Permissions ----
android.permissions = INTERNET,ACCESS_NETWORK_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_AUDIO

# ---- Build Settings ----
android.api = 33
android.minapi = 26

android.ndk = 25b

android.archs = arm64-v8a

android.enable_androidx = true

android.accept_sdk_license = True

android.gradle_dependencies = androidx.core:core:1.9.0

android.logcat_filters = *:S python:D

android.allow_backup = true

# ---- Signing (uncomment for release) ----
# android.release = 1
# android.keystore = release.keystore
# android.keyalias = dubbingtool
# android.keystore_password = your_password
# android.keyalias_password = your_password

[buildozer]

log_level = 2

warn_on_root = 1

build_timeout = 3600

build_dir = .buildozer
