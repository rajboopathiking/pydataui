# Data Team Page Templates

PyDataUI ships four low-code page templates for common data-team workflows. Each
template returns a normal `Container` component, so it works with server-rendered
pages, state-driven actions, mounting, and authentication exactly like any other
component tree.

**Visual examples:** [Open the generated template gallery](TEMPLATE_GALLERY.md)
to see all four pages rendered in a standalone HTML page.

```python
from pydataui import App
from pydataui.templates import analyst_dashboard

app = App(title="Analytics")

@app.page("/")
def home():
    return analyst_dashboard(
        metrics={"Revenue": "$48,250", "Orders": "1,284"},
    )
```

Templates are available from both `pydataui.templates` and the root package:

```python
from pydataui import templates
from pydataui.templates import (
    analyst_dashboard,
    data_quality_dashboard,
    pipeline_operations,
    model_registry,
)
```

## Choosing a template

| Role | Template | Typical content |
| --- | --- | --- |
| Data analyst | `analyst_dashboard` | KPIs, trend chart, filters, records, CSV export |
| Analytics engineer | `data_quality_dashboard` | Quality score, dataset catalog, schema checks, uploads |
| Data engineer | `pipeline_operations` | Pipeline steps, inventory, activity timeline, run history |
| ML engineer | `model_registry` | Model metrics, confusion matrix, feature importance, versions |

## Shared behavior

- `metrics` accepts a mapping of label to value, or a list of dictionaries with
  `title`, `value`, `delta`, `delta_type`, `icon`, and `description` keys.
- Tables accept a list of row dictionaries/lists, a component such as `Table`,
  or a pandas `DataFrame` (rendered through `DataFrameTable`).
- Status-like columns (`status`, `state`, `health`, `severity`, `stage`) are
  rendered as colored badges.
- Strings from application data are escaped by the underlying components.
- Every template accepts `actions=[...]` for header buttons or links.
- Aliases are available: `quality_dashboard`, `pipeline_dashboard`, and
  `ml_registry`.

## Analyst dashboard

`analyst_dashboard(*, title, subtitle, metrics, filters, chart, chart_title, table, table_columns, table_title, export, actions)`

Combines KPI cards, filter controls, a chart, a data table, and an optional
`FileDownload` export.

```python
from pydataui.components import BarChart, FileDownload, Input
from pydataui.templates import analyst_dashboard

return analyst_dashboard(
    title="Revenue Analysis",
    metrics={"Revenue": "$48,250", "Orders": "1,284", "Conversion": "4.8%"},
    filters=[Input("Region", placeholder="All regions")],
    chart=BarChart(labels=["Mon", "Tue"], data=[7400, 8100], label="Revenue"),
    table=[
        {"Region": "North", "Revenue": "$12,400"},
        {"Region": "South", "Revenue": "$9,850"},
    ],
    export=FileDownload(
        filename="revenue.csv",
        content="region,revenue\nNorth,12400\n",
        label="Export CSV",
        mime_type="text/csv",
    ),
)
```

## Data quality and catalog

`data_quality_dashboard(*, title, subtitle, metrics, score, score_label, datasets, dataset_columns, schema, issues, issue_columns, upload, actions)`

Shows an overall quality score, catalog health, schema details, open checks, and
an optional upload target.

```python
from pydataui.components import DataUpload
from pydataui.templates import data_quality_dashboard

return data_quality_dashboard(
    score=97.5,
    metrics={"Tables monitored": 142, "Open checks": 3},
    datasets=[
        {"Dataset": "orders", "Owner": "finance", "Status": "Healthy"},
        {"Dataset": "events", "Owner": "growth", "Status": "Stale"},
    ],
    schema={"user_id": "int64", "email": "varchar(255)"},
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
)
```

## Pipeline operations

`pipeline_operations(*, title, subtitle, metrics, pipeline, steps, pipelines, pipeline_columns, events, runs, run_columns, actions)`

Combines pipeline run metrics, a step tracker, a pipeline inventory, an activity
timeline, and recent run history.

```python
from pydataui.templates import pipeline_operations

return pipeline_operations(
    metrics={"Success rate": "99.8%", "Rows processed": "42.1M"},
    pipeline={
        "name": "warehouse_daily",
        "status": "running",
        "schedule": "Every day at 02:00 UTC",
        "steps": [
            {"name": "Extract Postgres", "status": "success"},
            {"name": "Transform with dbt", "status": "running"},
            {"name": "Publish marts", "status": "pending"},
        ],
    },
    pipelines=[
        {"Pipeline": "billing_sync", "Owner": "finance", "Status": "failed"},
    ],
    events=[
        {"time": "02:00", "label": "warehouse_daily started", "status": "running"},
    ],
    runs=[
        {"Run": "run_1042", "Duration": "8m 12s", "Status": "success"},
    ],
)
```

## ML model registry

`model_registry(*, title, subtitle, model, models, model_columns, metrics, confusion_matrix, feature_importance, feature_title, actions)`

Highlights a selected model with evaluation metrics, a confusion matrix, feature
importance, and a registry of model versions.

```python
from pydataui.templates import model_registry

return model_registry(
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
)
```

## More role-based recipes

### Analysts: pandas, Plotly, and an export

