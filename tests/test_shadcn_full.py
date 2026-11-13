import pytest
from pydataui.shadcn import (
    # Core & Layout
    ShadButton, ShadCard,
    ShadSidebarProvider, ShadSidebar, ShadSidebarHeader, ShadSidebarContent,
    ShadSidebarGroup, ShadSidebarGroupLabel, ShadSidebarMenu, ShadSidebarMenuItem,
    ShadSidebarMenuButton, ShadSidebarFooter, ShadSidebarRail, ShadSidebarTrigger,
    # High-level
    Sidebar, Header, DashboardLayout, NavGroup, NavItem,
    # Breadcrumbs
    ShadBreadcrumb, ShadBreadcrumbList, ShadBreadcrumbItem, ShadBreadcrumbLink,
    ShadBreadcrumbPage, ShadBreadcrumbSeparator,
    # Overlays
    ShadDropdownMenu, ShadDropdownItem, ShadDropdownSeparator, ShadDropdownLabel,
    ShadPopover, ShadTooltip, ShadAlertDialog, ShadCommandPalette,
    # Controls
    ShadSlider, ShadRadioGroup, ShadDatePicker, ShadPagination,
    # Extensibility
    create_shadcn_component, from_jsx, from_html, dynamic,
    LUCIDE_ICONS
)


def test_sidebar_system_render():
    provider = ShadSidebarProvider(default_open=True, collapsible="icon")
    provider_html = provider.render({})
    assert 'data-sidebar-provider="true"' in provider_html
    assert 'data-state="expanded"' in provider_html
    assert 'data-collapsible="icon"' in provider_html

    sidebar = ShadSidebar(
        ShadSidebarHeader("Test Header"),
        ShadSidebarContent(
            ShadSidebarGroup(
                ShadSidebarGroupLabel("Navigation"),
                ShadSidebarMenu(
                    ShadSidebarMenuItem(
                        ShadSidebarMenuButton("Dashboard", icon="layout-dashboard", active=True, badge="9+")
                    )
                )
            )
        ),
        ShadSidebarFooter("User profile"),
        ShadSidebarRail(),
        collapsible="icon"
    )
    sb_html = sidebar.render({})
    assert "<aside" in sb_html
    assert "Test Header" in sb_html
    assert "Navigation" in sb_html
    assert "Dashboard" in sb_html
    assert "9+" in sb_html
    assert "User profile" in sb_html
    assert 'data-pdu-sidebar-rail="true"' in sb_html
    assert 'data-pdu-sidebar-backdrop="true"' in sb_html

    # Trigger button
    trig = ShadSidebarTrigger()
    trig_html = trig.render({})
    assert 'data-pdu-sidebar-trigger="true"' in trig_html
    assert "<svg" in trig_html


def test_declarative_dashboard_and_header():
    sb = Sidebar(
        brand={"name": "PyDataUI Platform", "logo": "cpu", "plan": "Enterprise"},
        groups=[
            NavGroup("Platform", [
                NavItem("Models", icon="box", href="/models", active=True, badge="12"),
                NavItem("Telemetry", icon="activity", href="/telemetry")
            ])
        ],
        footer={"name": "PyDataUI Admin", "email": "admin@pydataui.org", "avatar": "UI"}
    )
    sb_html = sb.render({})
    assert "PyDataUI Platform" in sb_html
    assert "Enterprise" in sb_html
    assert "Models" in sb_html
    assert "12" in sb_html
    assert "Telemetry" in sb_html
    assert "PyDataUI Admin" in sb_html
    assert "admin@pydataui.org" in sb_html

    hdr = Header(
        breadcrumbs=["Home", "Models", "Mistral-7B"],
        search=True,
        actions=[ShadButton("Deploy")]
    )
    hdr_html = hdr.render({})
    assert "Mistral-7B" in hdr_html
    assert "Deploy" in hdr_html
    assert "data-pdu-command-trigger" in hdr_html
    assert "⌘K" in hdr_html

    # Full layout
    layout = DashboardLayout(
        sidebar=sb,
        header=hdr,
        content=[ShadCard("Model Performance Metrics")]
    )
    layout_html = layout.render({})
    assert "PyDataUI Platform" in layout_html
    assert "Mistral-7B" in layout_html
    assert "Model Performance Metrics" in layout_html


def test_breadcrumbs_hierarchy():
    bc = ShadBreadcrumb(
        ShadBreadcrumbList(
            ShadBreadcrumbItem(ShadBreadcrumbLink("Home", href="/")),
            ShadBreadcrumbSeparator(),
            ShadBreadcrumbItem(ShadBreadcrumbPage("Settings"))
        )
    )
    bc_html = bc.render({})
    assert '<nav' in bc_html
    assert 'aria-label="breadcrumb"' in bc_html
    assert 'href="/"' in bc_html
    assert 'aria-current="page"' in bc_html
    assert "Settings" in bc_html


def test_overlays_dropdown_popover_tooltip():
    # DropdownMenu
    dd = ShadDropdownMenu(
        trigger=ShadButton("Options"),
        content=[
            ShadDropdownLabel("Actions"),
            ShadDropdownItem("Profile", icon="user", shortcut="⌘P"),
            ShadDropdownSeparator(),
            ShadDropdownItem("Delete Account", icon="x", danger=True)
        ]
    )
    dd_html = dd.render({})
    assert 'data-pdu-dropdown="true"' in dd_html
    assert 'data-pdu-dropdown-trigger="true"' in dd_html
    assert "Profile" in dd_html
    assert "⌘P" in dd_html
    assert "text-destructive" in dd_html

    # Popover
    pop = ShadPopover(
        trigger=ShadButton("Info"),
        content="Rich popover details"
    )
    pop_html = pop.render({})
    assert 'data-pdu-popover="true"' in pop_html
    assert "Rich popover details" in pop_html

    # Tooltip
    tt = ShadTooltip("Quick Help", ShadButton("Hover me"))
    tt_html = tt.render({})
    assert 'role="tooltip"' in tt_html
    assert "Quick Help" in tt_html
    assert "Hover me" in tt_html


