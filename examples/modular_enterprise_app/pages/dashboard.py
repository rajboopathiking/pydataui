"""dashboard.py - Analytics & Telemetry Page

Demonstrates:
- Reusable component composition with AppShell & KpiCard
- Real-time reactive state updates (workers, throughput, error rates)
- Action buttons modifying state
"""

import pydataui as pdu
try:
    from ..state import dashboard_state
    from ..actions import scale_up_workers, scale_down_workers, toggle_system_stress
    from ..components import AppShell, KpiCard
except ImportError:
    from state import dashboard_state
    from actions import scale_up_workers, scale_down_workers, toggle_system_stress
    from components import AppShell, KpiCard


def DashboardPage() -> pdu.Container:
    """Renders the real-time operational dashboard."""
    
    # 1. KPI Metric Grid
    kpi_grid = pdu.Grid(
        KpiCard(
            title="Active Workers",
            value=dashboard_state.active_workers,
            subtitle="Distributed Celery/Ray cluster nodes",
            trend="+4 auto-scale",
            is_positive=True
        ),
        KpiCard(
            title="Ingestion Rate",
            value=pdu.Row(
                pdu.Heading(dashboard_state.throughput_k, level=2, class_name="text-3xl font-bold"),
                pdu.Text("k req/s", class_name="text-sm text-muted-foreground self-end mb-1 ml-1")
            ),
            subtitle="Kafka real-time streaming buffer",
            trend="+15.2%",
            is_positive=True
        ),
        KpiCard(
            title="Error Rate",
            value=pdu.Row(
                pdu.Heading(dashboard_state.error_rate, level=2, class_name="text-3xl font-bold text-rose-500"),
                pdu.Text("%", class_name="text-sm text-muted-foreground self-end mb-1 ml-1")
            ),
            subtitle="5xx HTTP & worker timeout exceptions",
            trend="Within SLA",
            is_positive=True
        ),
        KpiCard(
            title="System Status",
            value=dashboard_state.system_status,
            subtitle="Global multi-region quorum",
            trend="Healthy",
            is_positive=True
        ),
        columns=4,
        class_name="gap-4 mb-8"
    )

    # 2. Control Toolbar
    controls = pdu.Card(
        pdu.Row(
            pdu.Col(
                pdu.Heading("Cluster Orchestrator Actions", level=3, class_name="text-base font-semibold"),
                pdu.Text("Scale worker pods up or down to test reactive HTMX state updates without page reload.", class_name="text-xs text-muted-foreground")
            ),
            pdu.Row(
                pdu.Button(
                    "Scale +4 Workers",
                    on_click=scale_up_workers,
                    variant="primary",
                    size="sm"
                ),
                pdu.Button(
                    "Scale -4 Workers",
                    on_click=scale_down_workers,
                    variant="outline",
                    size="sm"
                ),
                pdu.Button(
                    "Toggle Stress Test",
                    on_click=toggle_system_stress,
                    variant="secondary",
                    size="sm"
                ),
                class_name="space-x-2"
            ),
            class_name="justify-between items-center"
        ),
        class_name="p-4 mb-8 border border-border"
    )

    # 3. System Activity Card
    activity_section = pdu.Card(
        pdu.Col(
            pdu.Heading("Infrastructure Event Stream", level=3, class_name="text-lg font-semibold mb-2"),
            pdu.Text("Live telemetry streamed from internal Kubernetes pods and analytical databases.", class_name="text-xs text-muted-foreground mb-4"),
            
            pdu.Col(
                pdu.Row(
                    pdu.Badge("ETL", variant="secondary", class_name="text-xs"),
                    pdu.Text("Warehouse batch synchronization complete: 1,420,000 rows processed in 842ms", class_name="text-sm"),
                    pdu.Text("12s ago", class_name="text-xs text-muted-foreground ml-auto"),
                    class_name="items-center space-x-3 py-2 border-b border-border/50"
                ),
                pdu.Row(
                    pdu.Badge("DuckDB", variant="outline", class_name="text-xs"),
                    pdu.Text("In-memory analytical view created across 4 Parquet partitions", class_name="text-sm"),
                    pdu.Text("45s ago", class_name="text-xs text-muted-foreground ml-auto"),
                    class_name="items-center space-x-3 py-2 border-b border-border/50"
                ),
                pdu.Row(
                    pdu.Badge("Rust Core", variant="default", class_name="text-xs"),
                    pdu.Text("PyRustAPI server bridge serving 112,000 req/s with 0.8ms P99 latency", class_name="text-sm"),
                    pdu.Text("2m ago", class_name="text-xs text-muted-foreground ml-auto"),
                    class_name="items-center space-x-3 py-2"
                ),
                class_name="space-y-1"
            )
        ),
        class_name="p-6 border border-border"
    )

    body = pdu.Col(
        kpi_grid,
        controls,
        activity_section
    )

    return AppShell(
        title="Real-Time Analytics Dashboard",
        subtitle="Live telemetry and distributed worker orchestration powered by PyDataUI",
        content=body,
        current_path="/"
    )
