import os
import shutil
import tempfile
from pydataui.cli.main import _load_app, create_project, build_app, show_version, check_app
from unittest.mock import MagicMock

def test_cli_create_all_templates():
    temp_dir = tempfile.mkdtemp()
    try:
        for t in ["basic", "dashboard", "crud", "ml-dashboard", "data-pipeline", "auth"]:
            p_dir = os.path.join(temp_dir, f"proj_{t}")
            args = MagicMock(project_name=p_dir, template=t)
            create_project(args)
            assert os.path.exists(os.path.join(p_dir, "app.py"))
            assert os.path.exists(os.path.join(p_dir, "requirements.txt"))
            
            # Check app loads
            app = _load_app(os.path.join(p_dir, "app.py"))
            assert app is not None
            assert len(app.routes) >= 1
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_cli_build_app():
    temp_dir = tempfile.mkdtemp()
    try:
        sample_app = os.path.join(temp_dir, "app.py")
        with open(sample_app, "w") as f:
            f.write("from pydataui import App\napp = App()\n@app.page('/')\ndef h(): return 'Hi'\n")
            
        out_dir = os.path.join(temp_dir, "dist")
        args = MagicMock(file=sample_app, output=out_dir)
        build_app(args)
        
        assert os.path.exists(os.path.join(out_dir, "app.py"))
        assert os.path.exists(os.path.join(out_dir, "Dockerfile"))
        assert os.path.exists(os.path.join(out_dir, "docker-compose.yml"))
        assert os.path.exists(os.path.join(out_dir, "static", "htmx.min.js"))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
