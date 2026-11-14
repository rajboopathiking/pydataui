"""data_hub.py - Tabular Data Operations & Search Page

Demonstrates:
- Search filter input with explicit name="query" and on_change
- Region filter buttons
- Universal DataTable with schema sniffing and pagination
- Adding new records to state
"""

import pydataui as pdu
try:
    from ..state import data_hub_state
    from ..actions import filter_region, search_nodes, add_random_node
    from ..components import AppShell
except ImportError:
    from state import data_hub_state
    from actions import filter_region, search_nodes, add_random_node
    from components import AppShell


def DataHubPage() -> pdu.Container:
    """Renders the cluster nodes inventory & search table."""

    # 1. Filter & Search Toolbar
    toolbar = pdu.Card(
        pdu.Row(
            # Search input with explicit name="query"
            pdu.Form(
                pdu.Row(
                    pdu.Input(
                        placeholder="Search nodes by ID or status...",
                        name="query",
                        value=data_hub_state.search_query,
                        class_name="w-64"
                    ),
                    pdu.Button("Search", type="submit", variant="secondary", size="sm"),
                    class_name="space-x-2 items-center"
                ),
                on_submit=search_nodes
            ),

            # Region Filter Button Group
            pdu.Row(
                pdu.Button("All", on_click=lambda: filter_region("ALL"), variant="outline", size="sm"),
                pdu.Button("US-East", on_click=lambda: filter_region("US-East"), variant="outline", size="sm"),
                pdu.Button("EU-Central", on_click=lambda: filter_region("EU-Central"), variant="outline", size="sm"),
                pdu.Button("AP-South", on_click=lambda: filter_region("AP-South"), variant="outline", size="sm"),
                pdu.Button("+ Add Node", on_click=add_random_node, variant="primary", size="sm"),
                class_name="space-x-2 items-center"
            ),

            class_name="justify-between items-center"
        ),
        class_name="p-4 mb-6 border border-border"
    )

    # 2. Universal DataTable
    table_section = pdu.Card(
        pdu.Col(
            pdu.Row(
                pdu.Heading("Active Node Inventory", level=3, class_name="text-lg font-semibold"),
                pdu.Badge(f"Total: {data_hub_state.total_nodes} nodes", variant="secondary"),
                class_name="justify-between items-center mb-4"
            ),
            pdu.DataTable(
                data=data_hub_state.records,
                sortable=True,
                pagination=True,
                page_size=5,
                class_name="w-full"
            )
        ),
        class_name="p-6 border border-border"
    )

    body = pdu.Col(
        toolbar,
        table_section
    )

    return AppShell(
        title="Cluster Node Data Hub",
        subtitle="Manage distributed server instances with real-time filtering and sorting",
        content=body,
        current_path="/data"
    )
