# Data Science & Engineering Components Guide

PyDataUI provides first-class native components built specifically for data professionals. Rather than wiring together complex frontend widgets, you can pass Python data structures, pandas DataFrames, and Plotly charts directly to PyDataUI components.

For complete page layouts, see [Data Team Page Templates](DATA_TEMPLATES.md), which compose these components into analyst, data-quality, pipeline-operations, and ML-registry pages.

---

## Table of Contents

- [For Data Analysts](#for-data-analysts)
  - [DataFrameTable](#dataframetable)
  - [PlotlyChart](#plotlychart)
  - [MetricCard](#metriccard)
- [For AI & ML Engineers](#for-ai-ml-engineers)
  - [ModelMetrics](#modelmetrics)
  - [ConfusionMatrix](#confusionmatrix)
  - [FeatureImportance](#featureimportance)
- [For Data Engineers](#for-data-engineers)
  - [PipelineStatus](#pipelinestatus)
  - [DataTimeline](#datatimeline)
  - [SchemaViewer](#schemaviewer)
  - [SQLEditor](#sqleditor)
  - [FileDownload & DataUpload](#filedownload-dataupload)
  - [JSONViewer & CodeBlock](#jsonviewer-codeblock)

---

## For Data Analysts

### `DataFrameTable`
Renders a pandas DataFrame as a scrollable, styled table with shadcn design patterns.

```python
from pydataui.components.data_science import DataFrameTable
import pandas as pd

df = pd.read_csv("sales_data.csv")

# Render top 50 rows
DataFrameTable(df=df, max_rows=50)
```

**Props:**
- `df`: `pandas.DataFrame` instance.
- `max_rows`: Maximum rows to render (default: 100).

<div style="margin: 1rem 0 2rem 0; padding: 1.5rem; background: #09090b; border: 1px solid #27272a; border-radius: 0.75rem;">
  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
    <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: #71717a; font-weight: 700;">Rendered UI Preview</div>
    <span style="font-size: 0.75rem; color: #a1a1aa; background: #18181b; padding: 0.2rem 0.5rem; border-radius: 0.25rem; border: 1px solid #27272a;">4 of 12,450 rows</span>
  </div>
  <div style="overflow-x: auto; border: 1px solid #27272a; border-radius: 0.5rem; background: #18181b;">
    <table style="width: 100%; border-collapse: collapse; font-size: 0.875rem; text-align: left;">
      <thead>
        <tr style="border-bottom: 1px solid #27272a; background: #121215; color: #a1a1aa;">
          <th style="padding: 0.75rem 1rem; font-weight: 600;">order_id</th>
          <th style="padding: 0.75rem 1rem; font-weight: 600;">customer</th>
          <th style="padding: 0.75rem 1rem; font-weight: 600;">region</th>
          <th style="padding: 0.75rem 1rem; font-weight: 600; text-align: right;">amount</th>
          <th style="padding: 0.75rem 1rem; font-weight: 600; text-align: center;">status</th>
        </tr>
      </thead>
      <tbody style="color: #fafafa;">
        <tr style="border-bottom: 1px solid #27272a;">
          <td style="padding: 0.75rem 1rem; font-family: monospace; color: #818cf8;">#ORD-9021</td>
          <td style="padding: 0.75rem 1rem; font-weight: 500;">Acme Corp</td>
          <td style="padding: 0.75rem 1rem; color: #a1a1aa;">North America</td>
          <td style="padding: 0.75rem 1rem; text-align: right; font-weight: 600;">$14,250.00</td>
          <td style="padding: 0.75rem 1rem; text-align: center;"><span style="background: rgba(34, 197, 94, 0.15); color: #4ade80; padding: 0.15rem 0.5rem; border-radius: 9999px; font-size: 0.75rem; border: 1px solid rgba(34, 197, 94, 0.3);">Completed</span></td>
        </tr>
        <tr style="border-bottom: 1px solid #27272a; background: rgba(255, 255, 255, 0.02);">
          <td style="padding: 0.75rem 1rem; font-family: monospace; color: #818cf8;">#ORD-9022</td>
          <td style="padding: 0.75rem 1rem; font-weight: 500;">Starlight Media</td>
          <td style="padding: 0.75rem 1rem; color: #a1a1aa;">Europe West</td>
          <td style="padding: 0.75rem 1rem; text-align: right; font-weight: 600;">$8,920.50</td>
          <td style="padding: 0.75rem 1rem; text-align: center;"><span style="background: rgba(34, 197, 94, 0.15); color: #4ade80; padding: 0.15rem 0.5rem; border-radius: 9999px; font-size: 0.75rem; border: 1px solid rgba(34, 197, 94, 0.3);">Completed</span></td>
        </tr>
        <tr style="border-bottom: 1px solid #27272a;">
          <td style="padding: 0.75rem 1rem; font-family: monospace; color: #818cf8;">#ORD-9023</td>
          <td style="padding: 0.75rem 1rem; font-weight: 500;">BioGen Health</td>
          <td style="padding: 0.75rem 1rem; color: #a1a1aa;">Asia Pacific</td>
          <td style="padding: 0.75rem 1rem; text-align: right; font-weight: 600;">$31,400.00</td>
          <td style="padding: 0.75rem 1rem; text-align: center;"><span style="background: rgba(59, 130, 246, 0.15); color: #60a5fa; padding: 0.15rem 0.5rem; border-radius: 9999px; font-size: 0.75rem; border: 1px solid rgba(59, 130, 246, 0.3);">Processing</span></td>
        </tr>
        <tr>
          <td style="padding: 0.75rem 1rem; font-family: monospace; color: #818cf8;">#ORD-9024</td>
          <td style="padding: 0.75rem 1rem; font-weight: 500;">Apex Logistics</td>
          <td style="padding: 0.75rem 1rem; color: #a1a1aa;">North America</td>
          <td style="padding: 0.75rem 1rem; text-align: right; font-weight: 600;">$4,110.00</td>
          <td style="padding: 0.75rem 1rem; text-align: center;"><span style="background: rgba(34, 197, 94, 0.15); color: #4ade80; padding: 0.15rem 0.5rem; border-radius: 9999px; font-size: 0.75rem; border: 1px solid rgba(34, 197, 94, 0.3);">Completed</span></td>
        </tr>
      </tbody>
    </table>
  </div>
</div>

---

### `DataTable` (Universal Sniffing & In-Browser Interactivity)

Renders any dataset with automatic schema inference, instant client-side search filtering, interactive column sorting, and pagination.

```python
from pydataui import DataTable

# Pass Polars, Pandas, DuckDB, Arrow, Pydantic, or Dicts directly:
DataTable(
    data=df,              # Any DataFrame, Relation, Arrow Table, or list of objects
    searchable=True,      # In-browser instant text filter
    sortable=True,        # Clickable column sorting (numeric & alphabetic)
    paginated=True,       # Client-side pagination
    page_size=10
)
```

**Supported Inputs:**
- **Polars DataFrames & LazyFrames** (`df.to_dicts()`)
- **Pandas DataFrames & Series** (`df.to_dict('records')`)
- **DuckDB PyRelations** (`conn.sql(...)`)
- **PyArrow Tables & RecordBatches** (`table.to_pylist()`)
- **Pydantic Models & Dataclasses** (`[Item(...) for ...]`)
- **Columnar Dicts** (`{"col": [1, 2]}`)


---

### `PlotlyChart`
Embeds interactive Plotly charts with auto-resizing and responsive layouts.

```python
from pydataui.components.data_science import PlotlyChart
import plotly.express as px

fig = px.bar(
    df, x="quarter", y="revenue", color="region",
    title="Quarterly Regional Revenue",
    barmode="group"
)

PlotlyChart(figure=fig, height=450)
```

**Props:**
- `figure`: Plotly `Figure` instance.
- `height`: Pixel height of the rendered chart (default: 400).

---

### `MetricCard`
Displays key business performance indicators (KPIs) with value formatting, delta indicators, and icons.

```python
from pydataui.components.data_science import MetricCard

MetricCard(
    title="Monthly Active Users",
    value=284500,
    format=",.0f",             # Formats as "284,500"
    delta="+12.4% vs last mo",
    delta_type="increase",      # 'increase' (green) | 'decrease' (red) | 'neutral'
    icon="👥",
    description="Calculated based on unique 30-day token events"
)
```

<div style="margin: 1rem 0 2rem 0; padding: 1.5rem; background: #09090b; border: 1px solid #27272a; border-radius: 0.75rem;">
  <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: #71717a; margin-bottom: 1rem; font-weight: 700;">Rendered UI Preview</div>
  <div style="max-width: 22rem; background: #18181b; border: 1px solid #27272a; border-radius: 0.75rem; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <span style="font-size: 0.875rem; font-weight: 500; color: #a1a1aa;">Monthly Active Users</span>
      <span style="font-size: 1.25rem;">👥</span>
    </div>
    <div style="margin-top: 0.5rem; display: flex; align-items: baseline; gap: 0.75rem;">
      <span style="font-size: 2rem; font-weight: 800; color: #fafafa; letter-spacing: -0.025em;">284,500</span>
      <span style="display: inline-flex; align-items: center; font-size: 0.75rem; font-weight: 600; color: #4ade80; background: rgba(34, 197, 94, 0.15); padding: 0.125rem 0.5rem; border-radius: 0.25rem; border: 1px solid rgba(34, 197, 94, 0.3);">
        +12.4% vs last mo
      </span>
    </div>
    <p style="margin: 0.75rem 0 0 0; font-size: 0.75rem; color: #71717a;">Calculated based on unique 30-day token events</p>
  </div>
</div>

---

## For AI & ML Engineers

### `ModelMetrics`
Grid of cards summarizing model evaluation metrics.

```python
from pydataui.components.data_science import ModelMetrics

ModelMetrics(
    metrics={
        "Accuracy": 0.9542,
        "Precision": 0.9410,
        "Recall": 0.9680,
        "ROC-AUC": 0.9892
    }
)
```

<div style="margin: 1rem 0 2rem 0; padding: 1.5rem; background: #09090b; border: 1px solid #27272a; border-radius: 0.75rem;">
  <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: #71717a; margin-bottom: 1rem; font-weight: 700;">Rendered UI Preview</div>
  <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 0.75rem;">
    <div style="background: #18181b; border: 1px solid #27272a; border-radius: 0.5rem; padding: 1rem;">
      <div style="font-size: 0.75rem; color: #a1a1aa; font-weight: 500;">Accuracy</div>
      <div style="font-size: 1.5rem; font-weight: 700; color: #fafafa; margin-top: 0.25rem;">95.42%</div>
      <div style="font-size: 0.7rem; color: #4ade80; margin-top: 0.25rem;">+1.2% benchmark</div>
    </div>
    <div style="background: #18181b; border: 1px solid #27272a; border-radius: 0.5rem; padding: 1rem;">
      <div style="font-size: 0.75rem; color: #a1a1aa; font-weight: 500;">Precision</div>
      <div style="font-size: 1.5rem; font-weight: 700; color: #fafafa; margin-top: 0.25rem;">94.10%</div>
      <div style="font-size: 0.7rem; color: #4ade80; margin-top: 0.25rem;">High Confidence</div>
    </div>
    <div style="background: #18181b; border: 1px solid #27272a; border-radius: 0.5rem; padding: 1rem;">
      <div style="font-size: 0.75rem; color: #a1a1aa; font-weight: 500;">Recall</div>
      <div style="font-size: 1.5rem; font-weight: 700; color: #fafafa; margin-top: 0.25rem;">96.80%</div>
      <div style="font-size: 0.7rem; color: #4ade80; margin-top: 0.25rem;">Minimal FNs</div>
    </div>
    <div style="background: #18181b; border: 1px solid #27272a; border-radius: 0.5rem; padding: 1rem;">
      <div style="font-size: 0.75rem; color: #a1a1aa; font-weight: 500;">ROC-AUC</div>
      <div style="font-size: 1.5rem; font-weight: 700; color: #818cf8; margin-top: 0.25rem;">0.9892</div>
      <div style="font-size: 0.7rem; color: #a1a1aa; margin-top: 0.25rem;">Near-Optimal</div>
    </div>
  </div>
</div>

---

### `ConfusionMatrix`
Heat-mapped visual table representing model prediction accuracy across target classes.

```python
from pydataui.components.data_science import ConfusionMatrix

ConfusionMatrix(
    matrix=[
        [1450, 42],    # [True Negative, False Positive]
        [28, 1380]     # [False Negative, True Positive]
    ],
    labels=["Legitimate", "Fraud"]
)
```

<div style="margin: 1rem 0 2rem 0; padding: 1.5rem; background: #09090b; border: 1px solid #27272a; border-radius: 0.75rem;">
  <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: #71717a; margin-bottom: 1rem; font-weight: 700;">Rendered UI Preview</div>
  <div style="max-width: 24rem; border: 1px solid #27272a; border-radius: 0.5rem; background: #18181b; overflow: hidden;">
    <div style="padding: 0.75rem 1rem; background: #121215; border-bottom: 1px solid #27272a; font-size: 0.8rem; font-weight: 600; color: #a1a1aa;">
      Confusion Matrix (Actual vs Predicted)
    </div>
    <div style="display: grid; grid-template-columns: 80px 1fr 1fr; text-align: center; font-size: 0.8rem;">
      <div style="padding: 0.5rem; color: #71717a;"></div>
      <div style="padding: 0.5rem; font-weight: 600; color: #a1a1aa; border-bottom: 1px solid #27272a;">Pred: Legitimate</div>
      <div style="padding: 0.5rem; font-weight: 600; color: #a1a1aa; border-bottom: 1px solid #27272a;">Pred: Fraud</div>

      <div style="padding: 1rem 0.5rem; font-weight: 600; color: #a1a1aa; border-right: 1px solid #27272a; display: flex; align-items: center; justify-content: center;">Act: Legitimate</div>
      <div style="padding: 1rem; background: rgba(34, 197, 94, 0.2); border-right: 1px solid #27272a; border-bottom: 1px solid #27272a;">
        <div style="font-size: 1.25rem; font-weight: 700; color: #4ade80;">1,450</div>
        <div style="font-size: 0.7rem; color: #86efac;">TN (97.2%)</div>
      </div>
      <div style="padding: 1rem; background: rgba(239, 68, 68, 0.1); border-bottom: 1px solid #27272a;">
        <div style="font-size: 1.25rem; font-weight: 700; color: #f87171;">42</div>
        <div style="font-size: 0.7rem; color: #fca5a5;">FP (2.8%)</div>
      </div>

      <div style="padding: 1rem 0.5rem; font-weight: 600; color: #a1a1aa; border-right: 1px solid #27272a; display: flex; align-items: center; justify-content: center;">Act: Fraud</div>
      <div style="padding: 1rem; background: rgba(239, 68, 68, 0.1); border-right: 1px solid #27272a;">
        <div style="font-size: 1.25rem; font-weight: 700; color: #f87171;">28</div>
        <div style="font-size: 0.7rem; color: #fca5a5;">FN (2.0%)</div>
      </div>
      <div style="padding: 1rem; background: rgba(34, 197, 94, 0.25);">
        <div style="font-size: 1.25rem; font-weight: 700; color: #4ade80;">1,380</div>
        <div style="font-size: 0.7rem; color: #86efac;">TP (98.0%)</div>
      </div>
    </div>
  </div>
</div>

---

### `FeatureImportance`
Horizontal relative-importance bar chart for model explainability (e.g. SHAP values, Random Forest Gini importance).

```python
from pydataui.components.data_science import FeatureImportance

FeatureImportance(
    features={
        "transaction_amount_ratio": 0.385,
        "login_ip_entropy": 0.241,
        "card_age_days": 0.182,
        "failed_attempts_last_hour": 0.125,
        "is_foreign_country": 0.067
    },
    title="XGBoost Feature Importance"
)
```

<div style="margin: 1rem 0 2rem 0; padding: 1.5rem; background: #09090b; border: 1px solid #27272a; border-radius: 0.75rem;">
  <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: #71717a; margin-bottom: 1rem; font-weight: 700;">Rendered UI Preview</div>
  <div style="max-width: 26rem; background: #18181b; border: 1px solid #27272a; border-radius: 0.5rem; padding: 1.25rem;">
    <div style="font-size: 0.875rem; font-weight: 600; color: #fafafa; margin-bottom: 1rem;">XGBoost Feature Importance</div>
    <div style="display: flex; flex-direction: column; gap: 0.75rem;">
      <div>
        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #e4e4e7; margin-bottom: 0.25rem;">
          <span style="font-family: monospace;">transaction_amount_ratio</span>
          <span style="font-weight: 600; color: #818cf8;">38.5%</span>
        </div>
        <div style="width: 100%; height: 0.5rem; background: #27272a; border-radius: 9999px; overflow: hidden;">
          <div style="width: 38.5%; height: 100%; background: linear-gradient(90deg, #6366f1, #818cf8); border-radius: 9999px;"></div>
        </div>
      </div>
      <div>
        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #e4e4e7; margin-bottom: 0.25rem;">
          <span style="font-family: monospace;">login_ip_entropy</span>
          <span style="font-weight: 600; color: #818cf8;">24.1%</span>
        </div>
        <div style="width: 100%; height: 0.5rem; background: #27272a; border-radius: 9999px; overflow: hidden;">
          <div style="width: 24.1%; height: 100%; background: linear-gradient(90deg, #6366f1, #818cf8); border-radius: 9999px;"></div>
        </div>
      </div>
      <div>
        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #e4e4e7; margin-bottom: 0.25rem;">
          <span style="font-family: monospace;">card_age_days</span>
          <span style="font-weight: 600; color: #818cf8;">18.2%</span>
        </div>
        <div style="width: 100%; height: 0.5rem; background: #27272a; border-radius: 9999px; overflow: hidden;">
          <div style="width: 18.2%; height: 100%; background: linear-gradient(90deg, #6366f1, #818cf8); border-radius: 9999px;"></div>
        </div>
      </div>
      <div>
        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #e4e4e7; margin-bottom: 0.25rem;">
          <span style="font-family: monospace;">failed_attempts_last_hour</span>
          <span style="font-weight: 600; color: #818cf8;">12.5%</span>
        </div>
        <div style="width: 100%; height: 0.5rem; background: #27272a; border-radius: 9999px; overflow: hidden;">
          <div style="width: 12.5%; height: 100%; background: linear-gradient(90deg, #6366f1, #818cf8); border-radius: 9999px;"></div>
        </div>
      </div>
      <div>
        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #e4e4e7; margin-bottom: 0.25rem;">
          <span style="font-family: monospace;">is_foreign_country</span>
          <span style="font-weight: 600; color: #818cf8;">6.7%</span>
        </div>
        <div style="width: 100%; height: 0.5rem; background: #27272a; border-radius: 9999px; overflow: hidden;">
          <div style="width: 6.7%; height: 100%; background: linear-gradient(90deg, #6366f1, #818cf8); border-radius: 9999px;"></div>
        </div>
      </div>
    </div>
  </div>
</div>

---

## For Data Engineers

### `PipelineStatus`
Real-time step tracker for ETL/ELT pipelines, Spark jobs, and DAGs.

```python
from pydataui.components.data_science import PipelineStatus

PipelineStatus(
    steps=[
        {"name": "1. Extract from S3 Buckets", "status": "success", "message": "2.4GB in 12s"},
        {"name": "2. Data Cleansing & Validation", "status": "success", "message": "0 schema violations"},
        {"name": "3. PySpark Aggregations", "status": "running", "message": "Stage 4 of 8 active"},
        {"name": "4. Load to ClickHouse Data Mart", "status": "pending", "message": "Awaiting stage 3"},
        {"name": "5. Refresh Metabase Dashboards", "status": "pending", "message": "Awaiting stage 4"},
    ]
)
```
Status types: `'success'` (green), `'running'` (animated blue pulse), `'pending'` (gray), `'failed'` (red), `'skipped'` (yellow).

<div style="margin: 1rem 0 2rem 0; padding: 1.5rem; background: #09090b; border: 1px solid #27272a; border-radius: 0.75rem;">
  <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: #71717a; margin-bottom: 1rem; font-weight: 700;">Rendered UI Preview</div>
  <div style="max-width: 28rem; background: #18181b; border: 1px solid #27272a; border-radius: 0.5rem; padding: 1.25rem;">
    <div style="display: flex; flex-direction: column; gap: 1rem;">
      <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
        <span style="display: flex; align-items: center; justify-content: center; width: 1.5rem; height: 1.5rem; border-radius: 9999px; background: rgba(34, 197, 94, 0.2); color: #4ade80; font-size: 0.75rem; font-weight: bold;">✓</span>
        <div style="flex: 1;">
          <div style="font-size: 0.875rem; font-weight: 600; color: #fafafa;">1. Extract from S3 Buckets</div>
          <div style="font-size: 0.75rem; color: #4ade80;">2.4GB in 12s</div>
        </div>
        <span style="font-size: 0.75rem; color: #a1a1aa; font-family: monospace;">08:00:12</span>
      </div>
      <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
        <span style="display: flex; align-items: center; justify-content: center; width: 1.5rem; height: 1.5rem; border-radius: 9999px; background: rgba(34, 197, 94, 0.2); color: #4ade80; font-size: 0.75rem; font-weight: bold;">✓</span>
        <div style="flex: 1;">
          <div style="font-size: 0.875rem; font-weight: 600; color: #fafafa;">2. Data Cleansing & Validation</div>
          <div style="font-size: 0.75rem; color: #4ade80;">0 schema violations</div>
        </div>
        <span style="font-size: 0.75rem; color: #a1a1aa; font-family: monospace;">08:01:45</span>
      </div>
      <div style="display: flex; align-items: flex-start; gap: 0.75rem;">
        <span style="display: flex; align-items: center; justify-content: center; width: 1.5rem; height: 1.5rem; border-radius: 9999px; background: rgba(59, 130, 246, 0.2); color: #60a5fa; font-size: 0.75rem; font-weight: bold;">●</span>
        <div style="flex: 1;">
          <div style="font-size: 0.875rem; font-weight: 600; color: #60a5fa;">3. PySpark Aggregations</div>
          <div style="font-size: 0.75rem; color: #93c5fd;">Stage 4 of 8 active (16 executors)</div>
        </div>
        <span style="font-size: 0.75rem; color: #60a5fa; font-family: monospace;">Running</span>
      </div>
      <div style="display: flex; align-items: flex-start; gap: 0.75rem; opacity: 0.6;">
        <span style="display: flex; align-items: center; justify-content: center; width: 1.5rem; height: 1.5rem; border-radius: 9999px; background: #27272a; color: #a1a1aa; font-size: 0.75rem;">○</span>
        <div style="flex: 1;">
          <div style="font-size: 0.875rem; font-weight: 500; color: #fafafa;">4. Load to ClickHouse Data Mart</div>
          <div style="font-size: 0.75rem; color: #71717a;">Awaiting stage 3</div>
        </div>
        <span style="font-size: 0.75rem; color: #71717a; font-family: monospace;">Pending</span>
      </div>
    </div>
  </div>
</div>

---

### `DataTimeline`
Vertical activity stream and audit log for pipeline triggers and system events.

```python
from pydataui.components.data_science import DataTimeline

DataTimeline(
    events=[
        {"time": "08:00:00", "label": "Scheduled Airflow DAG run triggered", "status": "info"},
        {"time": "08:01:12", "label": "S3 raw extract completed (14,200 partitions)", "status": "success"},
        {"time": "08:04:30", "label": "Great Expectations test suite passed", "status": "success"},
        {"time": "08:06:45", "label": "Cluster scaled from 4 to 16 compute nodes", "status": "info"},
    ]
)
```

---

### `SchemaViewer`
Interactive table inspecting dataset columns, data types, null counts, and unique value counts.

```python
from pydataui.components.data_science import SchemaViewer

# Option 1: Pass pandas DataFrame directly
SchemaViewer(df=my_dataframe)

# Option 2: Pass explicit schema dictionary
SchemaViewer(
    schema={
        "user_id": "int64",
        "email": "varchar(255)",
        "signup_ts": "datetime64[ns]",
        "lifetime_spend": "float64"
    }
)
```

---

### `SQLEditor`
SQL query console with query parameter binding and an inline Run action button.

```python
from pydataui.components.data_science import SQLEditor
from pydataui import State

class QueryState(State):
    query_text: str = "SELECT * FROM transactions LIMIT 100;"

    def run_query(self):
        # Execute query against database
        ...

SQLEditor(
    bind=QueryState.query_text,
    on_run=QueryState.run_query,
    rows=10,
    placeholder="Enter your SQL query here..."
)
```

---

### `FileDownload` & `DataUpload`
In-browser data interchange components.

```python
from pydataui.components.data_science import FileDownload, DataUpload

# Export CSV button
FileDownload(
    filename="aggregated_report.csv",
    content="date,metric\n2024-01-01,100\n",
    label="Download CSV Export"
)

# Upload dataset area
DataUpload(
    accept=".csv,.parquet,.json",
    on_upload="/api/data/upload"
)
```

---

### `JSONViewer` & `CodeBlock`
Pretty-printed technical data displays.

```python
from pydataui.components.data_science import JSONViewer, CodeBlock

# Collapsible formatted JSON
JSONViewer(
    data={"model": "Llama-3-70B", "quantization": "4-bit", "context_window": 8192}
)

# Syntax-aware code block with one-click copy button
CodeBlock(
    code="""from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('Ingest').getOrCreate()
df = spark.read.parquet('s3://lake/raw/*')
""",
    language="python"
)
```
