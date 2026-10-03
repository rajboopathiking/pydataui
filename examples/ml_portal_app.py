"""
Production ML Evaluation & Model Registry Portal.
Showcases:
  - AuthManager (RBAC & API Keys)
  - Data Science Components (ModelMetrics, ConfusionMatrix, FeatureImportance, PipelineStatus)
  - shadcn/ui components (ShadCard, ShadButton, ShadBadge)
  - Automatic REST API endpoints
"""
from pydataui import App, State
from pydataui.components import Container, Heading, Grid, Flex, Card
from pydataui.components.data_science import (
    ModelMetrics, ConfusionMatrix, FeatureImportance, PipelineStatus
)
from pydataui.components.shadcn import ShadButton, ShadBadge
from pydataui.auth import (
    AuthManager, Role, LoginPage, UserMenu, APIKeyManager, require_auth
)

app = App(
    title="MLOps Model Performance Hub",
    description="Enterprise ML Evaluation, Monitoring & Key Provisioning Portal",
    version="0.2.0"
)

auth = AuthManager(secret_key="production-mlops-portal-secret-key-min-32-chars!")

# Seed users
admin = auth.add_user("lead_mlops", "admin123", email="mlops@corp.internal", roles=[Role.ADMIN, Role.ML_ENGINEER])
analyst = auth.add_user("data_analyst", "analyst123", email="analyst@corp.internal", roles=[Role.DATA_ANALYST])

# Seed production API key
auth.create_api_key("Continuous-Training-Pipeline", admin.id, scopes=["read", "write"])

app.setup_auth(auth)


class ModelTrainingState(State):
    model_version: str = "v3.2.1"
    is_evaluating: bool = False
    accuracy: float = 0.9642
    roc_auc: float = 0.9891

    def trigger_evaluation(self):
        self.is_evaluating = True
        self.accuracy = 0.9685
        self.roc_auc = 0.9912


@app.page("/login")
def login_view():
    return LoginPage(
        title="MLOps Control Hub",
        subtitle="Sign in with your engineering or analyst credentials",
        redirect_to="/"
    )


@app.page("/")
def hub_dashboard():
    keys = auth.list_api_keys(admin.id)
    return Container(
        Flex(
            Heading("Production Model Registry & Evaluation", level=1),
            UserMenu(admin),
            justify="space-between", align="center", margin_bottom="lg"
        ),
        # KPI & Metrics
        ModelMetrics(
            metrics={
                "Accuracy": ModelTrainingState.accuracy,
                "Precision": 0.9510,
                "Recall": 0.9780,
                "ROC-AUC": ModelTrainingState.roc_auc
            }
        ),
        # Visualizations Grid
        Grid(
            ConfusionMatrix(
                matrix=[[2840, 64], [38, 2690]],
                labels=["Normal", "Anomaly"]
            ),
            FeatureImportance(
                features={
                    "request_frequency_delta_10m": 0.342,
                    "jwt_token_entropy": 0.281,
                    "payload_size_stdev": 0.174,
                    "client_ip_subnet_risk": 0.125,
                    "failed_handshakes_1h": 0.078
                },
                title="Top Predictive Features"
            ),
            columns=2, gap="lg", margin_top="lg", margin_bottom="lg"
        ),
        # Pipeline Status
        Card(
            title="CI/CD Model Retraining Pipeline",
            children=[
                PipelineStatus(steps=[
                    {"name": "1. Extract Delta Lake Embeddings", "status": "success", "message": "2.4GB synced"},
                    {"name": "2. Validate Data Drift (PSI < 0.05)", "status": "success", "message": "Passed"},
                    {"name": "3. Distributed PyTorch Fine-tuning", "status": "running", "message": "Epoch 14/20"},
                    {"name": "4. Model Registry Promotion (MLflow)", "status": "pending", "message": "Waiting"},
                ])
            ],
            margin_bottom="lg"
        ),
        # API Key management
        APIKeyManager(keys=keys),
        padding="lg"
    )


if __name__ == "__main__":
    app.run(share=True, port=8080)
