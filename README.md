# To-Do List (Kivy + SQLite)

Run on desktop:   pip install kivy==2.3.0 && python main.py

## Build the APK (Ubuntu 22.04/24.04 or WSL2 - work inside ~/, NOT /mnt/c)
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip python3-venv autoconf libtool \
  pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev cmake libffi-dev libssl-dev build-essential
python3 -m venv ~/bvenv && source ~/bvenv/bin/activate
pip install --upgrade pip buildozer cython==0.29.36
cd ~/todo_app
buildozer -v android debug        # first build: 20-40 min (downloads SDK/NDK)

APK appears in ./bin/todolist-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
Install: copy to phone (USB / cloud / `adb install -r bin/*.apk`), tap it, allow
"Install unknown apps". Debug logs: `buildozer android logcat`.
