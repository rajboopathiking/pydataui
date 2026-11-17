"""
Next.js-Style Full-Stack SaaS Example in PyDataUI.

Run with:
    python examples/nextjs_style_fullstack.py

Highlights:
- Full-Stack Architecture in 1 Language (Python): Replaces Next.js + FastAPI dual stack.
- Multi-page routing via `@app.page()`.
- Server Actions via `@s.action`: Mutates state & swaps DOM surgically via HTMX.
- Direct In-Memory Data Access: 0ms latency between UI and backend logic.
- Built-in FastAPI REST API & Swagger UI documentation at `/docs`.
"""
from pydataui import (
    App, Container, Card, Heading, Text, Button, Table, Row, Col, state
)
from pydantic import BaseModel, Field

# 1. Initialize Full-Stack App
app = App(title="CloudAI Enterprise SaaS", debug=True)

# 2. Server-Side Reactive State & Server Actions (Next.js "use server" equivalent)
s = state(
    tier="Pro",
    credits=1500,
    api_calls=48200,
    deployments=[
        {"id": "dep-01", "model": "Llama-3.3-70B", "status": "Running", "rps": 340},
        {"id": "dep-02", "model": "DeepSeek-R1", "status": "Running", "rps": 580},
    ]
)

@s.action
def deploy_model(model_name: str = "Mistral-Large"):
    """Server action: mutates state in-memory and triggers surgical DOM update."""
    new_id = f"dep-0{len(s.deployments) + 1}"
    s.deployments.append({"id": new_id, "model": model_name, "status": "Running", "rps": 120})
    s.credits -= 100

@s.action
def recharge_credits():
    s.credits += 500


# 3. Next.js App Router Page Equivalent (`app/page.tsx`)
@app.page("/")
def dashboard_page():
    return Container(
        Row(
            Heading("Enterprise AI Cloud Dashboard", level=1),
            Button("Recharge +500 Credits", on_click=s.recharge_credits, variant="outline"),
            class_name="flex justify-between items-center mb-6"
        ),
        Row(
            Card(
                Heading("Subscription Tier", level=4),
                Text(s.tier, class_name="text-2xl font-bold text-primary"),
                class_name="flex-1"
            ),
            Card(
                Heading("Remaining Credits", level=4),
                Text(s.credits, class_name="text-2xl font-bold text-emerald-600"),
                class_name="flex-1"
            ),
            Card(
                Heading("Monthly API Requests", level=4),
                Text(f"{s.api_calls:,}", class_name="text-2xl font-bold"),
                class_name="flex-1"
            ),
            class_name="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
        ),
        Card(
            Row(
                Heading("Active Model Deployments", level=2),
                Button("+ Deploy Mistral-Large", on_click=lambda: deploy_model("Mistral-Large"), variant="primary"),
                class_name="flex justify-between items-center mb-4"
            ),
            Table(data=s.deployments),
            class_name="p-6 shadow-sm"
        ),
        class_name="max-w-6xl mx-auto p-8 space-y-6"
    )


# 4. Built-in FastAPI Route Handlers (Next.js route.ts / FastAPI API equivalent)
class InferenceRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    max_tokens: int = Field(default=256, ge=1, le=4096)

@app.api("/api/v1/generate", method="POST", tags=["AI Inference"])
async def generate_api(body: InferenceRequest):
    """External API endpoint automatically documented in Swagger UI at /docs."""
    # Direct access to server state in the same process
    s.api_calls += 1
    return {
        "success": True,
        "model": "Llama-3.3-70B",
        "output": f"Generated completion for: {body.prompt[:50]}...",
        "tokens_used": 42
    }


if __name__ == "__main__":
    print("Serving UI at: http://127.0.0.1:8000/")
    print("OpenAPI Docs at: http://127.0.0.1:8000/docs")
    app.run(port=8000)
