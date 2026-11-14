"""kpi_card.py - Reusable High-Contrast Metric Card Component

Demonstrates building custom composable UI widgets that accept reactive state
variables or raw values.
"""

from typing import Any, Optional
import pydataui as pdu


def KpiCard(
    title: str,
    value: Any,
    subtitle: Optional[str] = None,
    trend: Optional[str] = None,
    is_positive: bool = True
) -> pdu.Card:
    """Renders a modern metric card with trend indicator."""
    
    trend_badge = None
    if trend:
        badge_variant = "secondary"
        color_class = "text-emerald-500 font-semibold" if is_positive else "text-rose-500 font-semibold"
        trend_badge = pdu.Badge(trend, variant=badge_variant, class_name=f"text-xs {color_class}")

    top_row = pdu.Row(
        pdu.Text(title, class_name="text-xs font-semibold uppercase tracking-wider text-muted-foreground"),
        trend_badge if trend_badge else pdu.Text(""),
        class_name="justify-between items-center w-full"
    )

    body = pdu.Col(
        top_row,
        pdu.Heading(value, level=2, class_name="text-3xl font-bold tracking-tight mt-2"),
        pdu.Text(subtitle, class_name="text-xs text-muted-foreground mt-1") if subtitle else None,
        class_name="space-y-1"
    )

    return pdu.Card(body, class_name="p-5 border border-border bg-card shadow-sm hover:shadow transition-shadow")
