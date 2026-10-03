TEMPLATES = {
    "basic": '''from pydataui import App, State
from pydataui.components import Container, Card, Flex, Button, Heading, Divider

class CounterState(State):
    count: int = 0
    def increment(self): self.count += 1
    def decrement(self): self.count -= 1
    def reset(self): self.count = 0

app = App(title="PyDataUI Counter")

@app.page("/")
def home():
    return Container(
        Card(
            title="Counter App",
            children=[
                Flex(
                    Button("-", on_click=CounterState.decrement, variant="danger"),
                    Heading(CounterState.count, level=2),
                    Button("+", on_click=CounterState.increment, variant="success"),
                    align="center", justify="center", gap="lg",
                ),
                Divider(),
                Button("Reset", on_click=CounterState.reset, variant="outline", full_width=True),
            ]
        ),
        max_width="md",
        padding="lg",
    )

if __name__ == "__main__":
    app.run()
''',

    "dashboard": '''from pydataui import App, State
from pydataui.components import Container, Grid, Flex, Heading, Card, Stat, BarChart, Table

app = App(title="Data Analytics Dashboard")

@app.page("/")
def dashboard():
    return Container(
        Heading("Data Analytics Dashboard", level=1, margin_bottom="lg"),
        Grid(
            Stat(label="Total Ingested Rows", value="1.24M", change="+14.2%", trend="up"),
            Stat(label="Pipeline Success Rate", value="99.8%", change="+0.4%", trend="up"),
            Stat(label="Active Queries / sec", value="432", change="-5.1%", trend="down"),
            Stat(label="P99 Query Latency", value="42ms", change="-12ms", trend="up"),
            columns=4, gap="md", margin_bottom="lg"
        ),
        Card(
            title="Daily Ingestion Volume (GB)",
            children=[
                BarChart(
                    labels=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                    datasets=[{"label": "Processed Data (GB)", "data": [120, 190, 240, 210, 280, 150, 110]}],
                    height=280
                )
            ],
            margin_bottom="lg"
        ),
        Card(
            title="Top Active Data Sources",
            children=[
                Table(
                    columns=["Source", "Type", "Status", "Throughput"],
                    data=[
                        ["Postgres Warehouse", "Relational", "Healthy", "12.4 MB/s"],
                        ["Kafka Clickstream", "Streaming", "Healthy", "48.1 MB/s"],
                        ["S3 Delta Lake", "Object Storage", "Synced", "8.2 MB/s"],
                        ["Snowflake Sync", "Data Warehouse", "Idle", "0.0 MB/s"],
                    ]
                )
            ]
        ),
        padding="lg"
    )

if __name__ == "__main__":
    app.run()
''',

    "crud": '''from pydataui import App, State
from pydataui.components import Container, Card, Flex, Button, Heading, Table, Modal, Input, Alert
from pydantic import BaseModel
import uuid

class Dataset(BaseModel):
    id: str
    name: str
    owner: str
    records: int

class DatasetState(State):
    datasets: list = [
        {"id": "1", "name": "Customer Transactions", "owner": "alice@company.com", "records": 450000},
        {"id": "2", "name": "Model Predictions Log", "owner": "bob@company.com", "records": 1200000},
    ]
    show_modal: bool = False
    new_name: str = ""
    new_owner: str = ""
    new_records: int = 0
    message: str = ""

    def open_modal(self):
        self.new_name = ""
        self.new_owner = ""
        self.new_records = 0
        self.show_modal = True

    def close_modal(self):
        self.show_modal = False

    def add_dataset(self):
        if self.new_name.strip():
            self.datasets.append({
                "id": uuid.uuid4().hex[:6],
                "name": self.new_name.strip(),
                "owner": self.new_owner.strip() or "admin@company.com",
                "records": int(self.new_records) if self.new_records else 1000,
            })
            self.message = f"Dataset '{self.new_name}' created successfully!"
            self.show_modal = False

    def delete_dataset(self, item_id: str):
        self.datasets = [d for d in self.datasets if d["id"] != item_id]
        self.message = "Dataset deleted."

app = App(title="Dataset Catalog CRUD")

@app.page("/")
def home():
    alert_box = Alert(DatasetState.message, variant="success", margin_bottom="md") if DatasetState.message else None
    
    rows = []
    for d in DatasetState.datasets:
        del_btn = Button("Delete", size="sm", variant="danger", on_click=lambda id=d["id"]: DatasetState.delete_dataset(id))
        rows.append([d["id"], d["name"], d["owner"], f"{d['records']:,}", del_btn])

    modal = None
    if DatasetState.show_modal:
        modal = Modal(
            title="Register New Dataset",
            is_open=True,
            on_close=DatasetState.close_modal,
            children=[
                Flex(
                    Input("Dataset Name", bind=DatasetState.new_name, placeholder="e.g. clickstream_v2"),
                    Input("Owner Email", bind=DatasetState.new_owner, placeholder="e.g. engineer@org.com"),
                    Input("Estimated Records", bind=DatasetState.new_records, type="number"),
                    direction="column", gap="md"
                ),
                Flex(
                    Button("Cancel", variant="outline", on_click=DatasetState.close_modal),
                    Button("Save", variant="primary", on_click=DatasetState.add_dataset),
                    justify="flex-end", gap="sm", margin_top="md"
                )
            ]
        )

    return Container(
        Flex(
            Heading("Data Catalog", level=1),
            Button("+ Register Dataset", variant="primary", on_click=DatasetState.open_modal),
            justify="space-between", align="center", margin_bottom="lg"
        ),
        alert_box,
        Card(
            children=[
                Table(
                    columns=["ID", "Dataset Name", "Owner", "Records", "Actions"],
                    data=rows
                )
            ]
        ),
        modal,
        padding="lg"
    )

if __name__ == "__main__":
    app.run()
''',

    "ml-dashboard": '''from pydataui import App, State
from pydataui.components import Container, Heading, Flex, Grid, Card
from pydataui.components.data_science import MetricCard, ModelMetrics, ConfusionMatrix, FeatureImportance

app = App(title="ML Model Evaluation Dashboard")

@app.page("/")
def ml_dashboard():
    return Container(
        Heading("Production Model Performance (XGBoost v2.4)", level=1, margin_bottom="lg"),
        ModelMetrics(
            metrics={
                "Accuracy": 0.9452,
                "Precision": 0.9310,
                "Recall": 0.9580,
                "ROC-AUC": 0.9841
            }
        ),
        Grid(
            ConfusionMatrix(
                matrix=[[1450, 68], [42, 1380]],
                labels=["Normal", "Anomaly"]
            ),
            FeatureImportance(
                features={
                    "request_rate_10m": 0.324,
                    "error_ratio_1h": 0.281,
                    "payload_size_bytes": 0.174,
                    "client_ip_entropy": 0.125,
                    "auth_failures_count": 0.096,
                },
                title="Top Predictive Features"
            ),
            columns=2, gap="lg", margin_top="lg"
        ),
        padding="lg"
    )

if __name__ == "__main__":
    app.run()
''',

    "data-pipeline": '''from pydataui import App, State
from pydataui.components import Container, Heading, Grid, Card, Flex, Button
from pydataui.components.data_science import PipelineStatus, DataTimeline

app = App(title="Data Pipeline Monitor")

@app.page("/")
def pipeline_tracker():
    return Container(
        Flex(
            Heading("Data Pipeline Monitor", level=1),
            Button("Trigger Pipeline", variant="primary"),
            justify="space-between", align="center", margin_bottom="lg"
        ),
        Grid(
            Card(
                title="ETL DAG Execution Status",
                children=[
                    PipelineStatus(steps=[
                        {"name": "1. Extract from S3 Raw Buckets", "status": "success", "message": "1.8GB extracted in 14s"},
                        {"name": "2. Schema Validation & De-duplication", "status": "success", "message": "0 schema violations"},
                        {"name": "3. PySpark Transformations & Aggregations", "status": "running", "message": "Task 14/20 running"},
                        {"name": "4. Load to ClickHouse Data Marts", "status": "pending", "message": "Awaiting stage 3"},
                        {"name": "5. Refresh Metabase Cache", "status": "pending", "message": "Awaiting stage 4"},
                    ])
                ]
            ),
            Card(
                title="Audit & Run Timeline",
                children=[
                    DataTimeline(events=[
                        {"time": "10:00:00", "label": "Scheduled DAG triggered by cron", "status": "info"},
                        {"time": "10:00:14", "label": "Extract completed (2,410 files)", "status": "success"},
                        {"time": "10:01:05", "label": "Data quality check passed", "status": "success"},
                        {"time": "10:02:18", "label": "Spark cluster allocated 16 workers", "status": "running"},
                    ])
                ]
            ),
            columns=2, gap="lg"
        ),
        padding="lg"
    )

if __name__ == "__main__":
    app.run()
''',

    "auth": '''from pydataui import App, State
from pydataui.components import Container, Card, Heading, Text, Flex
from pydataui.auth import AuthManager, LoginPage, UserMenu, APIKeyManager, require_auth, User, Role

app = App(title="PyDataUI Workspace with Auth")
auth_mgr = AuthManager(secret_key="my-super-secret-key-12345")

# Seed initial users
admin_user = auth_mgr.add_user("admin", "admin123", email="admin@org.com", roles=[Role.ADMIN, Role.DATA_ENGINEER])
analyst_user = auth_mgr.add_user("analyst", "analyst123", email="analyst@org.com", roles=[Role.DATA_ANALYST])

# Generate a sample API key
auth_mgr.create_api_key("ETL-Ingestion-Key", admin_user.id, scopes=["read", "write"])

app.setup_auth(auth_mgr)

@app.page("/login")
def login_page():
    return LoginPage(title="PyDataUI Secure Portal", subtitle="Sign in with your team credentials")

@app.page("/")
def dashboard():
    keys = auth_mgr.list_api_keys(admin_user.id)
    return Container(
        Flex(
            Heading("Data Science Control Panel", level=1),
            UserMenu(admin_user),
            justify="space-between", align="center", margin_bottom="lg"
        ),
        Card(
            title="Team Credentials Info",
            children=[
                Text("Demo accounts created: <b>admin / admin123</b> and <b>analyst / analyst123</b>")
            ],
            margin_bottom="lg"
        ),
        APIKeyManager(keys=keys),
        padding="lg"
    )

if __name__ == "__main__":
    app.run()
'''
}
