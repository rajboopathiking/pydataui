import argparse
import sys
import os
import importlib.util
from pathlib import Path

__version__ = "0.1.0"

def create_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def init_project(name: str, template: str):
    project_dir = Path(name)
    if project_dir.exists():
        print(f"Error: Directory '{name}' already exists.")
        sys.exit(1)
        
    project_dir.mkdir(parents=True)
    
    # Common directories
    (project_dir / "pages").mkdir()
    (project_dir / "components").mkdir()
    (project_dir / "static").mkdir()
    
    # Common files
    create_file(project_dir / "pages" / "__init__.py", "")
    create_file(project_dir / "components" / "__init__.py", "")
    create_file(project_dir / "pydataui.toml", '[app]\ntitle = "My PyDataUI App"\n')
    create_file(project_dir / "requirements.txt", "pydataui>=0.1.0\n")
    
    if template == 'basic':
        create_file(project_dir / "states.py", '''from pydataui import State

class CounterState(State):
    count: int = 0
    
    def increment(self):
        self.count += 1
''')
        create_file(project_dir / "pages" / "home.py", '''from pydataui.components import Container, Heading, Button, Flex
from states import CounterState

def render():
    return Container(
        Heading("Basic Counter", level=1),
        Flex(
            Button("-", on_click=CounterState.decrement, variant="danger"),
            Heading(CounterState.count, level=2),
            Button("+", on_click=CounterState.increment, variant="success"),
            align="center", gap="md"
        )
    )
''')
        create_file(project_dir / "app.py", '''from pydataui import App
from pages.home import render as render_home

app = App(title="Basic App")

@app.page("/")
def home():
    return render_home()

if __name__ == "__main__":
    app.run()
''')

    elif template == 'dashboard':
        create_file(project_dir / "states.py", '''from pydataui import State

class DashboardState(State):
    active_tab: str = "Overview"
''')
        create_file(project_dir / "app.py", '''from pydataui import App
from pydataui.components import Container, Heading, Text

app = App(title="Dashboard App")

@app.page("/")
def home():
    return Container(Heading("Dashboard", level=1), Text("Welcome to the dashboard."))

if __name__ == "__main__":
    app.run()
''')
    elif template == 'crud':
        create_file(project_dir / "states.py", '''from pydataui import State

class CrudState(State):
    items: list = []
''')
        create_file(project_dir / "app.py", '''from pydataui import App
from pydataui.components import Container, Heading, Text

app = App(title="CRUD App")

@app.page("/")
def home():
    return Container(Heading("CRUD Application", level=1), Text("Manage your data."))

if __name__ == "__main__":
    app.run()
''')
    print(f"Project '{name}' initialized successfully with template '{template}'.")
    print(f"Run `cd {name}` and `pydataui run` to start.")

def run_project(file: str, host: str, port: int, reload: bool, workers: int):
    file_path = Path(file)
    if not file_path.exists():
        print(f"Error: File '{file}' not found.")
        sys.exit(1)
        
    # Dynamically import the app file
    spec = importlib.util.spec_from_file_location("main_app", file_path)
    if spec is None or spec.loader is None:
        print(f"Error: Could not load module from {file}")
        sys.exit(1)
        
    module = importlib.util.module_from_spec(spec)
    sys.modules["main_app"] = module
    
    # Add current directory to python path for imports
    sys.path.insert(0, os.path.abspath(os.path.dirname(file_path)))
    
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        print(f"Error running application: {e}")
        sys.exit(1)
        
    # Find App instance
    app_instance = None
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        # Using a loose check to avoid circular imports during CLI loading
        if type(attr).__name__ == "App" and hasattr(attr, "run"):
            app_instance = attr
            break
            
    if app_instance is None:
        print("Error: Could not find an App instance in the file.")
        sys.exit(1)
        
    print(f"Starting PyDataUI app on {host}:{port}...")
    app_instance.run(host=host, port=port)

def cli():
    parser = argparse.ArgumentParser(prog='pydataui', description='PyDataUI - Full-Stack Python Framework')
    subparsers = parser.add_subparsers(dest='command')
    
    # pydataui init <project_name>
    init_parser = subparsers.add_parser('init', help='Create a new PyDataUI project')
    init_parser.add_argument('name', help='Project name')
    init_parser.add_argument('--template', choices=['basic', 'dashboard', 'crud'], default='basic', help='Template to use')
    
    # pydataui run [file]
    run_parser = subparsers.add_parser('run', help='Run a PyDataUI application')
    run_parser.add_argument('file', nargs='?', default='app.py', help='Entrypoint file')
    run_parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    run_parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    run_parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    run_parser.add_argument('--workers', type=int, default=1, help='Number of worker processes')
    
    # pydataui version
    subparsers.add_parser('version', help='Show version')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        init_project(args.name, args.template)
    elif args.command == 'run':
        run_project(args.file, args.host, args.port, args.reload, args.workers)
    elif args.command == 'version':
        print(f"PyDataUI version {__version__}")
    else:
        parser.print_help()

if __name__ == "__main__":
    cli()
