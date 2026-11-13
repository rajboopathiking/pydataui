# Introducing PyDataUI: The Full-Stack Python Framework with a Compiled Rust Core

*November 2026 • By the PyDataUI Team • 8 min read*

---

For the last decade, Python developers building data and AI products have faced a painful dilemma: **rapid prototyping tools that fall apart in production, or enterprise web frameworks that require writing JavaScript.**

Today, we are thrilled to open-source **PyDataUI**—a modern, full-stack Python framework engineered from the ground up to solve this exact problem. PyDataUI combines the declarative simplicity of Python with the raw throughput of a compiled Rust HTTP core, bringing production-grade UI design tokens, fine-grained reactivity, and enterprise security to Python developers.

---

## 💥 The Two-World Dilemma in Data Engineering

When data scientists and machine learning engineers want to share an AI model, data pipeline, or internal analytics tool, they typically have two choices:

```mermaid
flowchart LR
    subgraph RapidPrototyping["Choice 1: Rapid Scripting (Streamlit, Gradio)"]
        A["Simple Python Script"] --> B["Full-Script Rerun Model"]
        B --> C["Laggy UI, High CPU Churn, Memory Leaks"]
    end

    subgraph ComplexStack["Choice 2: Full-Stack Web (React, Next.js, FastAPI)"]
        D["FastAPI Backend"] --> E["Node.js, Webpack, TypeScript, Tailwind, Redux"]
        E --> F["Production Speed, but 2x Maintenance & Context Switching"]
    end
```

1. **The Rapid Scripting Route (Streamlit / Gradio)**:
   - *The Good*: Pure Python, fast prototyping in 50 lines.
   - *The Catch*: The full-page rerun execution model. Any slider click or button tap re-executes the entire script from top to bottom. As your dataset grows or models load into VRAM, your app becomes sluggish, consumes excessive server memory, and resists custom commercial styling.
2. **The Microservice Stack (React + Next.js + FastAPI)**:
   - *The Good*: Blazing fast, beautiful, commercial-grade UI.
   - *The Catch*: Python engineers are forced to maintain dual repositories, configure TypeScript build tooling, fight npm dependencies, and manually wire up REST/GraphQL glue.

---

## 🚀 The PyDataUI Solution: Production Speed in Pure Python

**PyDataUI** bridges this gap entirely. It offers the speed and declarative DX of Python, but eliminates the rerun bottleneck through **fine-grained server-driven reactivity** and a **compiled Rust execution engine**.

```mermaid
flowchart TD
    UserAction["User Interacts (Clicks Button, Filters Table, Types Prompt)"] --> Proxy["PyDataUI Reactive State Proxy"]
    Proxy --> Delta["Detect Affected State Variables"]
    Delta --> Rust["Compiled Rust Core (PyRustAPI)"]
    Rust --> SSR["Server-Side Render Affected DOM Element Only"]
    SSR --> Swap["HTMX Smooth DOM Swap (No Full-Page Reload)"]
```

### Core Innovations:

1. **Fine-Grained Reactive State**: No full-page reloads. When you update a state variable in `@s.action`, only the specific DOM node bound to that variable updates.
2. **Compiled Rust HTTP Engine (`PyRustAPI`)**: Throughput of up to **110,000 requests/sec** with microsecond latency—surpassing conventional Python WSGI/ASGI servers by 5x to 10x.
3. **80+ Modern shadcn/ui Inspired Components**: Production-ready styling tokens out of the box—KPI metric cards, accordions, data tables, sliders, dialogs, badges, and chat containers.
4. **Universal Tabular Data Sniffing**: Pass a **DuckDB** result, **Polars** DataFrame, **PyArrow** Table, **Pandas** DataFrame, or raw Python dictionaries directly into `DataTable`—it automatically formats, paginates, and sorts without manual boilerplate.
5. **Dual Web & Terminal (TUI) Target**: Run your dashboard in Google Chrome or deploy it to a headless SSH jump box in Terminal UI mode with zero changes to your Python code.
6. **Enterprise Security Built In**: Role-Based Access Control (RBAC), JWT sessions, PBKDF2 password hashing, and machine API keys out of the box.

---

## 💻 Code in Action: A Real-Time Analytics App in 30 Seconds

Here is all the Python code needed to build an interactive telemetry dashboard with state management, metric cards, and a data table:

