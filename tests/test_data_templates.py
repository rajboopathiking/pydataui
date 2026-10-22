import pytest

from pydataui import State
from pydataui.components import BarChart, Button, DataUpload, FileDownload, Input
from pydataui.templates import (
    analyst_dashboard,
    data_quality_dashboard,
    ml_registry,
    model_registry,
    pipeline_dashboard,
    pipeline_operations,
    quality_dashboard,
)


class TemplateState(State):
    metrics = {"Revenue": "$48,250", "Orders": "1,284"}
    rows = [{"Region": "North", "Revenue": "$12,400"}]
    score = 99.0
    schema = {"user_id": "int64"}
    issues = [{"Dataset": "orders", "Severity": "low", "Status": "resolved"}]
    pipeline = {
        "name": "warehouse_daily",
        "status": "healthy",
        "steps": [{"name": "Extract", "status": "success"}],
    }
    events = [{"time": "02:00", "label": "warehouse_daily started", "status": "success"}]
    model = {
        "name": "churn_classifier",
        "stage": "production",
        "metrics": {"AUC": 0.985},
    }


def test_analyst_dashboard_renders_filters_metrics_chart_table_and_export():
    html = analyst_dashboard(
        title="Revenue Analysis",
        subtitle="Weekly performance",
        metrics={
            "Net revenue": "$48,250",
            "Orders": "1,284",
            "Conversion": "4.8%",
        },
        filters=[
            Input("Region", placeholder="All regions"),
            Input("Period", value="Last 7 days"),
        ],
        chart=BarChart(
            labels=["Mon", "Tue", "Wed"],
            data=[120, 180, 160],
            label="Orders",
        ),
        table=[
            {"Region": "North", "Revenue": "$12,400", "Orders": 312},
            {"Region": "South", "Revenue": "$9,850", "Orders": 241},
        ],
        actions=[Button("Refresh")],
        export=FileDownload(
            filename="revenue.csv",
            content="region,revenue\nNorth,12400\n",
            label="Export CSV",
            mime_type="text/csv",
        ),
    ).render({})

    assert "Revenue Analysis" in html
    assert "Weekly performance" in html
    assert "Net revenue" in html
    assert "$48,250" in html
    assert "Filters" in html
    assert "All regions" in html
    assert "Performance trend" in html
    assert "<canvas" in html
    assert "Latest records" in html
    assert "North" in html
    assert "Refresh" in html
    assert "Export CSV" in html
    assert "data:text/csv;base64," in html
    assert "pdu-card" in html


def test_data_quality_dashboard_renders_score_catalog_schema_issues_and_upload():
    html = data_quality_dashboard(
        score=97.5,
        metrics={"Tables monitored": 142, "Open checks": 3},
        datasets=[
            {"Dataset": "orders", "Owner": "finance", "Rows": "4.2M", "Status": "Healthy"},
            {"Dataset": "events", "Owner": "growth", "Rows": "18.7M", "Status": "Stale"},
        ],
        schema={"user_id": "int64", "email": "varchar(255)", "created_at": "timestamp"},
        issues=[
            {
                "Dataset": "events",
                "Check": "freshness",
                "Severity": "high",
                "Status": "open",
                "Detail": "Latest partition is 6 hours old",
            }
        ],
        upload=DataUpload(accept=".csv,.json", on_upload="/api/upload"),
    ).render({})

    assert "Data Quality &amp; Catalog" in html
    assert "97.5%" in html
    assert "role='progressbar'" in html
    assert "aria-valuenow='97.5'" in html
    assert "Dataset catalog" in html
    assert "Healthy" in html
    assert "Stale" in html
    assert "Schema health" in html
    assert "varchar(255)" in html
    assert "Quality checks" in html
    assert "High" in html
    assert "pdu-badge-danger" in html
    assert "pdu-badge-warning" in html
    assert "freshness" in html
    assert "Latest partition is 6 hours old" in html
    assert "Add data" in html
    assert 'hx-post="/api/upload"' in html
    assert 'hx-encoding="multipart/form-data"' in html


def test_pipeline_operations_renders_steps_pipelines_activity_and_runs():
    html = pipeline_operations(
        metrics={"Success rate": "99.8%", "Rows processed": "42.1M"},
        pipeline={
            "name": "warehouse_daily",
            "description": "Loads product analytics into the warehouse.",
            "status": "running",
            "schedule": "Every day at 02:00 UTC",
            "owner": "data-platform",
            "steps": [
                {"name": "Extract Postgres", "status": "success"},
                {"name": "Transform with dbt", "status": "running"},
                {"name": "Publish marts", "status": "pending"},
            ],
        },
        pipelines=[
            {"Pipeline": "warehouse_daily", "Owner": "data-platform", "Status": "running"},
            {"Pipeline": "billing_sync", "Owner": "finance", "Status": "failed"},
        ],
        events=[
            {"time": "02:00", "label": "warehouse_daily started", "status": "running"},
            {"time": "01:45", "label": "billing_sync failed", "status": "failed", "description": "Timeout"},
        ],
        runs=[
            {"Run": "run_1042", "Duration": "8m 12s", "Status": "success"},
            {"Run": "run_1041", "Duration": "0m 41s", "Status": "failed"},
        ],
    ).render({})

    assert "Pipeline Operations" in html
    assert "Success rate" in html
    assert "warehouse_daily" in html
    assert "Every day at 02:00 UTC" in html
    assert "Extract Postgres" in html
    assert "Transform with dbt" in html
    assert "animate-pulse" in html
    assert "Pipelines" in html
    assert "billing_sync" in html
    assert "pdu-badge-info" in html
    assert "pdu-badge-danger" in html
    assert "Recent activity" in html
    assert "billing_sync failed" in html
    assert "Timeout" in html
    assert "Recent runs" in html
    assert "run_1042" in html


