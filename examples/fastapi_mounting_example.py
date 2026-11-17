"""
Mounting PyDataUI Inside an Existing FastAPI Application.

Run with:
    uvicorn examples.fastapi_mounting_example:app --reload --port 8000

Highlights:
- Unlike Streamlit (which runs on Tornado and CANNOT be mounted into FastAPI without subprocess hacks),
  PyDataUI is a 100% standard ASGI application with a compiled Rust HTTP core.
- You can mount a complete reactive PyDataUI dashboard inside any existing FastAPI backend
  using standard `fastapi_app.mount("/ui", pdu_app)`.
- Shares the same process, same memory, and same port!
"""
from fastapi import FastAPI
from pydataui import App, Container, Heading, Text, Button, Table, state

# 1. Your Existing Enterprise FastAPI Application
app = FastAPI(
    title="Core Enterprise Microservice",
    description="Existing backend API with PyDataUI mounted for internal admin dashboard",
    version="1.0.0"
)

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "Core Enterprise Microservice"}


# 2. Build PyDataUI Dashboard (or import it from a separate module)
pdu_app = App(title="Internal Admin Operations", debug=True)

admin_state = state(
    system_load="14%",
    active_workers=8,
    incidents=[]
)

@admin_state.action
def simulate_incident():
    admin_state.incidents.append({
        "id": f"INC-{len(admin_state.incidents) + 1}",
        "severity": "Low",
        "description": "Transient API spike handled successfully"
    })

@pdu_app.page("/")
def admin_home():
    return Container(
        Heading("Internal Microservice Operations Dashboard", level=1),
        Text(f"System Load: {admin_state.system_load} | Active Workers: {admin_state.active_workers}"),
        Button("+ Trigger Test Incident", on_click=admin_state.simulate_incident),
        Table(data=admin_state.incidents),
        class_name="max-w-4xl mx-auto p-6 space-y-4"
    )


# 3. Mount PyDataUI into FastAPI with 1 Line!
# PyDataUI's underlying FastAPIEngine/Starlette ASGI app mounts cleanly:
app.mount("/dashboard", pdu_app._engine.app)


if __name__ == "__main__":
    import uvicorn
    print("Serving FastAPI API at:        http://127.0.0.1:8000/api/health")
    print("Serving FastAPI Docs at:       http://127.0.0.1:8000/docs")
    print("Serving PyDataUI Dashboard at: http://127.0.0.1:8000/dashboard/")
    uvicorn.run(app, host="127.0.0.1", port=8000)
