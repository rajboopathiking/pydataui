"""
Flagship AI Model Registry & Ops Dashboard.
Demonstrates PyDataUI's pure-Python modern shadcn/ui architecture:
- Responsive DashboardLayout with Collapsible Sidebar (icon / offcanvas)
- Interactive Breadcrumbs, Header, Theme Toggle, and Cmd+K Command Palette
- Machine Learning Precision Controls: ShadSlider, ShadRadioGroup, ShadDatePicker
- Overlays: ShadDropdownMenu, ShadPopover, ShadTooltip, ShadAlertDialog
- Universal Extensibility Engine: Direct copy-paste of upcoming components via from_jsx
"""
from pydataui import App, State
from pydataui.shadcn import (
    DashboardLayout, Sidebar, NavGroup, NavItem, Header,
    ShadButton, ShadCard, ShadCardHeader, ShadCardTitle, ShadCardDescription,
    ShadCardContent, ShadCardFooter, ShadBadge, ShadSlider, ShadRadioGroup,
    ShadDatePicker, ShadDropdownMenu, ShadDropdownItem, ShadDropdownSeparator,
    ShadPopover, ShadTooltip, ShadPagination, from_jsx
)
from pydataui.components.data_science import (
    MetricCard, ConfusionMatrix, FeatureImportance, PipelineStatus
)


class ModelState(State):
    temperature: float = 0.7
    top_p: float = 0.95
    selected_model: str = "mistral-7b"
    eval_date: str = "2026-11-11"


app = App(title="NeuroNest AI Model Registry", theme="dark", palette="zinc")


# Example of consuming an upcoming community component directly in pure Python:
BentoFeatureCard = from_jsx("""
<div className="rounded-xl border border-border bg-card text-card-foreground p-5 shadow-sm hover:shadow-md transition-shadow">
  <div className="flex items-center justify-between pb-2">
    <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{category}</span>
    <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20">{badge}</span>
  </div>
  <h4 className="text-lg font-bold tracking-tight">{title}</h4>
  <p className="text-xs text-muted-foreground mt-1">{description}</p>
  <div className="mt-4 pt-3 border-t border-border flex items-center justify-between">
    <span className="font-mono text-xs text-muted-foreground">{latency}</span>
    {action}
  </div>
</div>
""")


@app.page("/")
def home():
    # 1. Modern Collapsible Sidebar
    sidebar = Sidebar(
        brand={"name": "NeuroNest AI", "logo": "cpu", "plan": "Enterprise"},
        groups=[
            NavGroup("Platform", [
                NavItem("Model Registry", icon="box", href="/", active=True, badge="14"),
                NavItem("Prompt Studio", icon="sparkles", href="/prompts"),
                NavItem("Evaluation Benchmarks", icon="activity", href="/benchmarks"),
            ]),
            NavGroup("Operations", [
                NavItem("Drift & Telemetry", icon="activity", href="/telemetry"),
                NavItem("Vector Store Indexes", icon="database", href="/vectors"),
                NavItem("Audit & Compliance", icon="shield-check", href="/audit"),
                NavItem("Cluster Settings", icon="settings", href="/settings"),
            ]),
        ],
        footer={"name": "Boopathi Raj", "email": "boopathi@neuronest.ai", "avatar": "BR"},
        collapsible="icon"
    )

    # 2. Header with Breadcrumbs, Search, Theme Toggle, Actions
    header = Header(
        breadcrumbs=[("Home", "/"), ("Models", "/"), "Mistral-7B-Instruct-v0.3"],
        search=True,
        actions=[
            ShadTooltip("Download Model Weights", ShadButton("Export Safetensors", variant="outline", size="sm")),
            ShadDropdownMenu(
                trigger=ShadButton("Deploy to Cluster", variant="default", size="sm"),
                content=[
                    ShadDropdownItem("Deploy to H100 GPU Cluster", icon="cpu", shortcut="⌘D"),
                    ShadDropdownItem("Deploy to AWS Inferentia2", icon="box"),
                    ShadDropdownSeparator(),
                    ShadDropdownItem("Undeploy Active Replicas", icon="x", danger=True)
                ]
            )
        ],
        theme_toggle=True,
        user={"avatar": "BR"}
    )

    # 3. Content Area with AI & ML Analytics
    content = [
        # KPI Metrics Row
        MetricCard(title="Inference Latency", value="14.2 ms", delta="-3.1 ms", delta_type="decrease", icon="⚡"),
        MetricCard(title="Throughput", value="1,840 tok/s", delta="+12.4%", delta_type="increase", icon="📈"),
        MetricCard(title="Cluster GPU VRAM", value="84.6%", delta="Optimal", delta_type="neutral", icon="🧠"),

        # Pipeline Status
        PipelineStatus(
            steps=[
                {"name": "Tokenization", "status": "completed", "duration": "1.2ms"},
                {"name": "KV Cache Lookup", "status": "completed", "duration": "0.8ms"},
                {"name": "FlashAttention-3", "status": "running", "duration": "10.4ms"},
                {"name": "Sampling & Detokenize", "status": "pending", "duration": "-"},
            ]
        ),

        # Precision ML Controls Row
        ShadCard(
            ShadCardHeader(
                ShadCardTitle("Hyperparameter Studio"),
                ShadCardDescription("Tune generation parameters in real-time with zero frontend code.")
            ),
            ShadCardContent(
                ShadSlider(
                    label="Sampling Temperature",
                    min_val=0.0,
                    max_val=2.0,
                    step=0.05,
                    value=0.7,
                    bind=ModelState.temperature
                ),
                ShadSlider(
                    label="Nucleus Sampling (top_p)",
                    min_val=0.1,
                    max_val=1.0,
                    step=0.01,
                    value=0.95,
                    bind=ModelState.top_p
                ),
                ShadRadioGroup(
                    name="engine",
                    value="vllm",
                    options=[
                        {"value": "vllm", "label": "vLLM PagedAttention Engine", "description": "High-throughput production serving", "badge": "Recommended"},
                        {"value": "tgi", "label": "HuggingFace TGI", "description": "Optimized tensor-parallel inference"},
                        {"value": "trt", "label": "NVIDIA TensorRT-LLM", "description": "Maximum kernel fusion speed"}
                    ]
                ),
                ShadDatePicker(label="Benchmark Run Date", value="2026-11-11", bind=ModelState.eval_date)
            )
        ),

        # Bento Card using from_jsx extensibility
        BentoFeatureCard(
            category="Vector Embeddings",
            badge="Healthy",
            title="Hybrid Sparse-Dense Embeddings",
            description="Powered by BGE-M3 model indexed across 2.4M chunks in Qdrant.",
            latency="p99: 18ms",
            action=ShadButton("Inspect Shards", variant="outline", size="sm")
        ),

        # Evaluation Confusion Matrix
        ConfusionMatrix(
            matrix=[[850, 42], [38, 910]],
            labels=["Hallucinated", "Grounded"],
            title="Grounding & RAG Factuality Evaluation"
        ),

        # Feature Importance
        FeatureImportance(
            features={
                "Prompt Length": 0.88,
                "Recency Bias": 0.72,
                "Chunk Relevance": 0.65,
                "Temperature": 0.42,
                "Context Density": 0.31
            },
            title="LLM Routing Feature Attribution"
        ),

        # Pagination
        ShadPagination(total_pages=5, current_page=1)
    ]

    # Return cohesive, full-stack DashboardLayout
    return DashboardLayout(
        sidebar=sidebar,
        header=header,
        content=content,
        collapsible="icon"
    )


if __name__ == "__main__":
    app.run(port=8000)
