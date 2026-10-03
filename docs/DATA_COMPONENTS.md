# Data Science & Engineering Components Guide

PyDataUI provides first-class native components built specifically for data professionals. Rather than wiring together complex frontend widgets, you can pass Python data structures, pandas DataFrames, and Plotly charts directly to PyDataUI components.

---

## Table of Contents

- [For Data Analysts](#for-data-analysts)
  - [DataFrameTable](#dataframetable)
  - [PlotlyChart](#plotlychart)
  - [MetricCard](#metriccard)
- [For AI & ML Engineers](#for-ai--ml-engineers)
  - [ModelMetrics](#modelmetrics)
  - [ConfusionMatrix](#confusionmatrix)
  - [FeatureImportance](#featureimportance)
- [For Data Engineers](#for-data-engineers)
  - [PipelineStatus](#pipelinestatus)
  - [DataTimeline](#datatimeline)
  - [SchemaViewer](#schemaviewer)
  - [SQLEditor](#sqleditor)
  - [FileDownload & DataUpload](#filedownload--dataupload)
  - [JSONViewer & CodeBlock](#jsonviewer--codeblock)

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