def test_model_registry_renders_selected_model_metrics_evaluation_and_models():
    html = model_registry(
        model={
            "name": "churn_classifier",
            "version": "v12",
            "stage": "production",
            "owner": "ml-platform",
            "updated": "2026-10-20",
            "metrics": {"AUC": 0.985, "F1": 0.942, "Accuracy": 0.951},
        },
        confusion_matrix={
            "matrix": [[100, 10], [5, 85]],
            "labels": ["Retained", "Churned"],
        },
        feature_importance={"tenure": 0.45, "support_calls": 0.35, "plan": 0.20},
        models=[
            {"Model": "churn_classifier", "Version": "v12", "Stage": "production"},
            {"Model": "ltv_regressor", "Version": "v3", "Stage": "staging"},
        ],
    ).render({})

    assert "Model Registry" in html
    assert "churn_classifier" in html
    assert "Version v12" in html
    assert "Production" in html
    assert "0.9850" in html
    assert "0.9420" in html
    assert "Retained" in html
    assert "Churned" in html
    assert "Feature importance" in html
    assert "tenure" in html
    assert "Registered models" in html
    assert "ltv_regressor" in html
    assert "Staging" in html


def test_data_template_aliases_are_available():
    assert quality_dashboard is data_quality_dashboard
    assert pipeline_dashboard is pipeline_operations
    assert ml_registry is model_registry

    from pydataui import templates

    assert templates.analyst_dashboard is analyst_dashboard


def test_data_templates_accept_state_refs():
    analyst_html = analyst_dashboard(
        metrics=TemplateState.metrics,
        table=TemplateState.rows,
    ).render({})
    quality_html = data_quality_dashboard(
        score=TemplateState.score,
        schema=TemplateState.schema,
        issues=TemplateState.issues,
    ).render({})
    pipeline_html = pipeline_operations(
        pipeline=TemplateState.pipeline,
        events=TemplateState.events,
    ).render({})
    model_html = model_registry(model=TemplateState.model).render({})

    assert "$48,250" in analyst_html
    assert "North" in analyst_html
    assert "99.0%" in quality_html
    assert "user_id" in quality_html
    assert "warehouse_daily" in pipeline_html
    assert "Extract" in pipeline_html
    assert "churn_classifier" in model_html
    assert "0.9850" in model_html


def test_data_templates_accept_pandas_dataframes():
    pd = pytest.importorskip("pandas")
    frame = pd.DataFrame(
        [
            {"Region": "North", "Revenue": 12400},
            {"Region": "South", "Revenue": 9850},
        ]
    )

    html = analyst_dashboard(
        metrics={"Rows": len(frame)},
        table=frame,
    ).render({})

    assert "North" in html
    assert "South" in html
    assert "2 rows" in html


def test_data_quality_dashboard_reports_no_open_issues_for_empty_list():
    html = data_quality_dashboard(issues=[]).render({})
    assert "No open quality issues." in html


def test_data_templates_escape_untrusted_text():
    payload = "<script>window.__pwned=1</script>"
    html = "\n".join(
        [
            analyst_dashboard(
                title=payload,
                metrics=[
                    {
                        "title": payload,
                        "value": payload,
                        "delta": payload,
                        "icon": payload,
                        "description": payload,
                    }
                ],
                filters=[Input(payload)],
                table=[{payload: payload}],
            ).render({}),
            data_quality_dashboard(
                issues=[
                    {
                        "Dataset": payload,
                        "Check": payload,
                        "Severity": payload,
                        "Status": payload,
                        "Detail": payload,
                    }
                ],
                schema={payload: payload},
            ).render({}),
            pipeline_operations(
                pipeline={
                    "name": payload,
                    "description": payload,
                    "status": payload,
                    "steps": [{"name": payload, "message": payload, "status": payload}],
                },
                events=[{"time": payload, "label": payload, "description": payload}],
                runs=[{"Run": payload, "Status": payload}],
            ).render({}),
            model_registry(
                model={
                    "name": payload,
                    "version": payload,
                    "stage": payload,
                    "owner": payload,
                    "updated": payload,
                    "metrics": {payload: 0.5},
                },
                confusion_matrix={"matrix": [[1, 0], [0, 1]], "labels": [payload, payload]},
                feature_importance={payload: 1.0},
                models=[{"Model": payload, "Stage": payload}],
            ).render({}),
        ]
    )

    assert "<script>" not in html
    assert "window.__pwned" not in html or "&lt;script&gt;" in html
    assert html.count("&lt;script&gt;window.__pwned=1&lt;/script&gt;") >= 1


def test_data_templates_render_empty_states():
    assert "Add metrics" in analyst_dashboard().render({})
    assert "Configure quality" in data_quality_dashboard().render({})
    assert "Add metrics" in pipeline_operations().render({})
    assert "Register a model" in model_registry().render({})
