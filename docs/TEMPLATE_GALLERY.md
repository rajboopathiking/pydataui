# Data Team Page Templates Gallery

PyDataUI provides ready-to-use, production-grade page templates in `pydataui.templates` for data engineering, model operations, executive reporting, and interactive data analysis.

---

## Available Pre-Built Templates

### 1. Data Pipeline Ops (`pipeline_page`)
Real-time monitoring dashboard for ETL data pipelines, queue latency, task throughput, and worker node health.

- **Component**: `pipeline_page(metrics=..., pipelines=..., alert=...)`
- **Key Features**:
  - Live pipeline status cards (`RUNNING`, `SUCCESS`, `FAILED`)
  - Throughput charts and queue backpressure telemetry
  - Interactive retry / pause controls
- **Reference**: See [Data Team Templates](DATA_TEMPLATES.md).

```python
from pydataui import App
from pydataui.templates import pipeline_page

app = App(title="Data Pipeline Ops")

@app.page("/")
def pipeline_dashboard():
    return pipeline_page()
```

---

### 2. Model Observability (`model_eval_page`)
Model evaluation workbench for tracking accuracy, drift, F1-scores, and classification confusion matrices.

- **Component**: `model_eval_page(model_name=..., metrics=..., confusion_matrix=...)`
- **Key Features**:
  - Precision, Recall, F1, and AUC scorecards
  - High-density classification confusion matrix
  - Residual error distribution plots
- **Reference**: See [Data Team Templates](DATA_TEMPLATES.md).

```python
from pydataui import App
from pydataui.templates import model_eval_page

app = App(title="Model Evaluation")

@app.page("/")
def eval_dashboard():
    return model_eval_page(model_name="Llama-3-8B-Instruct")
```

---

### 3. Executive KPI Dashboard (`kpi_dashboard_page`)
High-level operational summary designed for business intelligence and executive review.

- **Component**: `kpi_dashboard_page(metrics=..., tables=...)`
- **Key Features**:
  - Quarterly and monthly growth metrics with trend badges
  - Multi-tier breakdown cards
  - Top performer tables with universal sorting
- **Reference**: See [Data Team Templates](DATA_TEMPLATES.md).

```python
from pydataui import App
from pydataui.templates import kpi_dashboard_page

app = App(title="Executive Reporting")

@app.page("/")
def executive_kpis():
    return kpi_dashboard_page()
```

---

### 4. Interactive Data Analysis (`data_analysis_page`)
Self-service analytics studio featuring DuckDB / Polars querying, data filtering, and CSV / Parquet exports.

- **Component**: `data_analysis_page(dataset=..., query=...)`
- **Key Features**:
  - Embedded SQL query editor
  - Universal data sniffing for Pandas, Polars, and DuckDB
  - Instant download and upload capabilities
- **Reference**: See [Data Team Templates](DATA_TEMPLATES.md).

```python
from pydataui import App
from pydataui.templates import data_analysis_page

app = App(title="Interactive Analytics Studio")

@app.page("/")
def analytics_studio():
    return data_analysis_page()
```

---

## Running the Showcase Example

To run a live showcase of all templates simultaneously:

```bash
python examples/commercial_saas_app.py
```
Or run in terminal UI mode:
```bash
pydataui run --tui examples/commercial_saas_app.py
```
