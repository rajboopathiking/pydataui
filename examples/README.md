# 🚀 PyDataUI Examples Gallery

This directory contains standalone, runnable examples demonstrating PyDataUI across Web, Mobile, and Desktop.

---

## 📱 Mobile Examples (No Xcode / No Android Studio Required)

PyDataUI lets you develop, preview, and test mobile apps directly in your browser with hot-reload, test on real physical phones via QR code, and build standalone `.apk` packages without opening Xcode or Android Studio.

### 1. Mobile PWA Checklist & Field App (`mobile_pwa_app.py`)
A mobile-first inspection checklist application featuring:
- In-browser Mobile Device Simulator (iPhone 15 Pro, Pixel 8, iPad Mini) with live fast-reload
- Instant QR Code generator to test on real physical phones over Wi-Fi
- Standalone full-screen Progressive Web App (`pwa=True`)
- Mobile touch buttons, thumb-friendly cards, and responsive layout
- Zero build tools or compilation needed

**Run with In-Browser Mobile Simulator:**
```bash
pydataui mobile preview examples/mobile_pwa_app.py
```
Or with direct python:
```bash
python examples/mobile_pwa_app.py --preview
```
- Open `http://localhost:8000/_pdu/preview` to switch devices (iPhone 15 Pro, Pixel 8), rotate orientation, or fast reload.
- Click **Test on Real Phone** to display a QR code: scan with your phone's camera to run directly on your phone!
- On your phone, tap **Share** ➡️ **Add to Home Screen** to install as a standalone mobile app icon.

---

### 2. Standalone Mobile Build & Install (CLI Only - No IDEs)
When you are ready to compile an Android APK or prepare native release packages:

```bash
# 1. Initialize mobile project
pydataui mobile init --app-name "Field Inspector" --app-id "com.company.fieldinspector" --engine capacitor

# 2. Compile Android APK directly from terminal (No Android Studio GUI!)
pydataui mobile build --platform android

# 3. Direct install to connected Android phone via ADB / USB:
pydataui mobile install --platform android
```

---

## 🖥️ Desktop Examples

### 1. Standalone Desktop Operations Hub (`desktop_app.py`)
A widescreen desktop operations hub featuring:
- Standalone native OS desktop window mode without browser tabs or address bar
- Multi-column widescreen grid (`max_width="7xl"`)
- Live KPIs, microservice status controls (Start / Stop), and interactive alerts

**Run as standalone desktop window:**
```bash
python examples/desktop_app.py --desktop
```
or via the PyDataUI CLI:
```bash
pydataui run examples/desktop_app.py --desktop
```

---

### 2. Native Desktop Shell via Tauri 2.0
Compile into a native `.dmg` (macOS), `.msi` (Windows), or `.deb` (Linux):
```bash
# Initialize Tauri 2.0 shell
pydataui desktop init --app-name "Operations Hub"

# Run in development mode with hot reload
pydataui desktop dev

# Build standalone installer
pydataui desktop build
```

---

## 🌐 Classic Web Examples

| File | Description | Run Command |
| :--- | :--- | :--- |
| `hello_world.py` | Minimal 5-line PyDataUI application | `python examples/hello_world.py` |
| `counter_app.py` | Reactive counter demonstrating HTMX SSR | `python examples/counter_app.py` |
| `todo_app.py` | Full reactive Todo list with state mutation | `python examples/todo_app.py` |
| `crud_app.py` | Database CRUD operations and tables | `python examples/crud_app.py` |
| `dashboard.py` | Executive analytics dashboard | `python examples/dashboard.py` |
| `custom_ui_app.py` | Tailwind and shadcn/ui custom styling | `python examples/custom_ui_app.py` |
| `ml_portal_app.py` | Machine Learning model deployment portal | `python examples/ml_portal_app.py` |
| `data_team_samples.py` | Pre-built templates for data engineering | `python examples/data_team_samples.py` |