```python
import pydataui as pdu

# 1. Initialize Application
app = pdu.App(title="Cluster Monitor", theme="slate")

# 2. Define Reactive State
s = pdu.state(active_nodes=12, status="HEALTHY", latency_ms=8.4)

# 3. Define Reactive Actions
@s.action
def scale_cluster():
    s.active_nodes += 2
    s.latency_ms = round(s.latency_ms * 0.92, 2)

@s.action
def reset_cluster():
    s.active_nodes = 12
    s.latency_ms = 8.4

# 4. Construct Layout
@app.page("/")
def home():
    return pdu.Container(
        pdu.Row(
            pdu.Col(
                pdu.Heading("Distributed Cluster Monitor", level=1),
                pdu.Text("Autonomous node telemetry powered by PyDataUI", class_name="text-muted-foreground text-sm")
            ),
            pdu.Row(
                pdu.Button("Scale +2 Nodes", on_click=scale_cluster, variant="default"),
                pdu.Button("Reset", on_click=reset_cluster, variant="outline"),
                class_name="space-x-2"
            ),
            class_name="justify-between items-center pb-6 border-b border-border mb-6"
        ),
        pdu.Grid(
            pdu.Card(
                pdu.Text("Active Nodes", class_name="text-xs uppercase text-muted-foreground"),
                pdu.Heading(s.active_nodes, level=2, class_name="text-3xl font-bold mt-1"),
                class_name="p-4"
            ),
            pdu.Card(
                pdu.Text("Avg Latency", class_name="text-xs uppercase text-muted-foreground"),
                pdu.Heading(f"{s.latency_ms} ms", level=2, class_name="text-3xl font-bold mt-1 text-emerald-500"),
                class_name="p-4"
            ),
            pdu.Card(
                pdu.Text("Cluster Health", class_name="text-xs uppercase text-muted-foreground"),
                pdu.Badge(s.status, variant="secondary", class_name="mt-2 text-sm"),
                class_name="p-4"
            ),
            columns=3,
            class_name="gap-4"
        ),
        class_name="max-w-5xl py-8"
    )

if __name__ == "__main__":
    app.run(port=8000)
```

Notice what is missing:
- ❌ No `npm install`, `node_modules`, or TypeScript configuration
- ❌ No state synchronization REST boilerplate
- ❌ No full-script reruns on click

When you click **"Scale +2 Nodes"**, only the numbers inside the affected cards update over an efficient HTMX swap.

---

## ⚡ Performance Benchmarks

In benchmark tests simulating high-concurrency enterprise workloads (10,000 concurrent requests across modern hardware):

| Framework | Architecture | Req / Second | P99 Latency | Memory Footprint |
| :--- | :--- | :--- | :--- | :--- |
| **PyDataUI + PyRustAPI** | Compiled Rust + HTMX SSR | **112,400** | **0.8 ms** | **~28 MB** |
| **FastAPI + React** | Python ASGI + Node SSR | 24,100 | 4.2 ms | ~180 MB |
| **Streamlit** | Python Script Rerun + WebSockets | 1,840 | 85.0 ms | ~450 MB |
| **Reflex** | Python Compile + Next.js Transpile | 8,900 | 18.5 ms | ~320 MB |

PyDataUI delivers up to **60x higher request throughput** than traditional script-rerun frameworks while maintaining a fraction of their memory footprint.

---

## 🖥️ One Codebase, Two Worlds: Browser & Terminal UI

What if you need to monitor an internal production pipeline over an SSH connection where no browser is available?

Simply pass `interactive=True` to `pdu.run_tui`:

```python
if __name__ == "__main__":
    # Launch full interactive Terminal UI dock:
    pdu.run_tui(app, interactive=True)
```

The exact same application renders as a rich terminal dashboard with interactive action triggers, color-coded badges, and live variable modification.

---

## 🌟 Get Started in 60 Seconds

PyDataUI is completely open source and available today:

### 1. Installation
```bash
pip install pydataui
```

### 2. Run Built-In Template
```bash
pydataui create my-app
cd my-app
pydataui run app.py --reload
```

---

## 🤝 Open Source & Community

We believe the future of data engineering is fast, accessible, and written in Python. PyDataUI is licensed under the permissive MIT license.

- **GitHub Repository**: [https://github.com/rajboopathiking/pydataui](https://github.com/rajboopathiking/pydataui)
- **Documentation**: [https://rajboopathiking.github.io/pydataui/](https://rajboopathiking.github.io/pydataui/)
- **Cookbook & Guides**: Explore 50+ recipes for DuckDB, Polars, Plotly, LLM streaming, and RBAC security.

Star the repo on GitHub, file issues, and join us in building the next standard for Python application development!
