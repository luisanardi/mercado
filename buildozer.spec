[app]

# (str) Title of your application
title = ITALO SUPERMERCADO - Validade

# (str) Package name
package.name = italovalidade

# (str) Package domain (needed for android/ios packaging)
package.domain = com.italo.validade

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,db

# (str) Application versioning
version = 0.1

# (list) Application requirements
requirements = python3,kivy,sqlite3

# (list) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (bool) Accept SDK license (Essencial para não dar erro)
android.accept_sdk_license = True

# (bool) Private storage
android.private_storage = True

# (list) Architectures to build
android.archs = arm64-v8a, armeabi-v7a

# (bool) Backup feature
android.allow_backup = True

[buildozer]

# (int) Log level
log_level = 2

# (int) Display warning if run as root
warn_on_root = 1
