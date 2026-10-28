"""
Capacitor Mobile Integration for PyDataUI.
Provides scaffolding and runners for packaging PyDataUI web apps
into native iOS (Xcode) and Android (Android Studio / APK) mobile apps.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def get_cap_cmd() -> list[str]:
    """Return command to invoke Capacitor CLI."""
    if shutil.which("cap"):
        return ["cap"]
    return ["npx", "--yes", "@capacitor/cli@latest"]


def init_capacitor(
    project_dir: str = ".",
    app_name: str = "PyDataUI App",
    app_id: str = "com.pydataui.app",
    port: int = 8000,
    server_url: Optional[str] = None,
    overwrite: bool = False,
) -> str:
    """
    Scaffold a Capacitor mobile project inside the target directory.
    """
    root = Path(project_dir).resolve()
    cap_config = root / "capacitor.config.json"
    pkg_json = root / "package.json"
    dist_dir = root / "dist"

    dist_dir.mkdir(parents=True, exist_ok=True)

    # 1. Dist placeholder index.html if missing
    index_html = dist_dir / "index.html"
    if not index_html.exists():
        index_html.write_text(
            f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <title>{app_name}</title>
    <style>
        body {{
            margin: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #09090b;
            color: #f4f4f5;
        }}
    </style>
</head>
<body>
    <div style="text-align: center;">
        <h2>{app_name} Mobile</h2>
        <p style="color: #a1a1aa; font-size: 14px;">PyDataUI Mobile Application</p>
    </div>
</body>
</html>
""",
            encoding="utf-8",
        )

    # 2. package.json for Capacitor
    if not pkg_json.exists() or overwrite:
        pkg_data = {
            "name": app_name.lower().replace(" ", "-"),
            "version": "0.3.5",
            "private": True,
            "scripts": {
                "cap": "cap"
            },
            "devDependencies": {
                "@capacitor/cli": "^6.0.0",
                "@capacitor/core": "^6.0.0",
                "@capacitor/android": "^6.0.0",
                "@capacitor/ios": "^6.0.0"
            }
        }
        pkg_json.write_text(json.dumps(pkg_data, indent=2), encoding="utf-8")

    # 3. capacitor.config.json
    # Default to localhost/emulator host for live development
    url_target = server_url or f"http://10.0.2.2:{port}"
    config_data = {
        "appId": app_id,
        "appName": app_name,
        "webDir": "dist",
        "bundledWebRuntime": False,
        "server": {
            "url": url_target,
            "cleartext": True
        }
    }
    if not cap_config.exists() or overwrite:
        cap_config.write_text(json.dumps(config_data, indent=2), encoding="utf-8")

    return str(cap_config)


def add_platform(project_dir: str = ".", platform: str = "android") -> int:
    """Add a mobile platform (android or ios) to Capacitor."""
    root = Path(project_dir).resolve()
    cap_cmd = get_cap_cmd()
    print(f"📱 Adding Capacitor platform '{platform}'...")
    return subprocess.call(cap_cmd + ["add", platform], cwd=str(root))


def run_capacitor_dev(
    project_dir: str = ".",
    app_file: str = "app.py",
    platform: str = "android",
    host: str = "0.0.0.0",
    port: int = 8000,
) -> int:
    """
    Launch PyDataUI server and run Capacitor live-sync on connected device or emulator.
    """
    root = Path(project_dir).resolve()
    init_capacitor(str(root), port=port)

    platform_dir = root / platform
    if not platform_dir.exists():
        add_platform(str(root), platform=platform)

    print(f"\n🚀 [Capacitor] Starting PyDataUI backend on http://{host}:{port}...")
    server_env = dict(os.environ, PYDATAUI_HOST=host, PYDATAUI_PORT=str(port))
    cmd = [sys.executable, str(root / app_file)]
    server_proc = subprocess.Popen(cmd, cwd=str(root), env=server_env)

    try:
        cap_cmd = get_cap_cmd()
        print(f"🔄 Syncing mobile assets for {platform}...")
        subprocess.call(cap_cmd + ["sync", platform], cwd=str(root))
        print(f"📱 Launching Capacitor on {platform}...")
        return subprocess.call(cap_cmd + ["run", platform], cwd=str(root))
    finally:
        print("\n🛑 Shutting down PyDataUI backend server...")
        server_proc.terminate()
        try:
            server_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_proc.kill()


