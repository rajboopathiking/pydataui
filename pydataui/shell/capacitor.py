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
            "version": "0.3.3",
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

            target_task = "assembleDebug" if mode == "debug" else "assembleRelease"
            print(f"📦 Compiling Android APK via Gradle ({target_task})...")

            # Route to Java 17/21 if available on macOS to avoid Class 69 error
            gradle_env = dict(os.environ)
            if sys.platform == "darwin":
                for ver in ("17", "21"):
                    try:
                        jh_res = subprocess.run(["/usr/libexec/java_home", "-v", ver], capture_output=True, text=True)
                        if jh_res.returncode == 0 and jh_res.stdout.strip():
                            target_jh = jh_res.stdout.strip()
                            gradle_env["JAVA_HOME"] = target_jh
                            gradle_env["PATH"] = f"{target_jh}/bin:" + gradle_env.get("PATH", "")
                            break
                    except Exception:
                        pass

            # Patch Capacitor compatibility if compiling with Java 17
            cap_build_gradle = root / "android" / "app" / "capacitor.build.gradle"
            if cap_build_gradle.exists():
                c_txt = cap_build_gradle.read_text(encoding="utf-8")
                if "VERSION_21" in c_txt and "17" in gradle_env.get("JAVA_HOME", ""):
                    cap_build_gradle.write_text(c_txt.replace("VERSION_21", "VERSION_17"), encoding="utf-8")

            # Make gradlew executable
            os.chmod(str(gradlew), 0o755)
            cmd = [str(gradlew), target_task]
            res = subprocess.call(cmd, cwd=str(root / "android"), env=gradle_env)
            apk_path = root / "android" / "app" / "build" / "outputs" / "apk" / mode / f"app-{mode}.apk"
            if apk_path.exists():
                print(f"\n🎉 Standalone APK built successfully: {apk_path}")
            return res
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
        if shutil.which("adb") and apk_path.exists():
            print(f"📲 Installing {apk_path.name} to connected Android device via ADB...")
            return subprocess.call(["adb", "install", "-r", str(apk_path)])
        
        gradlew = root / "android" / "gradlew"
        if gradlew.exists():
            print("📲 Installing to connected Android device via Gradle installDebug...")
            os.chmod(str(gradlew), 0o755)
            return subprocess.call([str(gradlew), "installDebug"], cwd=str(root / "android"))

        print("💡 To install on Android: connect device via USB with USB Debugging enabled, or scan QR code to install PWA.")
        return 0
    else:
        print("💡 For iOS: scan QR code to install instantly as a PWA, or archive via Xcode for TestFlight.")
        return 0

