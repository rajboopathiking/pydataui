import argparse
import os
import shutil
import sys
import secrets
import importlib.util
from pathlib import Path
from pydataui.cli.templates import TEMPLATES

__version__ = "0.3.5"

def _load_app(file_path_str: str):
    """Dynamically load and locate the PyDataUI App instance in a given file."""
    file_path = Path(file_path_str).resolve()
    if not file_path.exists():
        print(f"Error: File '{file_path_str}' not found.")
        sys.exit(1)
        
    sys.path.insert(0, str(file_path.parent))
    spec = importlib.util.spec_from_file_location("main_app", str(file_path))
    if spec is None or spec.loader is None:
        print(f"Error: Could not load module from {file_path_str}")
        sys.exit(1)
        
    module = importlib.util.module_from_spec(spec)
    sys.modules["main_app"] = module
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error running application '{file_path_str}': {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    app_instance = None
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if type(attr).__name__ == "App" and hasattr(attr, "run"):
            app_instance = attr
            break
            
    if app_instance is None:
        from pydataui.dx import _default_app
        if _default_app is not None:
            app_instance = _default_app

    if app_instance is None:
        print(f"Error: Could not find an App instance in '{file_path_str}'. Define `app = App(...)` or use simplified `ui.*`.")
        sys.exit(1)
        
    return app_instance

def _app_factory():
    """ASGI Application Factory for Uvicorn auto-reload and multi-worker execution."""
    app_file = os.environ.get("PYDATAUI_APP_FILE")
    if not app_file:
        raise RuntimeError("PYDATAUI_APP_FILE environment variable is required for Uvicorn factory.")
    
    app_path = Path(app_file).resolve()
    if not app_path.exists():
        raise RuntimeError(f"PyDataUI application file '{app_file}' not found.")
        
    mobile_preview = os.environ.get("PYDATAUI_MOBILE_PREVIEW") == "1"
    reload_flag = os.environ.get("PYDATAUI_RELOAD") == "1"
    
    app = _load_app(str(app_path))
    if mobile_preview:
        app.config.mobile_preview = True
    if reload_flag:
        app.config.reload = True
    app._register_api_endpoints()
    return app.asgi_app

def create_project(args):
    project_name = args.project_name
    template = args.template
    
    if os.path.exists(project_name):
        print(f"Error: Directory '{project_name}' already exists.")
        sys.exit(1)
        
    os.makedirs(project_name)
    app_file = os.path.join(project_name, "app.py")
    
    with open(app_file, "w", encoding="utf-8") as f:
        f.write(TEMPLATES.get(template, TEMPLATES["basic"]))
        
    with open(os.path.join(project_name, "requirements.txt"), "w", encoding="utf-8") as f:
        f.write("pydataui>=0.2.1\n")
        
    print(f"\n✨ Created PyDataUI project '{project_name}' with template '{template}'!")
    print(f"   cd {project_name}")
    print(f"   pydataui dev app.py\n")

def dev_server(args):
    file_path = Path(args.file).resolve()
    os.environ["PYDATAUI_APP_FILE"] = str(file_path)
    mobile_preview = getattr(args, "mobile_preview", False)
    if mobile_preview:
        os.environ["PYDATAUI_MOBILE_PREVIEW"] = "1"
    if getattr(args, "reload", False):
        os.environ["PYDATAUI_RELOAD"] = "1"
    app = _load_app(str(file_path))
    print(f"\n🚀 Starting PyDataUI development server for '{args.file}' on {args.host}:{args.port} (reload={args.reload})...")
    app.run(host=args.host, port=args.port, reload=args.reload, workers=1, mobile_preview=mobile_preview)

def run_server(args):
    file_path = Path(args.file).resolve()
    os.environ["PYDATAUI_APP_FILE"] = str(file_path)
    desktop = getattr(args, "desktop", False)
    mobile_preview = getattr(args, "mobile_preview", False)
    if mobile_preview:
        os.environ["PYDATAUI_MOBILE_PREVIEW"] = "1"
    app = _load_app(str(file_path))
    if desktop:
        print(f"\n🖥️  Starting PyDataUI desktop application for '{args.file}' on {args.host}:{args.port}...")
    elif mobile_preview:
        print(f"\n📱 Starting PyDataUI with mobile preview for '{args.file}' on {args.host}:{args.port}...")
    else:
        print(f"\n⚡ Starting PyDataUI production server for '{args.file}' on {args.host}:{args.port} (workers={args.workers})...")
    app.run(host=args.host, port=args.port, reload=False, workers=args.workers, share=args.share, desktop=desktop, mobile_preview=mobile_preview)

def desktop_cmd(args):
    from pydataui.shell.tauri import init_tauri, run_tauri_dev, build_tauri
    if args.action == "init":
        p = init_tauri(app_name=args.name, identifier=args.id, overwrite=args.force)
        print(f"\n✨ Initialized Tauri 2.0 Desktop & Mobile shell in '{p}'!")
        print("   To start desktop development:")
        print("   pydataui desktop dev app.py\n")
    elif args.action == "dev":
        run_tauri_dev(app_file=args.file, port=args.port)
    elif args.action == "build":
        build_tauri(target=args.target)

def mobile_cmd(args):
    engine = getattr(args, "engine", "tauri")
    if args.action == "init":
        if engine == "capacitor":
            from pydataui.shell.capacitor import init_capacitor
            c = init_capacitor(app_name=args.name, app_id=args.id, overwrite=args.force)
            print(f"\n✨ Initialized Capacitor mobile configuration in '{c}'!")
            print("   To add platforms: npx cap add android / npx cap add ios\n")
        else:
            from pydataui.shell.tauri import init_tauri
            p = init_tauri(app_name=args.name, identifier=args.id, overwrite=args.force)
            print(f"\n✨ Initialized Tauri 2.0 Mobile shell in '{p}'!")
            print("   To initialize mobile targets:")
            print("   npx @tauri-apps/cli android init")
            print("   npx @tauri-apps/cli ios init\n")
    elif args.action == "dev":
        if engine == "capacitor":
            from pydataui.shell.capacitor import run_capacitor_dev
            run_capacitor_dev(app_file=args.file, platform=args.platform, port=args.port)
        else:
            from pydataui.shell.tauri import run_tauri_dev
            run_tauri_dev(app_file=args.file, port=args.port, target=args.platform)
    elif args.action == "preview":
        file_path = Path(args.file).resolve()
        os.environ["PYDATAUI_APP_FILE"] = str(file_path)
        os.environ["PYDATAUI_MOBILE_PREVIEW"] = "1"
        reload_enabled = getattr(args, "reload", True)
        if reload_enabled:
            os.environ["PYDATAUI_RELOAD"] = "1"
        app = _load_app(str(file_path))
        print(f"\n📱 Starting PyDataUI Mobile Simulator for '{args.file}' on {args.host}:{args.port} (reload={reload_enabled})...")
        app.run(host=args.host, port=args.port, reload=reload_enabled, mobile_preview=True)
    elif args.action == "build":
        if engine == "capacitor":
            from pydataui.shell.capacitor import build_mobile
            server_url = getattr(args, "server_url", None)
            port = getattr(args, "port", 8000)
            app_file = getattr(args, "file", None)
            build_mobile(platform=args.platform, server_url=server_url, port=port, app_file=app_file)
        else:
            from pydataui.shell.tauri import build_tauri
            build_tauri(target=args.platform)
    elif args.action == "install":
        from pydataui.shell.capacitor import install_mobile
        install_mobile(platform=args.platform)

def build_app(args):
    build_dir = args.output or "__pydataui_build__"
    if os.path.exists(build_dir) and os.listdir(build_dir):
        raise ValueError("Build output directory is not empty; choose a new output directory")
    os.makedirs(build_dir, exist_ok=True)
    
    file_path = Path(args.file).resolve()
    if not file_path.exists():
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)
        
    shutil.copy(str(file_path), os.path.join(build_dir, "app.py"))
    
    # Copy real static assets from the installed package
    static_dest = os.path.join(build_dir, "static")
    os.makedirs(static_dest, exist_ok=True)
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    js_src = os.path.join(pkg_dir, "styling", "js", "htmx.min.js")
    css_src = os.path.join(pkg_dir, "styling", "css", "pydataui.css")
    if os.path.exists(js_src):
        shutil.copy(js_src, os.path.join(static_dest, "htmx.min.js"))
    if os.path.exists(css_src):
        shutil.copy(css_src, os.path.join(static_dest, "pydataui.css"))
        
    dockerfile_content = '''FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["pydataui", "run", "app.py", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
'''
    with open(os.path.join(build_dir, "Dockerfile"), "w", encoding="utf-8") as f:
        f.write(dockerfile_content)
        
    compose_content = '''version: '3.8'
services:
  pydataui-app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYDATAUI_HOST=0.0.0.0
      - PYDATAUI_PORT=8000
    restart: unless-stopped
'''
    with open(os.path.join(build_dir, "docker-compose.yml"), "w", encoding="utf-8") as f:
        f.write(compose_content)
        
    with open(os.path.join(build_dir, "requirements.txt"), "w", encoding="utf-8") as f:
        f.write("pydataui>=0.2.1\n")
        
    print(f"\n📦 Production Build Summary:")
    print(f"  - App entrypoint:   {build_dir}/app.py")
    print(f"  - Bundled assets:   {static_dest}/ (htmx.min.js, pydataui.css)")
    print(f"  - Dockerfile:       {build_dir}/Dockerfile")
    print(f"  - Docker Compose:   {build_dir}/docker-compose.yml")
    print(f"  - Requirements:     {build_dir}/requirements.txt")
    print(f"\nReady for containerization! Run: cd {build_dir} && docker compose up --build\n")

