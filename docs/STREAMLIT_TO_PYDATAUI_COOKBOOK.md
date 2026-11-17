# The Complete Streamlit-to-PyDataUI Feature Cookbook

> **The Developer Experience of Streamlit + The Power of Production ASGI.**  
> This cookbook provides high-level code snippets and best practices for every procedural feature in PyDataUI.

---

## 1. Page Configuration & Theming

```python
import pydataui as pdu

# Configure global page properties
pdu.set_page_config(
    title="GPU Cluster Operations",
    layout="wide",          # "wide" (100% responsive fluid) or "centered" (max-w-6xl)
    theme="zinc",           # 20 built-in presets: zinc, slate, emerald, violet, etc.
    dark_mode=True          # True, False, or synced with system
)

# Render an interactive dark/light mode toggle anywhere in the app
pdu.theme_toggle()

# Multi-page navigation link (Streamlit-parity)
pdu.page_link("/copilot", label="AI Copilot", icon="💬")
pdu.page_link("/settings", label="Cluster Settings", icon="⚙️")
```

---

## 2. Layout & Containers

### Sticky Sidebar
```python
with pdu.sidebar():
    pdu.title("Controls")
    pdu.theme_toggle()
    pdu.selectbox("Select Model", ["Llama-3.3", "DeepSeek-R1", "GPT-4o"])
```

### Multi-Column Responsive Grid
```python
col1, col2, col3 = pdu.columns([1, 2, 1])
with col1:
    pdu.metric("Active Nodes", "16 / 16", delta="+2")
with col2:
    pdu.write("Center telemetry panel")
with col3:
    pdu.button("Drain Nodes")
```

### Collapsible Panel (`expander`)
```python
with pdu.expander("Advanced Hyperparameters", expanded=False):
    pdu.slider("Temperature", 0.0, 1.0, 0.7)
    pdu.slider("Top-P", 0.0, 1.0, 0.9)
    pdu.checkbox("Enable FP8 Quantization", value=True)
```

### Interactive In-Memory Tabs
```python
tab_data, tab_chat, tab_logs = pdu.tabs(["Data Explorer", "AI Copilot", "Logs"])
with tab_data:
    pdu.write("Data table view...")
with tab_chat:
    pdu.write("Chat history...")
with tab_logs:
    pdu.code("2026-11-18 01:00:00 [INFO] Cluster healthy")
```

### Card & Box Containers
```python
with pdu.card():
    pdu.subheader("Node 01 Status")
    pdu.text("Temperature: 42°C | Power: 340W")

pdu.divider()  # Sleek horizontal rule
```

---

## 3. Typography & Code

```python
pdu.title("H1 Top-Level Page Title")
pdu.header("H2 Section Header")
pdu.subheader("H3 Subsection Header")
pdu.caption("Small muted metadata text")
pdu.text("Plain body paragraph text")

# GitHub Flavored Markdown (Supports bold, italic, tables, lists, links)
pdu.markdown("""
### Cluster Status Summary
* **SXM5 Nodes**: 16 Online
* **Network**: 3.2 Tbps InfiniBand
Check docs at [Internal Portal](https://internal.company.io).
""")

# Syntax-highlighted code block
pdu.code("""
def calculate_loss(pred, target):
    return torch.nn.functional.cross_entropy(pred, target)
""", language="python")

# Interactive in-browser Monaco-grade code editor
pdu.code_editor(initial_value="SELECT * FROM gpu_telemetry LIMIT 100;", language="sql")
```

---

## 4. Polymorphic `pdu.write()`

`pdu.write()` automatically inspects the argument and selects the optimal visual component:

```python
pdu.write("# Markdown Header")                   # Markdown
pdu.write("Simple plain text")                    # Text
pdu.write(pandas_df)                              # Paginated interactive DataFrame table
pdu.write({"status": "active", "nodes": 16})      # Interactive collapsible JSON tree
pdu.write(["Node-1", "Node-2", "Node-3"])         # Formatted list
pdu.write(plotly_fig)                             # Interactive Plotly chart
pdu.write(matplotlib_fig)                         # High-res crisp PNG chart

# Reactive dynamic state provider (re-evaluates live on every HTMX interaction):
pdu.write(lambda: pdu.session_state.get("df", default_df))
```

---

## 5. Data Science & Telemetry Display

### Interactive DataFrames & Tables
```python
# Renders Pandas, Polars, DuckDB, or PyArrow tables with pagination & sorting
pdu.dataframe(df, max_rows=50)

# Pass structured records or dict lists
pdu.table([
    {"Node": "node-01", "Utilization": "88%", "Status": "Online"},
    {"Node": "node-02", "Utilization": "92%", "Status": "Online"},
])

# Read CSV convenience helper
df = pdu.read_csv(uploaded_file)
```

### Executive KPI Metric Cards
```python
pdu.metric("Throughput", "3,400 req/s", delta="+8.5%", delta_type="increase")
pdu.metric("P99 Latency", "12.4ms", delta="-2.1ms", delta_type="decrease")
pdu.metric("Error Rate", "0.01%", delta="0.00%", delta_type="neutral")
```

