# PyDataUI

![PyPI - Version](https://img.shields.io/pypi/v/pydataui)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A production-grade full-stack Python framework powered by pyrustapi. Write pure Python, get reactive web apps with auto-generated REST APIs. No Javascript required.

## Key Features
- **Pure Python**: Write UI, logic, and state in Python. No JS, no HTML, no CSS (unless you want to).
- **Auto-generated REST APIs**: Your states and endpoints are automatically exposed as REST API routes.
- **Server-Side Rendered (SSR)**: Lightning fast initial loads powered by Rust (via `pyrustapi`).
- **Reactive via HTMX**: State changes trigger minimal DOM updates automatically using HTMX.
- **Type-safe**: Built with Pydantic and type annotations from the ground up.

## Quick Start

### Installation

```bash
pip install pydataui
```

### Minimal Example

```python
from pydataui import App
from pydataui.components import Container, Heading, Text

app = App(title='Hello World')

@app.page('/')
def home():
    return Container(
        Heading('Hello, World!', level=1),
        Text('Welcome to PyDataUI!'),
    )

if __name__ == '__main__':
    app.run()
```

Run your app:
```bash
pydataui run app.py
```

## Creating Projects
PyDataUI provides a CLI to bootstrap your projects:
```bash
pydataui init my_project --template basic
cd my_project
pydataui run
```

## Core Concepts

### Components
Build UIs using declarative, composable components.
```python
from pydataui.components import Card, Button, Flex
```

### State Management
Define globally accessible or session-scoped state with automatic API integration.
```python
from pydataui import State

class CounterState(State):
    count: int = 0
    
    def increment(self):
        self.count += 1
```

## Compared to Others
- **Gradio/Streamlit**: PyDataUI provides a true full-stack architecture. You can build multi-page apps, dashboards, and complex state flows securely and fast, rather than just ML demos.
- **Reflex**: PyDataUI leverages `pyrustapi` for backend serving which combines Rust's performance with Python's ease of use, avoiding heavy Node.js dependencies.

## Architecture
- **Backend**: Rust-powered ASGI/WSGI hybrid server via `pyrustapi` (Tokio/Hyper).
- **Frontend**: Server-rendered HTML enhanced with HTMX for seamless client-server reactivity.
- **State**: Pydantic-powered schemas.

## Configuration
Use `pydataui.toml` to configure app themes, routes, and plugins.

## Contributing
We welcome contributions! Please check `CONTRIBUTING.md` for guidelines.

## License
MIT License.
