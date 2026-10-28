"""
Mobile Progressive Web App (PWA) & Simulator Example for PyDataUI.

Features demonstrated:
- Zero Xcode & Zero Android Studio required for development or physical testing
- In-browser Mobile Simulator with device chassis (iPhone 15 Pro, Pixel 8, iPad Mini)
- Real physical device testing via instant QR Code scanning over local Wi-Fi
- Touch-friendly action buttons and cards sized for mobile thumbs
- Interactive state (Inspection checklist, quick status updates, counters)
- Safe-area aware layout with mobile top header and bottom navigation bar

To run in-browser Mobile Device Simulator:
    pydataui mobile preview examples/mobile_pwa_app.py
    
    or via run command:
    python examples/mobile_pwa_app.py --preview

To test on your real physical phone:
    1. Scan the QR code shown inside the mobile preview in your browser!
    2. Or open http://<your-lan-ip>:8000 on your phone, then tap 'Add to Home Screen'.
"""

from pydataui import App, State
from pydataui.components import (
    Container, Card, Flex, Button, Heading, Text, Badge, Input,
    Divider, Alert, Stat, Grid, Box
)
from pydantic import BaseModel
import uuid

class InspectionItem(BaseModel):
    id: str
    title: str
    category: str
    status: str = "pending"  # "passed", "failed", "pending"

class MobileAppState(State):
    inspector_name: str = "Alex Morgan"
    current_tab: str = "checklist"  # checklist, stats, settings
    new_task_title: str = ""
    items: list[InspectionItem] = [
        InspectionItem(id="1", title="Emergency Lighting & Exit Signs", category="Safety", status="passed"),
        InspectionItem(id="2", title="HVAC Airflow & Filter Check", category="Facilities", status="pending"),
        InspectionItem(id="3", title="Server Rack UPS Battery Health", category="IT Infrastructure", status="pending"),
        InspectionItem(id="4", title="Fire Suppression Pressure Gauge", category="Safety", status="passed"),
    ]

    def set_tab(self, tab: str):
        self.current_tab = tab

    def mark_passed(self, item_id: str):
        for item in self.items:
            if item.id == item_id:
                item.status = "passed"

    def mark_failed(self, item_id: str):
        for item in self.items:
            if item.id == item_id:
                item.status = "failed"

    def add_custom_item(self):
        if self.new_task_title.strip():
            self.items.append(
                InspectionItem(
                    id=uuid.uuid4().hex[:8],
                    title=self.new_task_title.strip(),
                    category="Custom Check",
                    status="pending"
                )
            )
            self.new_task_title = ""

    def reset_all(self):
        for item in self.items:
            item.status = "pending"


# Initialize App with PWA enabled for mobile
app = App(
    title="Field Inspector PWA",
    pwa=True,
    pwa_name="Field Inspector",
    pwa_short_name="Inspector",
    theme="dark",
    palette="zinc"
)


@app.page("/")
def mobile_home():
    total_count = len(MobileAppState.items)
    passed_count = sum(1 for x in MobileAppState.items if x.status == "passed")
    failed_count = sum(1 for x in MobileAppState.items if x.status == "failed")
    pending_count = total_count - passed_count - failed_count

    # Header section
    header = Card(
        children=[
            Flex(
                Flex(
                    Heading("📱 Field Inspector", level=2),
                    Text(f"Inspector: {MobileAppState.inspector_name}", size="sm", color="muted"),
                    direction="column",
                    gap="none"
                ),
                Badge("Online", variant="success"),
                justify="space-between",
                align="center"
            )
        ],
        padding="md"
    )

    # Quick Stats bar
    stats_bar = Grid(
        Card(Stat("Completed", f"{passed_count}/{total_count}"), padding="sm"),
        Card(Stat("Needs Fix", str(failed_count)), padding="sm"),
        Card(Stat("Pending", str(pending_count)), padding="sm"),
        cols=3,
        gap="sm"
    )

    # Checklist cards
    item_cards = []
    for item in MobileAppState.items:
        badge_variant = "success" if item.status == "passed" else ("danger" if item.status == "failed" else "secondary")
        badge_text = item.status.upper()

        card = Card(
            children=[
                Flex(
                    Flex(
                        Heading(item.title, level=4),
                        Text(item.category, size="xs", color="muted"),
                        direction="column",
                        gap="none"
                    ),
                    Badge(badge_text, variant=badge_variant),
                    justify="space-between",
                    align="start"
                ),
                Divider(),
                Flex(
                    Button(
                        "✓ Pass",
                        on_click=lambda id=item.id: MobileAppState.mark_passed(id),
                        variant="success" if item.status == "passed" else "outline",
                        full_width=True,
                        size="sm"
                    ),
                    Button(
                        "✕ Fail",
                        on_click=lambda id=item.id: MobileAppState.mark_failed(id),
                        variant="danger" if item.status == "failed" else "outline",
                        full_width=True,
                        size="sm"
                    ),
                    gap="sm"
                )
            ],
            padding="md"
        )
        item_cards.append(card)

    # Add item form
    add_form = Card(
        title="Add Checklist Item",
        children=[
            Flex(
                Input(
                    placeholder="New inspection point...",
                    bind=MobileAppState.new_task_title,
                    full_width=True
                ),
                Button("Add", on_click=MobileAppState.add_custom_item, variant="primary"),
                gap="sm"
            )
        ],
        padding="md"
    )

    # Quick action footer / reset
    footer_actions = Card(
        children=[
            Flex(
                Button("Reset All Statuses", on_click=MobileAppState.reset_all, variant="outline", full_width=True, size="sm"),
                direction="column",
                gap="sm"
            )
        ],
        padding="sm"
    )

    return Container(
        Flex(
            header,
            stats_bar,
            *item_cards,
            add_form,
            footer_actions,
            direction="column",
            gap="md"
        ),
        max_width="sm",  # Optimal mobile width
        padding="sm"
    )


if __name__ == "__main__":
    import sys
    is_preview = "--preview" in sys.argv or "--mobile-preview" in sys.argv
    app.run(host="0.0.0.0", port=8000, mobile_preview=is_preview)
