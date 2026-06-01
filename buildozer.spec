[app]

# éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²
#  é–°å¶‰ç…¶å®¸ãƒ¥å¿ - Android APK éµæ’³å¯˜é–°å¶‡ç–†
#  é©è½°ç°¬ Buildozer + Kivy 2.3.1
# éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²éˆºæ„¨æ™²

# éˆ¹í²€éˆ¹í²€ æ´æ—‚æ•¤é©çƒ˜æ¹°æ·‡â„ƒä¼… éˆ¹í²€éˆ¹í²€
title = é–°å¶‰ç…¶å®¸ãƒ¥å¿
package.name = dubbingtool
package.domain = com.tts.dubbing
source.dir = .
version = 1.0.0

# éˆ¹í²€éˆ¹í²€ éãƒ¥å½›é‚å›¦æ¬¢ éˆ¹í²€éˆ¹í²€
main.py = main.py

# éˆ¹í²€éˆ¹í²€ é–å‘­æƒˆé‚å›¦æ¬¢ç»«è¯²ç€· éˆ¹í²€éˆ¹í²€
source.include_exts = py,png,jpg,jpeg,kv,atlas,wav,mp3,ttf,otf

# éˆ¹í²€éˆ¹í²€ Python æ¸šæ¿Šç¦† (pip é–í²…) éˆ¹í²€éˆ¹í²€
requirements = python3,kivy==2.3.1,kivymd==1.2.0,edge-tts==7.2.8,python-docx==1.1.2,requests==2.32.0,Pillow==11.0.0,aiohttp==3.10.0

# éˆ¹í²€éˆ¹í²€ P4A é–°å¶†æŸŸ (Android ç¼‚æ ¬ç˜§æ¸šæ¿Šç¦†) éˆ¹í²€éˆ¹í²€
# android.recipe.blacklist = openssl,sqlite3

# éˆ¹í²€éˆ¹í²€ çå¿“ç®·é‚ç‘°æ‚œ éˆ¹í²€éˆ¹í²€
orientation = portrait
fullscreen = 0

# éˆ¹í²€éˆ¹í²€ Android é‰å†®æªº éˆ¹í²€éˆ¹í²€
android.permissions = INTERNET,ACCESS_NETWORK_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_AUDIO

# éˆ¹í²€éˆ¹í²€ Android é”ç†»å…˜å®¸èŒ¬æ•±é‰å†®æªºé‘·í²ªé”ã„¦å¸¹ç€µç¡·ç´éƒçŠ»æ¸¶æ£°æ¿†í²¤æ §ï¼é„í² éˆ¹í²€éˆ¹í²€

# éˆ¹í²€éˆ¹í²€ é‹å‹«ç¼“ç’å‰§ç–† éˆ¹í²€éˆ¹í²€
# Android API ç»¾ÑƒåŸ† (target=33, min=26 ç‘•å—™æ´Š 95% ç’æƒ§í²¤í²‡)
android.api = 33
android.minapi = 26

# NDK é—å Ÿæ¹°
android.ndk = 25b

# SDK é—å Ÿæ¹°
android.archs = arm64-v8a

# é‘·í²ªé”ã„¦å¸´é™í²— Android SDK ç’ç¨¿å½²ç’‡í²
android.accept_sdk_license = True

# éší²¯é¢í²¨ AndroidX
android.enable_androidx = true

# Java ç¼‚æ ¬ç˜§é–«å¤ã€
android.gradle_dependencies = androidx.core:core:1.9.0

# éˆ¹í²€éˆ¹í²€ ç»›æƒ§æ‚• éˆ¹í²€éˆ¹í²€
# é™æˆç«·éƒè·ºå½‡å¨‘å Ÿæ•é–²å©‚è‹Ÿæ¿‰í²«éãƒ¥ç˜‘é–½ãƒ¤ä¿Šé­í²¯
# android.release = 1
# android.keystore = release.keystore
# android.keyalias = dubbingtool
# android.keystore_password = your_password
# android.keyalias_password = your_password

# éˆ¹í²€éˆ¹í²€ é¥ç‚¬çˆ£æ¶“åº¡æƒé”ã„§æ•¾é—ˆí²¢ éˆ¹í²€éˆ¹í²€
# çí²† icon.png (512x512) é€æƒ§æ¹ªæ¤¤åœ­æ´°éåœ­æ´°è¤°í²•
# icon.filename = icon.png

# éší²¯é”ã„§æ•¾é—ˆí²¢
# presplash.filename = splash.png
# presplash.color = FAE5E5

# éˆ¹í²€éˆ¹í²€ éƒãƒ¥ç¹”æ©å›¨æŠ¤ éˆ¹í²€éˆ¹í²€
android.logcat_filters = *:S python:D

# éˆ¹í²€éˆ¹í²€ æ£°æ¿†í²¤æ ¨ç°®é®ä½ºæ´°è¤°í²• éˆ¹í²€éˆ¹í²€
android.add_src =

# éˆ¹í²€éˆ¹í²€ ç¼‚æ ¬ç˜§æµ¼æ¨ºå¯² éˆ¹í²€éˆ¹í²€
android.allow_backup = true

[buildozer]

# éˆ¹í²€éˆ¹í²€ é‹å‹«ç¼“å®¸ãƒ¥å¿ç’å‰§ç–† éˆ¹í²€éˆ¹í²€

# éƒãƒ¥ç¹”ç»¾ÑƒåŸ†: 0=é—ˆæ¬“ç²¯, 1=é©çƒ˜æ¹°æ·‡â„ƒä¼…, 2=ç’‡ï¸¾ç²
log_level = 2

# ç’€ï¹€æ†¡ root é¢ã„¦åŸ›
warn_on_root = 1

# ç“’å‘®æ¤‚ç’å‰§ç–† (ç»‰í²’)
build_timeout = 3600

# é‹å‹«ç¼“é©í²®è¤°í²•
build_dir = .buildozer