def show_version(args):
    print(f"PyDataUI version {__version__} (FastAPI default core)")

def open_docs(args):
    import webbrowser
    print("Opening PyDataUI documentation in your browser...")
    webbrowser.open("https://github.com/rajboopathiking/pydataui#readme")

def check_app(args):
    print(f"Validating '{args.file}' syntax and App definitions...")
    try:
        app = _load_app(args.file)
        routes_count = len(app.routes)
        print(f"✅ Success: '{args.file}' is valid.")
        print(f"   Found App instance with {routes_count} registered page route(s).")
    except Exception as e:
        print(f"❌ Error: Validation failed. {e}")
        sys.exit(1)

def generate_key(args):
    raw_key = "pdu_live_" + secrets.token_hex(16)
    print(f"\n🔑 Generated PyDataUI API Key:")
    print(f"   Name:   {args.name}")
    print(f"   Token:  {raw_key}")
    print(f"   Header: Authorization: Bearer {raw_key}\n")

def main():
    parser = argparse.ArgumentParser(prog="pydataui", description="PyDataUI — Production Full-Stack Python Framework for Data Roles")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # new
    parser_new = subparsers.add_parser("new", help="Create a new PyDataUI project")
    parser_new.add_argument("project_name", help="Name of the project directory")
    parser_new.add_argument("--template", choices=["basic", "dashboard", "crud", "ml-dashboard", "data-pipeline", "auth"], default="basic", help="Project template")

    # dev
    parser_dev = subparsers.add_parser("dev", help="Start development server with auto-reload")
    parser_dev.add_argument("file", nargs="?", default="app.py", help="App entrypoint file (default: app.py)")
    parser_dev.add_argument("--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)")
    parser_dev.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    parser_dev.add_argument("--reload", action="store_true", help="Enable auto-reload on code change")
    parser_dev.add_argument("--mobile-preview", action="store_true", help="Launch in-browser mobile device simulator with live reload & QR code")

    # run
    parser_run = subparsers.add_parser("run", help="Start production server")
    parser_run.add_argument("file", nargs="?", default="app.py", help="App entrypoint file (default: app.py)")
    parser_run.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser_run.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    parser_run.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    parser_run.add_argument("--share", action="store_true", help="Create public port forwarding tunnel (like Gradio)")
    parser_run.add_argument("--desktop", action="store_true", help="Launch in native desktop window")
    parser_run.add_argument("--mobile-preview", action="store_true", help="Launch in-browser mobile device simulator with live reload & QR code")

    # desktop
    parser_desktop = subparsers.add_parser("desktop", help="Manage Tauri 2.0 cross-platform desktop application")
    desktop_subs = parser_desktop.add_subparsers(dest="action", required=True)
    
    d_init = desktop_subs.add_parser("init", help="Scaffold Tauri 2.0 desktop & mobile shell")
    d_init.add_argument("--name", default="PyDataUI App", help="Application display name")
    d_init.add_argument("--id", default="com.pydataui.app", help="Application bundle identifier")
    d_init.add_argument("--force", action="store_true", help="Overwrite existing configuration")
    
    d_dev = desktop_subs.add_parser("dev", help="Run desktop development window with live backend")
    d_dev.add_argument("file", nargs="?", default="app.py", help="App entrypoint file")
    d_dev.add_argument("--port", type=int, default=8000, help="Backend port")
    
    d_build = desktop_subs.add_parser("build", help="Build production native desktop installers")
    d_build.add_argument("--target", default=None, help="Build target")

    # mobile
    parser_mobile = subparsers.add_parser("mobile", help="Manage Tauri 2.0 / Capacitor mobile application (iOS & Android)")
    mobile_subs = parser_mobile.add_subparsers(dest="action", required=True)

    m_preview = mobile_subs.add_parser("preview", help="Run mobile device simulator in the browser with live reload & QR code")
    m_preview.add_argument("file", nargs="?", default="app.py", help="App entrypoint file")
    m_preview.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    m_preview.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    m_preview.add_argument("--reload", action="store_true", default=True, help="Enable auto-reload on code change")

    m_init = mobile_subs.add_parser("init", help="Scaffold mobile application shell")
    m_init.add_argument("--name", default="PyDataUI App", help="Application display name")
    m_init.add_argument("--id", default="com.pydataui.app", help="Application bundle identifier")
    m_init.add_argument("--engine", choices=["tauri", "capacitor"], default="tauri", help="Mobile shell engine (default: tauri)")
    m_init.add_argument("--force", action="store_true", help="Overwrite existing configuration")
    
    m_dev = mobile_subs.add_parser("dev", help="Run mobile app in simulator or device")
    m_dev.add_argument("file", nargs="?", default="app.py", help="App entrypoint file")
    m_dev.add_argument("--platform", choices=["android", "ios"], default="android", help="Target platform (android or ios)")
    m_dev.add_argument("--engine", choices=["tauri", "capacitor"], default="tauri", help="Mobile shell engine")
    m_dev.add_argument("--port", type=int, default=8000, help="Backend port")
    
    m_build = mobile_subs.add_parser("build", help="Build release APK or mobile packages without opening Android Studio/Xcode")
    m_build.add_argument("--platform", choices=["android", "ios"], default="android", help="Target platform")
    m_build.add_argument("--engine", choices=["tauri", "capacitor"], default="capacitor", help="Mobile shell engine")
    m_build.add_argument("--server-url", default=None, help="Backend server URL (defaults to auto-detected local Wi-Fi IP)")
    m_build.add_argument("--port", type=int, default=8000, help="Backend server port (default: 8000)")
    m_build.add_argument("--file", default=None, help="App file (e.g. app.py)")

    m_install = mobile_subs.add_parser("install", help="Directly install compiled app on mobile device without IDE")
    m_install.add_argument("--platform", choices=["android", "ios"], default="android", help="Target platform")

    # build
    parser_build = subparsers.add_parser("build", help="Build static assets and Docker configuration")
    parser_build.add_argument("file", nargs="?", default="app.py", help="App entrypoint file (default: app.py)")
    parser_build.add_argument("--output", default="dist", help="Output directory (default: dist)")

    # version
    parser_version = subparsers.add_parser("version", help="Show PyDataUI version")

    # docs
    parser_docs = subparsers.add_parser("docs", help="Open documentation in browser")

    # check
    parser_check = subparsers.add_parser("check", help="Validate app syntax and routes")
    parser_check.add_argument("file", nargs="?", default="app.py", help="App file to check")

    # generate key
    parser_gen = subparsers.add_parser("generate", help="Generate assets (e.g. API keys)")
    parser_gen_sub = parser_gen.add_subparsers(dest="gen_type", required=True)
    parser_key = parser_gen_sub.add_parser("key", help="Generate a production API key")
    parser_key.add_argument("--name", required=True, help="Name or label for the key")

    args = parser.parse_args()

    if args.command == "new":
        create_project(args)
    elif args.command == "dev":
        dev_server(args)
    elif args.command == "run":
        run_server(args)
    elif args.command == "desktop":
        desktop_cmd(args)
    elif args.command == "mobile":
        mobile_cmd(args)
    elif args.command == "build":
        build_app(args)
    elif args.command == "version":
        show_version(args)
    elif args.command == "docs":
        open_docs(args)
    elif args.command == "check":
        check_app(args)
    elif args.command == "generate":
        if args.gen_type == "key":
            generate_key(args)

cli = main

if __name__ == "__main__":
    main()
