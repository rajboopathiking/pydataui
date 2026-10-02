import pytest
from pydataui import App
from pydataui.components import Text

def test_app_creation():
    app = App(title="Test App")
    assert app.title == "Test App"

def test_page_registration():
    app = App()
    
    @app.page("/about")
    def about():
        return Text("About Page")
        
    assert "/about" in app.routes
    assert app.routes["/about"]() == Text("About Page")

def test_api_registration():
    app = App()
    
    @app.api("/data", method="GET")
    def get_data():
        return {"status": "ok"}
        
    assert "/data" in app.api_routes
    assert app.api_routes["/data"]["handler"]() == {"status": "ok"}
