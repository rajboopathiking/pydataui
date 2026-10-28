"""
Desktop Application Example for PyDataUI.

Features demonstrated:
- Standalone desktop application window with zero browser tabs or URL bar
- Multi-column widescreen dashboard optimized for desktop monitors
- Real-time reactive state: Service status management, KPI metrics, log stream
- Works out-of-the-box with native desktop window or Tauri 2.0 shell

To run in standalone desktop window:
    python examples/desktop_app.py --desktop
    
    or via CLI:
    pydataui run examples/desktop_app.py --desktop

To run standard web server:
    python examples/desktop_app.py
"""

import sys
import time
from pydataui import App, State
from pydataui.components import (
    Container, Card, Flex, Button, Heading, Text, Badge, Input,
    Divider, Grid, Stat, Alert, Table, TableTag, TheadTag, TbodyTag, TrTag, ThTag, TdTag
)
from pydantic import BaseModel

class ServiceInfo(BaseModel):
    id: str
    name: str
    port: int
    status: str      # "RUNNING", "STOPPED", "DEGRADED"
    uptime: str
    cpu: str

class DesktopAppState(State):
    cluster_name: str = "Production-US-East"
    active_connections: int = 1420
    system_cpu: str = "24.8%"
    system_ram: str = "6.2 GB / 32 GB"
    services: list[ServiceInfo] = [
        ServiceInfo(id="srv-1", name="PostgreSQL Primary Cluster", port=5432, status="RUNNING", uptime="14d 8h", cpu="12.4%"),
        ServiceInfo(id="srv-2", name="Redis Cache & PubSub", port=6379, status="RUNNING", uptime="28d 2h", cpu="3.1%"),
        ServiceInfo(id="srv-3", name="ML Inference Worker Group", port=8001, status="RUNNING", uptime="2d 11h", cpu="44.2%"),
        ServiceInfo(id="srv-4", name="Async Task Celery Queue", port=5555, status="STOPPED", uptime="0h", cpu="0.0%"),
    ]
    last_action_msg: str = "Desktop Hub initialized. All systems normal."

    def toggle_service(self, srv_id: str):
        for srv in self.services:
            if srv.id == srv_id:
                if srv.status == "RUNNING":
                    srv.status = "STOPPED"
                    srv.uptime = "0h"
                    srv.cpu = "0.0%"
                    self.last_action_msg = f"Service '{srv.name}' has been stopped."
                else:
                    srv.status = "RUNNING"
                    srv.uptime = "Just started"
                    srv.cpu = "4.5%"
                    self.last_action_msg = f"Service '{srv.name}' restarted successfully."

    def refresh_metrics(self):
        import random
        self.active_connections = random.randint(1200, 1800)
        self.system_cpu = f"{random.uniform(18.0, 35.0):.1f}%"
        self.last_action_msg = f"Metrics refreshed at {time.strftime('%H:%M:%S')}."


# Initialize desktop app with dark slate palette
app = App(
    title="Desktop Operations Hub",
    theme="dark",
    palette="slate",
    debug=False
)


@app.page("/")
def desktop_dashboard():
    running_count = sum(1 for s in DesktopAppState.services if s.status == "RUNNING")
    total_count = len(DesktopAppState.services)

    # Top Navigation Bar
    navbar = Card(
        children=[
            Flex(
                Flex(
                    Heading("🖥️ Desktop Operations Hub", level=2),
                    Badge(DesktopAppState.cluster_name, variant="secondary"),
                    align="center",
                    gap="md"
                ),
                Flex(
                    Button("↻ Refresh Metrics", on_click=DesktopAppState.refresh_metrics, variant="outline", size="sm"),
                    Button("Export Snapshot", variant="secondary", size="sm"),
                    gap="sm",
                    align="center"
                ),
                justify="space-between",
                align="center"
            )
        ],
        padding="md"
    )

    # KPI Metric Cards
    kpis = Grid(
        Card(Stat("Services Active", f"{running_count} / {total_count}"), padding="md"),
        Card(Stat("Active Connections", f"{DesktopAppState.active_connections:,}"), padding="md"),
        Card(Stat("System CPU", DesktopAppState.system_cpu), padding="md"),
        Card(Stat("Memory Usage", DesktopAppState.system_ram), padding="md"),
        cols=4,
        gap="md"
    )

    # Status notice banner
    notice = Alert(DesktopAppState.last_action_msg, variant="info")

    # Service table rows
    table_rows = []
    for srv in DesktopAppState.services:
        is_running = srv.status == "RUNNING"
        badge_variant = "success" if is_running else "danger"
        toggle_label = "Stop" if is_running else "Start"
        toggle_variant = "danger" if is_running else "success"

        row = TrTag(
            TdTag(Text(srv.name, weight="semibold")),
            TdTag(Text(str(srv.port), color="muted")),
            TdTag(Badge(srv.status, variant=badge_variant)),
            TdTag(Text(srv.uptime, color="muted")),
            TdTag(Text(srv.cpu, color="muted")),
            TdTag(
                Button(
                    toggle_label,
                    on_click=lambda id=srv.id: DesktopAppState.toggle_service(id),
                    variant=toggle_variant,
                    size="sm"
                )
            )
        )
        table_rows.append(row)

    services_table = Card(
        title="Microservices & Cluster Daemons",
        children=[
            TableTag(
                TheadTag(
                    TrTag(
                        ThTag("Service Name"),
                        ThTag("Port"),
                        ThTag("Status"),
                        ThTag("Uptime"),
                        ThTag("CPU Usage"),
                        ThTag("Control"),
                    )
                ),
                TbodyTag(*table_rows),
                class_name="w-full text-left"
            )
        ],
        padding="md"
    )

    return Container(
        Flex(
            navbar,
            notice,
            kpis,
            services_table,
            direction="column",
            gap="lg"
        ),
        max_width="7xl",
        padding="lg"
    )


if __name__ == "__main__":
    # Check if --desktop flag was passed in command line
    launch_desktop = "--desktop" in sys.argv
    app.run(
        host="127.0.0.1",
        port=8050,
        desktop=launch_desktop
    )