def find_java_home() -> Optional[str]:
    """
    Find a compatible Java Home (JDK 17 or 21) suitable for Gradle Android builds.
    Avoids Java 25+ which causes Gradle 8 'Unsupported class file major version 69'.
    """
    env_jh = os.environ.get("JAVA_HOME")
    if env_jh and os.path.isdir(env_jh):
        try:
            ver_proc = subprocess.run([os.path.join(env_jh, "bin", "java"), "-version"], capture_output=True, text=True)
            ver_str = ver_proc.stderr + ver_proc.stdout
            if "17." in ver_str or "21." in ver_str:
                return env_jh
        except Exception:
            pass

    if sys.platform == "darwin":
        for ver in ("17", "21"):
            try:
                res = subprocess.run(["/usr/libexec/java_home", "-v", ver], capture_output=True, text=True)
                if res.returncode == 0 and res.stdout.strip():
                    path = res.stdout.strip()
                    if os.path.isdir(path):
                        return path
            except Exception:
                pass

    standard_paths = [
        "/usr/lib/jvm/java-17-openjdk",
        "/usr/lib/jvm/java-17-openjdk-amd64",
        "/usr/lib/jvm/java-21-openjdk",
        "/usr/lib/jvm/java-21-openjdk-amd64",
        os.path.expanduser("~/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home"),
        os.path.expanduser("~/Library/Java/JavaVirtualMachines/temurin-21.jdk/Contents/Home"),
        "/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home",
        "/Library/Java/JavaVirtualMachines/temurin-21.jdk/Contents/Home",
    ]
    for p in standard_paths:
        if os.path.isdir(p):
            return p

    return env_jh if (env_jh and os.path.isdir(env_jh)) else None


def find_adb() -> Optional[str]:
    """Find installed ADB executable across PATH and Android SDK directory."""
    which_adb = shutil.which("adb")
    if which_adb:
        return which_adb
    sdk = find_android_sdk()
    if sdk:
        for sub in ("platform-tools", "cmdline-tools/bin", "tools/bin"):
            cand = Path(sdk) / sub / ("adb.exe" if sys.platform == "win32" else "adb")
            if cand.exists():
                return str(cand)
    return None


def find_android_sdk() -> Optional[str]:
    """Find installed Android SDK directory across standard system locations."""
    for var in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
        val = os.environ.get(var)
        if val and os.path.isdir(val):
            return val

    candidates = [
        os.path.expanduser("~/Library/Android/sdk"),
        "/usr/local/share/android-commandlinetools",
        "/usr/local/share/android-sdk",
        "/opt/homebrew/share/android-commandlinetools",
        "/opt/homebrew/share/android-sdk",
        os.path.join(os.path.expanduser("~"), "AppData", "Local", "Android", "Sdk"),
    ]
    for c in candidates:
        if c and os.path.isdir(c):
            return c
    return None


def build_mobile(
    project_dir: str = ".",
    platform: str = "android",
    mode: str = "debug",
) -> int:
    """
    Headless mobile build without opening Xcode or Android Studio GUI.
    Compiles an installable Android APK or prepares iOS distribution.
    """
    root = Path(project_dir).resolve()
    if not (root / "package.json").exists() or not (root / "capacitor.config.json").exists():
        init_capacitor(str(root))

    cap_cmd = get_cap_cmd()

    platform_dir = root / platform
    if not platform_dir.exists():
        add_platform(str(root), platform=platform)

    print(f"🔄 Syncing mobile platform assets for '{platform}'...")
    sync_code = subprocess.call(cap_cmd + ["sync", platform], cwd=str(root))
    if sync_code != 0:
        print("💡 Note: To link native modules locally, run 'npm install' in project directory.")

    if platform == "android":
        gradlew = root / "android" / "gradlew"
        if gradlew.exists():
            # Check if Java runtime is available
            java_ok = False
            try:
                check_res = subprocess.run(["java", "-version"], capture_output=True)
                java_ok = (check_res.returncode == 0)
            except Exception:
                java_ok = False

            if not java_ok:
                print("\n⚠️  Java Runtime is not installed on this machine.")
                print("   Android Gradle requires Java (JDK) to compile .apk binaries locally.\n")
                print("💡 You do NOT need to install heavy Java! You have 3 zero-Java alternatives:")
                print("   1. 📱 Instant PWA (Recommended): Open app on phone browser & tap 'Add to Home Screen'.")
                print("      Runs in full-screen standalone mode with native app icon, zero installation needed.")
                print("   2. ☁️ Cloud GitHub Actions: Push to GitHub and let cloud runners compile your APK for free.")
                print("   3. 📦 PWABuilder (by Microsoft): Drop your PWA URL at https://www.pwabuilder.com to get an APK.\n")
                return 0

            # Check / Configure Android SDK location
            local_props = root / "android" / "local.properties"
            sdk_path = find_android_sdk()
            if sdk_path and not local_props.exists():
                local_props.write_text(f"sdk.dir={sdk_path}\n", encoding="utf-8")
                print(f"🔧 Configured Android SDK location: {sdk_path}")

            if not sdk_path and not local_props.exists():
                print("\n⚠️  Android SDK not found on this machine.")
                print("   Gradle requires the Android SDK (API 34 + Build Tools) to compile .apk binaries locally.\n")
                print("🛠️  To build locally:")
                print("   1. Install Android Studio: https://developer.android.com/studio (installs SDK to ~/Library/Android/sdk)")
                print("   2. Or install command line tools: brew install --cask android-commandlinetools\n")
                print("☁️  Zero-Install Alternatives (Recommended):")
                print("   1. 📱 Instant PWA: Scan QR code at http://localhost:8000/_pdu/preview & tap 'Add to Home Screen'.")
                print("   2. ☁️ Cloud GitHub Actions: Push to GitHub - our .github/workflows/build-apk.yml builds the APK in the cloud!\n")
                return 0

            # Clean up any stale APK from previous builds
            apk_path = root / "android" / "app" / "build" / "outputs" / "apk" / mode / f"app-{mode}.apk"
            if apk_path.exists():
                try:
                    apk_path.unlink()
                except Exception:
                    pass

            target_task = "assembleDebug" if mode == "debug" else "assembleRelease"
            print(f"📦 Compiling Android APK via Gradle ({target_task})...")

            # Route to compatible Java 17/21 to avoid Class 69 error on newer default JREs
            gradle_env = dict(os.environ)
            target_jh = find_java_home()
            if target_jh:
                gradle_env["JAVA_HOME"] = target_jh
                gradle_env["PATH"] = f"{target_jh}/bin:" + gradle_env.get("PATH", "")

            # Patch Capacitor compatibility if compiling with Java 17
            for gfile in (root / "android").rglob("*.gradle"):
                if gfile.is_file():
                    try:
                        c_txt = gfile.read_text(encoding="utf-8")
                        if "VERSION_21" in c_txt:
                            gfile.write_text(c_txt.replace("VERSION_21", "VERSION_17"), encoding="utf-8")
                    except Exception:
                        pass

            # Make gradlew executable
            os.chmod(str(gradlew), 0o755)
            cmd = [str(gradlew)]
            if target_jh:
                cmd.append(f"-Dorg.gradle.java.home={target_jh}")
            cmd.append(target_task)

            res = subprocess.call(cmd, cwd=str(root / "android"), env=gradle_env)
            if res == 0 and apk_path.exists():
                print(f"\n🎉 Standalone APK built successfully: {apk_path}")
                return 0
            else:
                print(f"\n❌ Android APK compilation failed (Gradle exit code: {res}).")
                return res if res != 0 else 1
        else:
            print("💡 Capacitor Android assets synced. To compile APK manually: cd android && ./gradlew assembleDebug")
            return 0

    elif platform == "ios":
        if shutil.which("xcodebuild"):
            workspace = root / "ios" / "App" / "App.xcworkspace"
            if workspace.exists():
                print("📦 Compiling iOS package via headless xcodebuild...")
                cmd = [
                    "xcodebuild",
                    "-workspace", str(workspace),
                    "-scheme", "App",
                    "-configuration", "Debug",
                    "-destination", "generic/platform=iOS",
                    "build"
                ]
                return subprocess.call(cmd, cwd=str(root))
        print("💡 Capacitor iOS project prepared at 'ios/App/'. Open with Xcode or use PWA install.")
        return 0

    return 0


