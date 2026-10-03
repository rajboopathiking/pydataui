from pydataui.components.shadcn import (
    ShadButton, ShadCard, ShadCardHeader, ShadCardTitle, ShadCardDescription,
    ShadCardContent, ShadCardFooter, ShadInput, ShadCheckbox, ShadBadge, ShadAlert,
    ShadSeparator, ShadProgress, ShadSkeleton, ShadSwitch, ShadTable,
    ShadSelect, ShadTextarea, ShadLabel, ShadDialog, ShadScrollArea,
    ShadTabs, ShadToast, ShadAvatar, ShadHoverCard, ShadAccordion, ShadSheet
)

def test_shad_button_variants():
    default_btn = ShadButton("Submit")
    assert "bg-primary" in default_btn.render({})

    dest_btn = ShadButton("Delete", variant="destructive")
    assert "bg-destructive" in dest_btn.render({})

    outline_btn = ShadButton("Cancel", variant="outline")
    assert "border" in outline_btn.render({})

def test_shad_card_hierarchy():
    card = ShadCard(
        ShadCardHeader(
            ShadCardTitle("Model Card"),
            ShadCardDescription("XGBoost classifier details")
        ),
        ShadCardContent(
            ShadBadge("Production", variant="default")
        ),
        ShadCardFooter(
            ShadButton("Deploy")
        )
    )
    html = card.render({})
    assert "Model Card" in html
    assert "XGBoost classifier details" in html
    assert "Production" in html
    assert "Deploy" in html

def test_shad_form_controls():
    inp = ShadInput(placeholder="email@example.com")
    assert "ring-offset-background" in inp.render({})

    sw = ShadSwitch(checked=True, name="notifications", label="Enable Alerts")
    sw_html = sw.render({})
    assert 'role="switch"' in sw_html
    assert 'aria-checked="true"' in sw_html
    assert 'name="notifications"' in sw_html
    assert 'Enable Alerts' in sw_html

    chk = ShadCheckbox(label="I accept terms", checked=True, name="terms")
    chk_html = chk.render({})
    assert 'type="checkbox"' in chk_html
    assert 'name="terms"' in chk_html
    assert 'checked="checked"' in chk_html
    assert 'I accept terms' in chk_html

    sel = ShadSelect(options=[{"value": "cpu", "label": "CPU"}, {"value": "gpu", "label": "GPU"}], value="gpu", name="device")
    sel_html = sel.render({})
    assert '<select' in sel_html
    assert 'name="device"' in sel_html
    assert '<option value="gpu" selected>GPU</option>' in sel_html

    prog = ShadProgress(value=75, max_val=100)
    assert 'aria-valuenow="75"' in prog.render({})

def test_shad_dialog_and_sheet():
    # Closed dialog returns empty string
    d_closed = ShadDialog("Hidden content", open=False)
    assert d_closed.render({}) == ""

    # Open dialog returns backdrop, title, and close button
    from pydataui.state import EventHandler
    dummy_close = EventHandler("TestState", "close")
    d_open = ShadDialog("Visible content", open=True, title="Confirm Action", on_close=dummy_close)
    html = d_open.render({})
    assert "Visible content" in html
    assert "backdrop-blur-sm" in html
    assert "Confirm Action" in html
    assert 'hx-post="/_pdu/event/TestState/close"' in html

    # Open sheet
    sheet = ShadSheet("Drawer content", open=True, side="right", title="Settings Drawer", on_close=dummy_close)
    html_sheet = sheet.render({})
    assert "Drawer content" in html_sheet
    assert "border-l" in html_sheet
    assert "Settings Drawer" in html_sheet
    assert 'hx-post="/_pdu/event/TestState/close"' in html_sheet
