from pydataui.components.data_science import (
    DataFrameTable, MetricCard, ModelMetrics, PipelineStatus,
    ConfusionMatrix, JSONViewer, CodeBlock, FileDownload,
    DataUpload, SQLEditor, PlotlyChart, DataTimeline,
    FeatureImportance, SchemaViewer
)

def test_metric_card():
    card = MetricCard(
        title="Conversion Rate",
        value=0.0482,
        format=".2%",
        delta="+0.8%",
        delta_type="increase",
        icon="📊",
        description="Compared to last week"
    )
    html = card.render({})
    assert "Conversion Rate" in html
    assert "4.82%" in html
    assert "+0.8%" in html
    assert "text-green-600" in html
    assert "📊" in html
    assert "Compared to last week" in html

def test_model_metrics():
    mm = ModelMetrics(metrics={"AUC": 0.985, "F1": 0.942, "Accuracy": 0.951})
    html = mm.render({})
    assert "AUC" in html
    assert "0.9850" in html
    assert "F1" in html
    assert "0.9420" in html

def test_pipeline_status():
    ps = PipelineStatus(steps=[
        {"name": "Fetch S3", "status": "success"},
        {"name": "Cleanse", "status": "running"},
        {"name": "Load DW", "status": "pending"},
    ])
    html = ps.render({})
    assert "Fetch S3" in html
    assert "Cleanse" in html
    assert "Load DW" in html
    assert "bg-green-500" in html
    assert "animate-pulse" in html

def test_confusion_matrix():
    cm = ConfusionMatrix(
        matrix=[[100, 10], [5, 85]],
        labels=["Negative", "Positive"]
    )
    html = cm.render({})
    assert "Predicted" in html
    assert "Actual" in html
    assert "Negative" in html
    assert "Positive" in html
    assert "100" in html
    assert "85" in html

def test_json_viewer():
    jv = JSONViewer(data={"model": "ResNet50", "epochs": 100, "layers": [64, 128, 256]})
    html = jv.render({})
    assert "ResNet50" in html
    assert "epochs" in html
    assert "256" in html

def test_code_block():
    cb = CodeBlock(code="SELECT count(*) FROM users WHERE is_active = true;", language="sql")
    html = cb.render({})
    assert "SELECT count(*)" in html
    assert "sql" in html
    assert "Copy" in html

def test_file_download():
    fd = FileDownload(filename="dataset.csv", content="col1,col2\n1,2", label="Export CSV")
    html = fd.render({})
    assert "dataset.csv" in html
    assert "data:text/plain;base64," in html
    assert "Export CSV" in html

def test_feature_importance():
    fi = FeatureImportance(
        features={"user_age": 0.45, "credit_score": 0.35, "income": 0.20},
        title="Credit Risk Factors"
    )
    html = fi.render({})
    assert "Credit Risk Factors" in html
    assert "user_age" in html
    assert "credit_score" in html
    assert "0.4500" in html

def test_schema_viewer_dict():
    sv = SchemaViewer(schema={"user_id": "int64", "email": "varchar(255)", "created_at": "timestamp"})
    html = sv.render({})
    assert "user_id" in html
    assert "varchar(255)" in html
    assert "timestamp" in html