def test_alert_dialog_and_command():
    # Alert dialog closed vs open
    ad_closed = ShadAlertDialog(title="Delete Database?", open=False)
    assert ad_closed.render({}) == ""

    ad_open = ShadAlertDialog(title="Delete Database?", description="Cannot be recovered.", open=True)
    ad_html = ad_open.render({})
    assert "Delete Database?" in ad_html
    assert "Cannot be recovered." in ad_html
    assert "Continue" in ad_html

    # Command palette
    cmd = ShadCommandPalette(
        items=[
            {"label": "Clone Repository", "category": "Git", "shortcut": "⌘C"},
            {"label": "Deploy Production", "category": "CI/CD"}
        ]
    )
    cmd_html = cmd.render({})
    assert 'data-pdu-command-palette="true"' in cmd_html
    assert "Clone Repository" in cmd_html
    assert "Deploy Production" in cmd_html
    assert "⌘C" in cmd_html


def test_precision_inputs_slider_radio_date_pagination():
    # Slider
    slider = ShadSlider(min_val=0.0, max_val=2.0, step=0.1, value=0.7, label="Temperature", name="temp")
    sl_html = slider.render({})
    assert 'type="range"' in sl_html
    assert 'min="0.0"' in sl_html
    assert 'max="2.0"' in sl_html
    assert 'value="0.7"' in sl_html
    assert 'Temperature' in sl_html

    # RadioGroup
    rg = ShadRadioGroup(
        name="model",
        value="gpt4",
        options=[
            {"value": "gpt4", "label": "GPT-4o", "description": "High reasoning", "badge": "Fast"},
            {"value": "claude", "label": "Claude 3.5 Sonnet", "description": "Superior code"}
        ]
    )
    rg_html = rg.render({})
    assert 'role="radiogroup"' in rg_html
    assert 'value="gpt4" checked' in rg_html
    assert 'value="claude"' in rg_html
    assert 'High reasoning' in rg_html
    assert 'Fast' in rg_html

    # DatePicker
    dp = ShadDatePicker(label="Evaluation Date", value="2026-11-11", name="eval_date")
    dp_html = dp.render({})
    assert 'type="date"' in dp_html
    assert 'value="2026-11-11"' in dp_html
    assert 'Evaluation Date' in dp_html

    # Pagination
    pag = ShadPagination(total_pages=5, current_page=2)
    pag_html = pag.render({})
    assert 'aria-label="pagination"' in pag_html
    assert 'Previous' in pag_html
    assert 'Next' in pag_html
    assert 'aria-current="page">2<' in pag_html


def test_component_factory():
    Kbd = create_shadcn_component(
        tag="kbd",
        base_classes="rounded border px-1.5 py-0.5 font-mono text-xs",
        variants={"dark": "bg-zinc-900 text-white", "light": "bg-zinc-100 text-zinc-900"},
        default_variant="dark",
        name="ShadKbd"
    )
    kbd_comp = Kbd("⌘K")
    html = kbd_comp.render({})
    assert "<kbd" in html
    assert "⌘K" in html
    assert "bg-zinc-900" in html


def test_universal_jsx_and_html_transpiler():
    # from_jsx
    NewBentoCard = from_jsx("""
    <div className="rounded-xl border bg-card text-card-foreground p-6 shadow-sm">
      <h3 className="font-bold text-lg">{title}</h3>
      <p className="text-sm text-muted-foreground">{description}</p>
      <div className="mt-4">{children}</div>
    </div>
    """)

    bento = NewBentoCard(
        title="Vector Search Node",
        description="Pinecone & Qdrant hybrid index",
        children=[ShadButton("Re-index")]
    )
    bento_html = bento.render({})
    assert 'class="rounded-xl border bg-card text-card-foreground p-6 shadow-sm"' in bento_html
    assert "Vector Search Node" in bento_html
    assert "Pinecone &amp; Qdrant hybrid index" in bento_html
    assert "Re-index" in bento_html

    # from_html
    HtmlPill = from_html('<span class="badge {color}">{label}</span>')
    pill = HtmlPill(color="bg-emerald-500", label="Healthy")
    assert pill.render({}) == '<span class="badge bg-emerald-500">Healthy</span>'

    # dynamic with dictionary schema
    DynComp = dynamic({"name": "CustomBento", "tag": "section", "tailwind": "grid grid-cols-3 gap-4"})
    dyn_inst = DynComp("Inner item")
    assert "<section" in dyn_inst.render({})
    assert "grid grid-cols-3 gap-4" in dyn_inst.render({})


def test_cli_add_generator(tmp_path):
    from pydataui.cli.add import generate_python_component_code
    schema = {
        "name": "carousel",
        "tag": "div",
        "tailwind": "relative w-full overflow-hidden",
        "files": [
            {"content": '<div className="flex gap-4 p-4 rounded-xl border bg-card">Carousel Content</div>'}
        ]
    }
    code = generate_python_component_code(schema, "carousel")
    assert "class Carousel(Component):" in code
    assert "relative w-full overflow-hidden" in code
