"""
AI Customer Support Chatbot Example
Demonstrates modern commercial UI/UX with PyDataUI:
- Zero-class procedural state hook (state(**defaults))
- High-level commercial Chat component with speech bubbles and online status
- Automatic dual-compatibility: Web SSR (FastAPI + HTMX) and Terminal TUI (pydataui tui)
"""
from pydataui import App, state, Container
from pydataui.components import Chat
import httpx

app = App(title="AI Customer Support")

# 1. Zero-Class Reactive State
s = state(
    messages=[
        {"role": "assistant", "content": "Hello! I am your AI Support Assistant. Ask me anything."}
    ],
    session_id="sess_001",
)

# 2. Asynchronous Message Dispatcher
@s.action
async def handle_chat(message: str = "", **kwargs):
    user_msg = message or kwargs.get("message", "").strip()
    if not user_msg:
        return

    # Reflect user message immediately
    s.messages.append({"role": "user", "content": user_msg})

    # Optional backend LLM/API call (or graceful local simulation)
    try:
        async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=120.0) as client:
            resp = await client.post(
                "/chat/invoke",
                json={"id": s.session_id, "message": user_msg}
            )
            resp.raise_for_status()
            reply = resp.json().get("response", "Thank you for reaching out.")
    except Exception:
        # Fallback intelligent customer support response
        q_lower = user_msg.lower()
        if "order" in q_lower or "track" in q_lower:
            reply = "Your order #10492 is out for delivery today via FedEx. Tracking: FX-8492041."
        elif "refund" in q_lower or "return" in q_lower:
            reply = "Returns are accepted within 30 days of purchase. A prepaid return label has been emailed to you."
        elif "hours" in q_lower or "support" in q_lower:
            reply = "Our technical support team is available 24/7. Live agent escalation is ready if needed."
        else:
            reply = f"Thank you for reaching out. We received your request: '{user_msg}'. An agent is reviewing it."

    s.messages.append({"role": "assistant", "content": reply})

# 3. Clean Declarative Layout
@app.page("/")
def home():
    return Container(
        Chat(
            messages=s.messages,
            title="Customer Support AI",
            placeholder="Type your message and press Enter...",
            on_send=handle_chat,
        ),
        max_width="lg",
        padding="lg",
    )

if __name__ == "__main__":
    app.run(port=8000)
