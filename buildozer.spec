[app]

# ════════════════════════════════════════
#  配音工具 - Android APK 打包配置
#  基于 Buildozer + Kivy 2.3.1
# ════════════════════════════════════════

# ── 应用基本信息 ──
title = 配音工具
package.name = dubbingtool
package.domain = com.tts.dubbing
source.dir = .
version = 1.0.0

# ── 入口文件 ──
main.py = main.py

# ── 包含文件类型 ──
source.include_exts = py,png,jpg,jpeg,kv,atlas,wav,mp3,ttf,otf

# ── Python 依赖 (pip 包) ──
requirements = python3,kivy==2.3.1,kivymd==1.2.0,edge-tts==7.2.8,python-docx==1.1.2,requests==2.32.0,Pillow==11.0.0,aiohttp==3.10.0

# ── P4A 配方 (Android 编译依赖) ──
# android.recipe.blacklist = openssl,sqlite3

# ── 屏幕方向 ──
orientation = portrait
fullscreen = 0

# ── Android 权限 ──
android.permissions = INTERNET,ACCESS_NETWORK_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_AUDIO

# ── Android 功能声明 ──
android.features = android.hardware.audio.output

# ── Meta 数据 ──
android.meta_data = \
    com.google.android.play.core.assetpacks.versionCode=1

# ── 构建设置 ──
# Android API 级别 (target=33, min=26 覆盖 95% 设备)
android.api = 33
android.minapi = 26

# NDK 版本
android.ndk = 25b

# SDK 版本
android.sdk = 33

# CPU 架构 (arm64-v8a 覆盖主流设备; 加 armeabi-v7a 覆盖旧设备)
android.arch = arm64-v8a

# 启用 AndroidX
android.enable_androidx = true

# Java 编译选项
android.gradle_dependencies = androidx.core:core:1.9.0

# ── 签名 ──
# 发布时取消注释并填入密钥信息
# android.release = 1
# android.keystore = release.keystore
# android.keyalias = dubbingtool
# android.keystore_password = your_password
# android.keyalias_password = your_password

# ── 图标与启动画面 ──
# 将 icon.png (512x512) 放在项目根目录
# icon.filename = icon.png

# 启动画面
# presplash.filename = splash.png
# presplash.color = FAE5E5

# ── 日志过滤 ──
android.logcat_filters = *:S python:D

# ── 额外源码目录 ──
android.add_src =

# ── 编译优化 ──
android.allow_backup = true

[buildozer]

# ── 构建工具设置 ──

# 日志级别: 0=静默, 1=基本信息, 2=详细
log_level = 2

# 警告 root 用户
warn_on_root = 1

# 超时设置 (秒)
build_timeout = 3600

# 构建目录
build_dir = .buildozer