Templates accept a pandas `DataFrame` directly for the table and any component
for chart slots. `PlotlyChart` is used here when Plotly is installed.

```python
import pandas as pd
import plotly.express as px

from pydataui import App
from pydataui.components import FileDownload
from pydataui.components.data_science import PlotlyChart
from pydataui.templates import analyst_dashboard

app = App(title="Monthly Revenue")

@app.page("/")
def revenue():
    frame = pd.DataFrame(
        [
            {"month": "Jul", "region": "North", "revenue": 12400},
            {"month": "Aug", "region": "North", "revenue": 13800},
            {"month": "Sep", "region": "North", "revenue": 15100},
        ]
    )

    return analyst_dashboard(
        metrics={
            "Rows": len(frame),
            "Revenue": f"${frame['revenue'].sum():,.0f}",
        },
        chart=PlotlyChart(px.bar(frame, x="month", y="revenue")),
        table=frame,
        export=FileDownload(
            filename="revenue.csv",
            content=frame.to_csv(index=False),
            label="Download data",
            mime_type="text/csv",
        ),
    )
```

### Data engineers: refresh a pipeline from state

Templates resolve `State` references each render, so action handlers can update
the displayed runs and metrics without bespoke frontend code.

```python
from pydataui import App, State
from pydataui.components import Button
from pydataui.templates import pipeline_operations

class PipelineState(State):
    runs = [
        {"Run": "run_1042", "Duration": "8m 12s", "Status": "success"},
        {"Run": "run_1041", "Duration": "0m 41s", "Status": "failed"},
    ]

    def trigger(self):
        next_run = f"run_{len(self.runs) + 1041}"
        self.runs = [
            {"Run": next_run, "Duration": "running", "Status": "running"},
            *self.runs[:2],
        ]

app = App(title="Pipeline Console")

@app.page("/")
def pipelines():
    return pipeline_operations(
        metrics={"Tracked runs": len(PipelineState.runs)},
        pipeline={
            "name": "warehouse_daily",
            "status": "running",
            "steps": [
                {"name": "Extract Postgres", "status": "success"},
                {"name": "Transform with dbt", "status": "running"},
            ],
        },
        runs=PipelineState.runs,
        actions=[
            Button("Trigger run", on_click=PipelineState.trigger),
        ],
    )
```

### Analytics engineers: receive an uploaded file

`DataUpload` accepts either a URL or a `State` method. The template handles the
layout; your handler validates and stores the file.

```python
from pydataui import App, State
from pydataui.components import DataUpload
from pydataui.templates import data_quality_dashboard

class QualityState(State):
    last_file: str = ""
    last_size: int = 0

    def handle_file(self, file=None):
        self.last_file = getattr(file, "filename", "")
        self.last_size = getattr(file, "size", 0)

app = App(title="Quality Console")

@app.page("/")
def quality():
    return data_quality_dashboard(
        score=97.5,
        metrics={"Last file size": f"{int(QualityState.last_size):,} bytes"},
        datasets=[
            {"Dataset": "orders", "Owner": "finance", "Status": "Healthy"},
        ],
        issues=[],
        upload=DataUpload(
            accept=".csv,.json,.parquet",
            on_upload=QualityState.handle_file,
        ),
    )
```

### ML engineers: compose custom evaluation widgets

Evaluation slots accept either structured dictionaries or your own PyDataUI
components. This is useful when a metric needs a custom chart or annotation.

```python
from pydataui.components.data_science import (
    ConfusionMatrix,
    FeatureImportance,
    PlotlyChart,
)
from pydataui.templates import model_registry

return model_registry(
    model={
        "name": "churn_classifier",
        "version": "v12",
        "stage": "production",
        "metrics": {"AUC": 0.985, "F1": 0.942},
    },
    confusion_matrix=ConfusionMatrix(
        matrix=[[100, 10], [5, 85]],
        labels=["Retained", "Churned"],
    ),
    feature_importance=FeatureImportance(
        features={"tenure": 0.45, "support_calls": 0.35},
        title="Drivers of churn",
    ),
    models=[
        {"Model": "churn_classifier", "Version": "v12", "Stage": "production"},
    ],
)
```

### Protect a template with a role

Templates are page content, so the normal authentication decorators apply:

```python
from pydataui.auth import require_role, Role

@app.page("/models")
@require_role(Role.ML_ENGINEER)
def models():
    return model_registry(...)
```

## Visual gallery

The repository includes a standalone, responsive HTML gallery that renders all
four templates with sample data:

- File: `docs/examples/data-team-gallery.html`
- Sample data: `examples/data_team_samples.py`
- Live app: `python examples/data_team_templates.py`
- Regenerate the gallery: `python examples/generate_data_team_gallery.py`

The gallery uses the Tailwind and Chart.js CDNs so it can be opened directly in a
browser. Regeneration is deterministic, which keeps documentation diffs clean.

## Adding actions

All templates accept components in `actions`. They can be plain links or
state-bound buttons, so the templates remain low-code while supporting real
interactions:

```python
from pydataui import State
from pydataui.components import Button

class PipelineState(State):
    def trigger(self):
        ...

return pipeline_operations(
    actions=[Button("Run pipeline", on_click=PipelineState.trigger)],
    ...
)
```

See `examples/data_team_templates.py` for a complete four-page application.
