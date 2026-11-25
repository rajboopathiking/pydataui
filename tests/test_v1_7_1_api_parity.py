import pydataui as pdu


def test_version_1_7_1():
    assert pdu.__version__ == "1.7.1"


def test_all_track1_apis_exist():
    expected_track1 = [
        "set_page_config", "title", "header", "subheader", "sidebar", "tabs",
        "page", "switch_page", "expander", "dialog", "pinned",
        "container", "columns", "flex", "row", "column", "grid", "card",
        "scrollable", "spacer", "divider",
        "write", "markdown", "text", "caption", "code", "json", "image",
        "video", "audio", "dataframe", "table", "metric",
        "text_input", "text_area", "number_input", "password_input",
        "selectbox", "multiselect", "checkbox", "radio", "toggle",
        "slider", "file_uploader", "date_input", "time_input", "search_input",
        "button", "form", "form_submit_button", "download_button", "link_button",
        "line_chart", "bar_chart", "area_chart", "plotly_chart",
        "stat_card", "sparkline", "progress",
        "success", "error", "warning", "info", "toast", "badge", "spinner", "status",
        "chat_message", "chat_input",
        "create_user", "login", "logout", "session_state", "get_fastapi", "mount",
    ]
    missing = [name for name in expected_track1 if not hasattr(pdu, name)]
    assert missing == [], f"Missing Track 1 APIs: {missing}"


def test_all_track2_top_level_exports_exist():
    expected_track2 = [
        "Container", "Flex", "Grid", "Stack", "HStack", "VStack", "Box", "Center", "Divider", "Card",
        "Heading", "Text", "Paragraph", "Markdown", "Code", "Blockquote", "Link", "JSONViewer",
        "Input", "TextArea", "Select", "Checkbox", "Radio", "Switch", "Slider", "FileUpload", "Button", "DatePicker",
        "BarChart", "LineChart", "PieChart", "DoughnutChart", "Sparkline", "PlotlyChart", "MetricCard", "Stat", "Progress",
        "DataFrameTable", "DataTable", "ModelMetrics", "ConfusionMatrix", "FeatureImportance",
        "PipelineStatus", "DataTimeline", "SchemaViewer", "SQLEditor", "FileDownload",
        "ShadButton", "ShadCard", "ShadBadge", "ShadAlert", "ShadSeparator", "ShadProgress",
        "ShadSkeleton", "ShadSwitch", "ShadTable", "ShadSelect", "ShadTextarea", "ShadLabel",
        "ShadDialog", "ShadScrollArea", "ShadTabs", "ShadToast", "ShadAvatar", "ShadHoverCard",
        "ShadAccordion", "ShadSheet",
    ]
    missing = [name for name in expected_track2 if not hasattr(pdu, name)]
    assert missing == [], f"Missing Track 2 exports: {missing}"


def test_new_v1_7_1_widgets_render():
    pdu.reset()
    pw = pdu.password_input("API Key", placeholder="sk-...")
    assert 'type="password"' in pw.render({})

    lb = pdu.link_button("Docs", url="https://github.com/rajboopathiking/pydataui")
    lb_html = lb.render({})
    assert "https://github.com/rajboopathiking/pydataui" in lb_html
    assert "Docs" in lb_html

    db = pdu.download_button("Export JSON", data={"ok": True}, file_name="out.json")
    db_html = db.render({})
    assert 'download="out.json"' in db_html
    assert "Export JSON" in db_html

    dp = pdu.DatePicker(label="Start Date", value="2026-11-25")
    dp_html = dp.render({})
    assert 'type="date"' in dp_html
    assert "2026-11-25" in dp_html
    pdu.reset()