def install_mobile(
    project_dir: str = ".",
    platform: str = "android",
) -> int:
    """
    Directly install compiled app on a connected mobile device over USB/WiFi
    without opening Android Studio or Xcode.
    """
    root = Path(project_dir).resolve()
    if platform == "android":
        apk_path = root / "android" / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
        adb = find_adb()

        # Check for connected devices via ADB if ADB is available
        connected_devices = []
        if adb:
            try:
                res = subprocess.run([adb, "devices"], capture_output=True, text=True)
                lines = [line.strip() for line in res.stdout.strip().splitlines() if line.strip()]
                connected_devices = [l for l in lines[1:] if "\tdevice" in l]
            except Exception:
                pass

        if adb and not connected_devices:
            print("\n⚠️  No connected Android devices or emulators found.")
            print("💡 To install your app on a physical Android phone:")
            print("   1. Connect your phone via USB cable.")
            print("   2. Enable 'USB Debugging' in Settings -> Developer Options.")
            print("   3. Or scan the QR code from 'pydataui run --mobile-preview' to install instantly as a PWA!\n")
            return 0

        if not apk_path.exists():
            print("📦 No compiled APK found. Compiling first...")
            b_code = build_mobile(project_dir=project_dir, platform="android", mode="debug")
            if b_code != 0 or not apk_path.exists():
                print("❌ Failed to compile APK before install.")
                return 1

        if adb and connected_devices:
            print(f"📲 Installing {apk_path.name} to {len(connected_devices)} connected device(s)...")
            return subprocess.call([adb, "install", "-r", str(apk_path)])

        gradlew = root / "android" / "gradlew"
        if gradlew.exists():
            print("📲 Installing to connected Android device via Gradle installDebug...")
            os.chmod(str(gradlew), 0o755)
            cmd = [str(gradlew)]
            target_jh = find_java_home()
            if target_jh:
                cmd.append(f"-Dorg.gradle.java.home={target_jh}")
            cmd.append("installDebug")
            gradle_env = dict(os.environ)
            if target_jh:
                gradle_env["JAVA_HOME"] = target_jh
            return subprocess.call(cmd, cwd=str(root / "android"), env=gradle_env)

        print("💡 To install on Android: connect device via USB with USB Debugging enabled, or scan QR code to install PWA.")
        return 0
    else:
        print("💡 For iOS: scan QR code to install instantly as a PWA, or archive via Xcode for TestFlight.")
        return 0

