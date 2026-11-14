"""settings.py - Application Settings & Configuration Page

Demonstrates:
- Form submission with explicit field names
- Text input, Slider, and Button components
- Saving state feedback banners
"""

import pydataui as pdu
try:
    from ..state import settings_state
    from ..actions import save_settings
    from ..components import AppShell
except ImportError:
    from state import settings_state
    from actions import save_settings
    from components import AppShell


def SettingsPage() -> pdu.Container:
    """Renders the settings and preferences view."""

    feedback = None
    if settings_state.saved_feedback:
        feedback = pdu.Card(
            pdu.Row(
                pdu.Badge("Saved", variant="secondary", class_name="text-emerald-500 font-semibold"),
                pdu.Text(settings_state.saved_feedback, class_name="text-sm font-medium text-emerald-600"),
                class_name="items-center space-x-2"
            ),
            class_name="p-3 bg-emerald-50/50 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-800 mb-6"
        )

    form_section = pdu.Card(
        pdu.Form(
            pdu.Col(
                # Email Input
                pdu.Col(
                    pdu.Text("Alert Notification Email", class_name="text-sm font-semibold mb-1"),
                    pdu.Input(
                        placeholder="e.g. alerts@company.com",
                        name="alert_email",
                        value=settings_state.alert_email,
                        class_name="w-full"
                    ),
                    pdu.Text("Incident alerts and threshold violations will be routed here.", class_name="text-xs text-muted-foreground mt-1"),
                    class_name="mb-5"
                ),

                # API Rate Limit Input
                pdu.Col(
                    pdu.Text("Global API Rate Limit (req / min)", class_name="text-sm font-semibold mb-1"),
                    pdu.Input(
                        type="number",
                        name="api_rate_limit",
                        value=settings_state.api_rate_limit,
                        class_name="w-full"
                    ),
                    pdu.Text("Maximum requests allowed per client IP before HTTP 429 throttling.", class_name="text-xs text-muted-foreground mt-1"),
                    class_name="mb-6"
                ),

                # Submit Button
                pdu.Button(
                    "Save Configuration",
                    type="submit",
                    variant="primary",
                    class_name="w-full sm:w-auto"
                ),
                class_name="space-y-2"
            ),
            on_submit=save_settings
        ),
        class_name="p-6 border border-border"
    )

    body = pdu.Col(
        feedback if feedback else None,
        form_section
    )

    return AppShell(
        title="System Preferences & Configuration",
        subtitle="Manage alert destinations, rate limits, and cluster policy thresholds",
        content=body,
        current_path="/settings"
    )
