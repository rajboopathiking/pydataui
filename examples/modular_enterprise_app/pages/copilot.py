"""copilot.py - Conversational AI Copilot Page

Demonstrates:
- Dedicated Chat component with message history
- Quick suggestion chips
- Dynamic tokens counter
- Conversational state management
"""

import pydataui as pdu
try:
    from ..state import copilot_state
    from ..actions import handle_copilot_message, clear_copilot_chat
    from ..components import AppShell
except ImportError:
    from state import copilot_state
    from actions import handle_copilot_message, clear_copilot_chat
    from components import AppShell


def CopilotPage() -> pdu.Container:
    """Renders the AI copilot chat interface."""

    suggestions = [
        "How many nodes are currently active?",
        "What is the Kafka throughput?",
        "Generate a DuckDB query for average CPU",
        "Inspect high-stress worker pods"
    ]

    header_bar = pdu.Row(
        pdu.Row(
            pdu.Badge(copilot_state.active_model, variant="outline", class_name="font-mono text-xs"),
            pdu.Badge(f"Tokens: {copilot_state.total_tokens}", variant="secondary", class_name="text-xs"),
            class_name="space-x-2 items-center"
        ),
        pdu.Button("Clear History", on_click=clear_copilot_chat, variant="outline", size="sm"),
        class_name="justify-between items-center mb-6"
    )

    chat_box = pdu.Card(
        pdu.Chat(
            messages=copilot_state.messages,
            on_send=handle_copilot_message,
            on_clear=clear_copilot_chat,
            title="PyDataUI Copilot",
            placeholder="Ask about node telemetry, latency, or SQL aggregations...",
            suggestions=suggestions,
            loading=copilot_state.is_loading
        ),
        class_name="p-4 border border-border shadow-sm"
    )

    body = pdu.Col(
        header_bar,
        chat_box
    )

    return AppShell(
        title="AI Architecture Copilot",
        subtitle="Autonomous assistant for cluster diagnostics, metric queries, and pipeline advice",
        content=body,
        current_path="/copilot"
    )
