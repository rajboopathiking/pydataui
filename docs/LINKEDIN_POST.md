# PyDataUI Launch Announcement: LinkedIn Post

*Copy and paste the text below directly into your LinkedIn post.*

---

Stop rewriting your Python data prototypes in React just to make them fast enough for production. 🛑

For years, Python engineers have been caught between two extremes:
1. **Streamlit & Gradio**: Great for a 1-day proof-of-concept, but their "full-script rerun" architecture chokes on real datasets, causes memory leaks, and lacks commercial UI flexibility.
2. **React / Next.js + FastAPI**: Fast and scalable, but now your data team is forced to maintain dual repositories, deal with TypeScript build chains, npm dependencies, and state-sync boilerplate.

Today, we are changing that.

Introducing **PyDataUI** — a production-ready, full-stack Python framework engineered for Data & AI applications, powered by a **compiled Rust HTTP core**. 🦀🐍

---

### 💡 Why is PyDataUI different?

⚡ **Compiled Rust HTTP Engine (`PyRustAPI`)**:
Serves up to **112,000+ requests/sec** with sub-millisecond P99 latency. That is up to 60x faster than traditional Python UI rerun frameworks, with a base memory footprint under 30MB.

🎯 **Fine-Grained Reactive State**:
No full-page script re-executions. When your `@s.action` updates state, PyDataUI calculates the delta and updates *only* the affected DOM element via lightweight HTMX swaps.

🎨 **80+ Modern shadcn/ui Inspired Components**:
Enterprise-grade design tokens out of the box — KPI metric cards, data tables, Plotly charts, AI chatbots, sliders, dialogs, badges, and filters.

📊 **Universal Data Sniffing**:
Pass a **DuckDB** relation, **Polars** DataFrame, **PyArrow** Table, or **Pandas** DataFrame directly into `DataTable(s.data)`. No serialization or schema boilerplate required.

🖥️ **Dual Execution: Web Browser & Terminal UI (TUI)**:
The same Python code runs as a modern, responsive web application or as an interactive terminal dashboard over SSH jump boxes with zero code modifications (`pdu.run_tui(app)`).

🔒 **Enterprise Security Native**:
Built-in Role-Based Access Control (RBAC), JWT session management, PBKDF2 password hashing, and machine-to-machine API key management.

---

### 💻 A Full Reactive Dashboard in 20 Lines of Python:

```python
import pydataui as pdu

app = pdu.App(title="Cluster Telemetry", theme="slate")
s = pdu.state(active_nodes=12, latency_ms=8.4)

@s.action
def scale():
    s.active_nodes += 2
    s.latency_ms = round(s.latency_ms * 0.92, 2)

@app.page("/")
def home():
    return pdu.Container(
        pdu.Heading("Distributed Cluster Telemetry", level=1),
        pdu.Row(
            pdu.Card(pdu.Text("Active Nodes"), pdu.Heading(s.active_nodes, level=2)),
            pdu.Card(pdu.Text("Latency"), pdu.Heading(f"{s.latency_ms} ms", level=2)),
            pdu.Button("Scale Up", on_click=scale)
        )
    )

if __name__ == "__main__":
    app.run(port=8000)
```

No JavaScript. No Webpack. Just blazing-fast, reactive Python.

---

### 🔗 Try It Out Today:
We are 100% open-source under the MIT license:
⭐ **GitHub Repository**: https://github.com/rajboopathiking/pydataui
📖 **Full Documentation & Tutorials**: https://rajboopathiking.github.io/pydataui/
📦 **Get Started**: `pip install pydataui`

What are your biggest pain points when deploying Python data applications to production? Would love to hear your thoughts in the comments! 👇

---

#Python #DataScience #MachineLearning #WebDevelopment #RustLang #FastAPI #OpenSource #SoftwareEngineering #DataEngineering #AI #Streamlit #ReactJS
