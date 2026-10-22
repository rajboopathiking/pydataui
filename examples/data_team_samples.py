from pydataui.components import BarChart, DataUpload, FileDownload
from pydataui.templates import (
    analyst_dashboard,
    data_quality_dashboard,
    model_registry,
    pipeline_operations,
)


def analyst_page():
    return analyst_dashboard(
        title="Revenue Analysis",
        subtitle="Daily revenue, order volume, and regional performance.",
        metrics={
            "Net revenue": "$48,250",
            "Orders": "1,284",
            "Conversion": "4.8%",
        },
        chart=BarChart(
            labels=["Mon", "Tue", "Wed", "Thu", "Fri"],
            data=[7400, 8100, 9250, 11200, 12300],
            label="Revenue",
        ),
        table=[
            {"Region": "North", "Revenue": "$12,400", "Orders": 312},
            {"Region": "South", "Revenue": "$9,850", "Orders": 241},
            {"Region": "West", "Revenue": "$15,200", "Orders": 401},
        ],
        export=FileDownload(
            filename="revenue.csv",
            content="region,revenue,orders\nNorth,12400,312\nSouth,9850,241\n",
            label="Export CSV",
            mime_type="text/csv",
        ),
    )


def quality_page():
    return data_quality_dashboard(
        title="Data Quality & Catalog",
        score=97.5,
        metrics={
            "Tables monitored": 142,
            "Open checks": 3,
            "Freshness SLA": "99.2%",
        },
        datasets=[
            {"Dataset": "orders", "Owner": "finance", "Rows": "4.2M", "Status": "Healthy"},
            {"Dataset": "events", "Owner": "growth", "Rows": "18.7M", "Status": "Stale"},
            {"Dataset": "customers", "Owner": "crm", "Rows": "820K", "Status": "Healthy"},
        ],
        schema={
            "user_id": "int64",
            "email": "varchar(255)",
            "created_at": "timestamp",
        },
        issues=[
            {
                "Dataset": "events",
                "Check": "freshness",
                "Severity": "high",
                "Status": "open",
                "Detail": "Latest partition is 6 hours old",
            },
            {
                "Dataset": "orders",
                "Check": "duplicate_rows",
                "Severity": "medium",
                "Status": "resolved",
                "Detail": "0.02% duplicates in the last run",
            },
        ],
        upload=DataUpload(accept=".csv,.json,.parquet", on_upload="/api/upload"),
    )


def pipelines_page():
    return pipeline_operations(
        title="Pipeline Operations",
        metrics={
            "Success rate": "99.8%",
            "Rows processed": "42.1M",
            "P95 runtime": "8m 12s",
        },
        pipeline={
            "name": "warehouse_daily",
            "description": "Loads product analytics into the warehouse.",
            "status": "running",
            "schedule": "Every day at 02:00 UTC",
            "owner": "data-platform",
            "steps": [
                {"name": "Extract Postgres", "status": "success", "message": "2.4M rows"},
                {"name": "Transform with dbt", "status": "running", "message": "18 of 26 models"},
                {"name": "Publish marts", "status": "pending"},
            ],
        },
        pipelines=[
            {"Pipeline": "warehouse_daily", "Owner": "data-platform", "Status": "running"},
            {"Pipeline": "billing_sync", "Owner": "finance", "Status": "failed"},
            {"Pipeline": "events_stream", "Owner": "growth", "Status": "healthy"},
        ],
        events=[
            {"time": "02:00", "label": "warehouse_daily started", "status": "running"},
            {
                "time": "01:45",
                "label": "billing_sync failed",
                "status": "failed",
                "description": "Timeout after 30 minutes",
            },
            {"time": "01:30", "label": "events_stream checkpoint", "status": "success"},
        ],
        runs=[
            {"Run": "run_1042", "Started": "02:00", "Duration": "8m 12s", "Status": "success"},
            {"Run": "run_1041", "Started": "01:45", "Duration": "0m 41s", "Status": "failed"},
        ],
    )


def models_page():
    return model_registry(
        title="Model Registry",
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
        feature_importance={
            "tenure": 0.45,
            "support_calls": 0.35,
            "plan": 0.20,
        },
        models=[
            {
                "Model": "churn_classifier",
                "Version": "v12",
                "Stage": "production",
                "Owner": "ml-platform",
            },
            {"Model": "ltv_regressor", "Version": "v3", "Stage": "staging", "Owner": "growth"},
            {"Model": "fraud_scorer", "Version": "v7", "Stage": "canary", "Owner": "risk"},
        ],
    )


SAMPLES = [
    {
        "id": "analyst",
        "title": "Analyst dashboard",
        "role": "Data analyst",
        "description": "KPIs, a trend chart, filters, regional records, and a CSV export.",
        "builder": analyst_page,
    },
    {
        "id": "quality",
        "title": "Data quality & catalog",
        "role": "Analytics engineer",
        "description": "Quality score, dataset status, schema health, issues, and upload.",
        "builder": quality_page,
    },
    {
        "id": "pipelines",
        "title": "Pipeline operations",
        "role": "Data engineer",
        "description": "Step tracker, pipeline inventory, activity timeline, and run history.",
        "builder": pipelines_page,
    },
    {
        "id": "models",
        "title": "ML model registry",
        "role": "ML engineer",
        "description": "Selected model metrics, confusion matrix, feature importance, and registry.",
        "builder": models_page,
    },
]
