"""
Streamlit-Style Rapid Prototyping Example in PyDataUI.

Run with:
    python examples/streamlit_style_prototype.py
or:
    pdu run examples/streamlit_style_prototype.py

Highlights:
- Zero boilerplate (no App class, no component tree nesting, no decorators).
- Top-to-bottom procedural execution.
- 100% surgical HTMX DOM updates with ZERO full-script reruns!
- In-memory 0ms model & data access.
"""
import pydataui as pdu
import pandas as pd

# 1. Page Configuration & Theme
pdu.set_page_config(
    title="Executive AI Telemetry",
    layout="wide",
    theme="zinc",        # 20 built-in presets: zinc, slate, emerald, violet, amber...
    dark_mode=True
)

# 2. Modern Sidebar Controls
with pdu.sidebar():
    pdu.title("Cluster Controls")
    pdu.theme_toggle()
    
    env = pdu.selectbox("Active Environment", ["Production-US", "Staging-EU", "DR-Asia"])
    batch_size = pdu.slider("Inference Batch Size", min_value=1, max_value=64, value=16)
    enable_fp8 = pdu.checkbox("Enable FP8 Matrix Multiplication", value=True)
    dataset = pdu.file_uploader("Upload Evaluation Dataset", accept=[".jsonl", ".parquet"])

# 3. Main Dashboard Header & Status Banners
pdu.title("GPU Cluster Telemetry & Agent Dispatch")
pdu.success("All 16 H100 SXM5 nodes are operational. Zero packet loss detected.")

# 4. Multi-Column KPI Grid
col1, col2, col3 = pdu.columns([1, 1, 1])
with col1:
    pdu.metric("Active Sessions", "2,840", delta="+12.4%")
with col2:
    pdu.metric("P99 Inference Latency", "14.2ms", delta="-3.1ms")
with col3:
    pdu.metric("Token Throughput", "8.2k tokens/s", delta="+18.5%")

# 5. Interactive Multi-Tab Interface
tab_analytics, tab_copilot = pdu.tabs(["Analytics & Data", "Operations Copilot"])

with tab_analytics:
    # Polymorphic write: pass a DataFrame directly
    df = pd.DataFrame({
        "Worker Node": [f"node-{i:02d}" for i in range(1, 5)],
        "GPU Utilization": ["88%", "92%", "78%", "95%"],
        "VRAM Allocated": ["72 GB", "76 GB", "64 GB", "78 GB"],
        "Status": ["Healthy", "Healthy", "Idle", "Healthy"]
    })
    pdu.dataframe(df)

    pdu.subheader("24-Hour Utilization Trend")
    pdu.line_chart([65, 72, 80, 85, 92, 88, 84, 91, 95])

with tab_copilot:
    with pdu.chat_message("user"):
        pdu.write("Are there any memory anomalies on worker nodes?")
    with pdu.chat_message("assistant"):
        pdu.write("All nodes are operating within normal thermal and VRAM limits. Peak VRAM was 78 GB.")
    
    pdu.chat_input("Ask the operations assistant a question...")

if __name__ == "__main__":
    # Launch local server and optional zero-config public sharing tunnel
    pdu.run(port=8000, share=False)
