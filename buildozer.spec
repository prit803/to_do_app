[app]
title = To-Do List
package.name = todolist
package.domain = org.todoapp
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_dirs = bin,.buildozer,venv,__pycache__
version = 1.0.0

# sqlite3 MUST be listed or the app crashes on Android
requirements = python3,kivy==2.3.0,sqlite3

orientation = portrait
fullscreen = 0

# No permissions needed: the app is fully offline
android.permissions =
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