### JSON Tree Inspector
```python
pdu.json({"cluster": "us-east-1", "spec": {"h100_count": 64, "vram_total_gb": 5120}})
```

---

## 6. Built-In Interactive Charts

Zero external JS configuration required—pure 60fps hardware-accelerated rendering:

```python
# 1. Line Chart
pdu.line_chart([45, 52, 58, 65, 72, 80, 88], height="250px")

# 2. Bar Chart (Single or Multi-Series)
pdu.bar_chart({"A100": [10, 20, 30], "H100": [15, 35, 60]}, height="250px")

# 3. Area Chart
pdu.area_chart([100, 120, 140, 180, 210, 260], height="250px")

# 4. Scatter Chart
pdu.scatter_chart([1, 4, 9, 16, 25, 36, 49], height="250px")

# 5. Plotly & Matplotlib Integration
pdu.plotly_chart(plotly_fig, use_container_width=True)
pdu.pyplot(matplotlib_fig)
```

---

## 7. Interactive Form & Input Widgets

All widgets support `on_change`, `key` (auto-sync to `pdu.session_state`), and auto-inferred parameters:

```python
# Button
pdu.button("Run Evaluation", on_click=trigger_eval)

# Text Inputs
name = pdu.text_input("Username", placeholder="e.g. jdoe", key="username")
query = pdu.text_area("SQL Query", rows=4, placeholder="SELECT ...")

# Number Input
batch_size = pdu.number_input("Batch Size", min_value=1, max_value=128, value=32, step=8)

# Slider (Auto-infers 0.01 step for floats [0.0, 1.0] and 1 for ints [0, 100])
temp = pdu.slider("Temperature", 0.0, 1.0, 0.7)

# Dropdown & Multiselect
model = pdu.selectbox("Model", ["Llama-3.3", "DeepSeek-R1", "GPT-4o"], index=1)
tags = pdu.multiselect("Tags", ["Production", "Evaluation", "Benchmarked"])

# Checkbox & Toggle Switches
use_fp8 = pdu.checkbox("Enable FP8 Acceleration", value=True)
logging_enabled = pdu.toggle("Verbose Logging", value=False)
choice = pdu.radio("Precision", ["BF16", "FP16", "FP8"])

# Drag-and-drop File Uploader (Auto-syncs to session_state & supports pd.read_csv)
dataset = pdu.file_uploader(
    "Upload Evaluation CSV",
    accept=[".csv", ".parquet"],
    key="eval_file",
    on_change=handle_csv_upload
)
```

---

## 8. AI & Chat Operations

Native primitives for building conversational agents, LLM copilots, and multi-turn workflows:

```python
# User & Assistant Chat Bubbles
with pdu.chat_message("user"):
    pdu.write("Summarize cluster utilization for today.")

with pdu.chat_message("assistant", avatar="🤖"):
    pdu.write("Average GPU utilization was 84%. Node-04 peaked at 95% during batch inference.")

# Chat Input Field
# - Wraps in an auto-reset form via HTMX (prompt clears on Enter/Submit)
# - Mirrors input to pdu.session_state["user_prompt"]
# - Passes query directly to on_submit(query)
pdu.chat_input(
    "Ask the copilot a question...",
    key="user_prompt",
    on_submit=handle_agent_dispatch
)
```

---

## 9. Feedback & Status Notifications

```python
pdu.success("All 16 H100 SXM5 nodes online.")
pdu.info("Scheduled batch maintenance at 02:00 UTC.")
pdu.warning("High VRAM allocation on Worker-04 (88%).")
pdu.error("Node 07 reported transient PCIe bus error.")

# Floating transient toast notification (auto-dismissing)
pdu.toast("Agent dispatch complete!", icon="🚀")

# Progress bar
pdu.progress(85)  # 85% filled
```

---

## 10. Session State & Reactive Binding

```python
# Store and retrieve session state across requests:
pdu.session_state["model_name"] = "DeepSeek-R1"
pdu.session_state.run_id = "run-9842"

# Safe retrieval with fallback:
active_df = pdu.session_state.get("df", default_df)

# Reactive dynamic binding to UI:
# The table updates automatically whenever pdu.session_state["df"] changes:
pdu.write(lambda: pdu.session_state.get("df", default_df))
```

---

## 11. Production Deployment & FastAPI Mounting

### 1-Line Native FastAPI Mounting (Zero Reverse Proxy Needed)
```python
from fastapi import FastAPI
import pydataui as pdu

api = FastAPI(title="Core AI Microservice")

@api.get("/api/health")
def health():
    return {"status": "healthy"}

# Build your Streamlit-style UI
pdu.set_page_config(title="Dashboard", layout="wide")
pdu.title("Cluster Operations")
pdu.write("Live telemetry...")

# Mount inside FastAPI — 1 process, 1 port, 0ms shared in-memory access!
api.mount("/dashboard", pdu.get_app()._engine.app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host="127.0.0.1", port=8002)
```

### Instant 3.5s Zero-Config Public HTTPS Link
```python
if __name__ == "__main__":
    pdu.run(port=8000, share=True)  # Gives instant public HTTPS tunnel for stakeholders
```
