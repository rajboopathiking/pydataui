"""
Commercial Enterprise SaaS Application Example for PyDataUI:
"aiMetrics AI" — Enterprise LLM Gateway, Observability & Subscription Billing Platform.

Demonstrates:
  1. Multi-Page Navigation with a Unified Commercial Layout
  2. Reactive Event Handlers (Time-range filtering, Model benchmarks, Subscription upgrades)
  3. Enterprise Authentication & Role-Based Access Control (RBAC)
  4. shadcn/ui & Data Science Components (MetricCard, PipelineStatus, ShadBadge, ShadButton, ShadCard)
  5. Persistent SQLite WAL Storage for Multi-Worker Deployment
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import os

from pydataui import App, State, AppConfig
from pydataui.components import (
    Container, Card, Flex, Grid, HStack, VStack, Divider,
    Heading, Text, Badge, Button, Table, Link, RawHtml
)
from pydataui.components.data_science import (
    MetricCard, PipelineStatus, ModelMetrics, CodeBlock, JSONViewer
)
from pydataui.components.shadcn import (
    ShadButton, ShadBadge, ShadCard, ShadCardHeader,
    ShadCardTitle, ShadCardDescription, ShadCardContent,
    ShadProgress, ShadAlert
)
from pydataui.auth import (
    AuthManager, Role, LoginPage, UserMenu, APIKeyManager,
    current_user
)


# ==============================================================================
# 1. Application Initialization & Storage Backend
# ==============================================================================

app = App(
    title="AIMetrics AI — Enterprise LLM Observability & Billing",
    description="Commercial Multi-Tenant AI Gateway, Observability & Subscription Management Platform",
    version="1.0.0",
    storage="sqlite:///.ai_metrics.db",  # Cross-process SQLite WAL storage
    theme="light",
    palette="zinc"
)

auth = AuthManager(secret_key=os.environ.get("PYDATAUI_AUTH_SECRET", "ai-metrics-enterprise-secret-key-32bytes!"))

# Seed Enterprise Accounts (idempotent across restarts)
admin_user = auth.get_or_create_user(
    "admin@ai.com", "admin123",
    email="admin@ai.com",
    roles=[Role.ADMIN, Role.ML_ENGINEER]
)
dev_user = auth.get_or_create_user(
    "developer@ai.com", "developer123",
    email="dev@ai.com",
    roles=[Role.ML_ENGINEER, Role.USER]
)

# Seed Gateway API Key if not present
if not auth.list_api_keys(admin_user.id):
    auth.create_api_key("Production-Inference-Gateway", admin_user.id, scopes=["read", "write"])

app.setup_auth(auth)


# ==============================================================================
# 2. Reactive State Models
# ==============================================================================

class GatewayState(State):
    """Reactive state managing metrics, active time filter, model selection and billing."""
    time_range: str = "30d"
    mrr: str = "$148,250"
    mrr_delta: str = "+14.8%"
    active_tokens: str = "142.8M"
    active_tokens_delta: str = "+28.5%"
    p99_latency: str = "142ms"
    p99_delta: str = "-18ms"
    total_requests: str = "12,845,920"
    
    # Model Observatory State
    selected_model: str = "Claude 3.5 Sonnet"
    model_provider: str = "Anthropic"
    model_cost_per_m: str = "$3.00 / $15.00"
    model_latency: str = "138ms"
    model_accuracy: float = 0.984
    model_f1: float = 0.962
    
    # Billing State
    current_tier: str = "Enterprise Scale"
    tier_price: str = "$1,499"
    tier_period: str = "month"
    token_usage_pct: int = 57  # 57% of 250M quota
    
    # Benchmark Simulation State
    benchmark_status: str = "Ready"
    benchmark_runs: int = 14

    # ---- Actions ----
    def filter_24h(self):
        self.time_range = "24h"
        self.mrr = "$148,250"
        self.active_tokens = "4.8M"
        self.p99_latency = "135ms"
        self.total_requests = "432,100"

    def filter_7d(self):
        self.time_range = "7d"
        self.mrr = "$148,250"
        self.active_tokens = "34.2M"
        self.p99_latency = "139ms"
        self.total_requests = "3,110,400"

    def filter_30d(self):
        self.time_range = "30d"
        self.mrr = "$148,250"
        self.active_tokens = "142.8M"
        self.p99_latency = "142ms"
        self.total_requests = "12,845,920"

    def select_claude(self):
        self.selected_model = "Claude 3.5 Sonnet"
        self.model_provider = "Anthropic"
        self.model_cost_per_m = "$3.00 / $15.00"
        self.model_latency = "138ms"
        self.model_accuracy = 0.984
        self.model_f1 = 0.962

    def select_gpt4o(self):
        self.selected_model = "GPT-4o"
        self.model_provider = "OpenAI"
        self.model_cost_per_m = "$2.50 / $10.00"
        self.model_latency = "145ms"
        self.model_accuracy = 0.978
        self.model_f1 = 0.954

    def select_gemini(self):
        self.selected_model = "Gemini 1.5 Pro"
        self.model_provider = "Google"
        self.model_cost_per_m = "$1.75 / $7.00"
        self.model_latency = "128ms"
        self.model_accuracy = 0.972
        self.model_f1 = 0.948

    def select_llama(self):
        self.selected_model = "Llama 3.3 70B"
        self.model_provider = "Meta (Self-Hosted)"
        self.model_cost_per_m = "$0.35 / $0.80"
        self.model_latency = "89ms"
        self.model_accuracy = 0.945
        self.model_f1 = 0.921

    def trigger_benchmark(self):
        self.benchmark_runs += 1
        self.benchmark_status = f"Completed run #{self.benchmark_runs} (avg: 124ms)"

    def upgrade_starter(self):
        self.current_tier = "Starter"
        self.tier_price = "$99"
        self.token_usage_pct = 88

    def upgrade_growth(self):
        self.current_tier = "Growth"
        self.tier_price = "$499"
        self.token_usage_pct = 64

    def upgrade_enterprise(self):
        self.current_tier = "Enterprise Scale"
        self.tier_price = "$1,499"
        self.token_usage_pct = 57


# ==============================================================================
# 3. Commercial Layout Shell (Header, Navigation, User Menu)
# ==============================================================================

def commercial_shell(content_component, active_tab: str = "dashboard"):
    """Professional SaaS navigation shell with dark/light mode and user menu."""
    user = current_user.get()
    
    # Active navigation link indicator
    def nav_class(name: str):
        base = "text-sm font-medium transition-colors px-3 py-1.5 rounded-md "
        if name == active_tab:
            return base + "bg-primary text-primary-foreground font-semibold shadow-sm"
        return base + "text-muted-foreground hover:text-foreground hover:bg-muted/60"

    header = Flex(
        HStack(
            Flex(
                Text("⚡", class_name="text-xl mr-2"),
                Flex(
                    Heading("AIMetrics", level=4, class_name="font-extrabold tracking-tight text-foreground"),
                    ShadBadge("AI CLOUD", variant="secondary", class_name="ml-2 text-[10px] font-mono"),
                    align="center"
                ),
                align="center",
                class_name="cursor-pointer"
            ),
            # Global status indicator
            Flex(
                Text("●", class_name="text-emerald-500 animate-ai text-xs mr-1.5"),
                Text("Gateway: 99.99% Operational", class_name="text-xs text-muted-foreground font-medium hidden sm:inline"),
                align="center",
                class_name="ml-4 px-2.5 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full"
            ),
            align="center"
        ),
        # Navigation Links
        HStack(
            Link("Overview", href="/", underline=False, class_name=nav_class("dashboard")),
            Link("Models", href="/models", underline=False, class_name=nav_class("models")),
            Link("Billing", href="/billing", underline=False, class_name=nav_class("billing")),
            Link("API Keys", href="/keys", underline=False, class_name=nav_class("keys")),
            Link("API Docs ↗", href="/docs", external=True, underline=False, class_name=nav_class("docs")),
            gap="xs",
            align="center"
        ),
        UserMenu(user=user),
        justify="between",
        align="center",
        class_name="w-full border-b border-border bg-card/80 backdrop-blur px-6 py-3.5 sticky top-0 z-50 shadow-sm"
    )

    return Flex(
        header,
        Container(
            content_component,
            max_width="xl",
            padding="lg",
            center=True,
            class_name="w-full py-8"
        ),
        direction="column",
        class_name="min-h-screen bg-background text-foreground"
    )


# ==============================================================================
# 4. View: Executive Dashboard (`/`)
# ==============================================================================

@app.page("/", public=True)
def dashboard_view():
    user = current_user.get()
    
    # Top Bar: Title & Live Time Range Filters
    top_bar = Flex(
        VStack(
            Heading("Executive Observability Hub", level=2, class_name="font-bold tracking-tight text-2xl"),
            Text("Real-time telemetry, multi-model throughput, and enterprise revenue tracking.",
                 class_name="text-muted-foreground text-sm mt-1")
        ),
        HStack(
            Text("Time Window:", class_name="text-xs text-muted-foreground font-medium self-center mr-1"),
            ShadButton(
                "24 Hours",
                variant="default" if GatewayState.time_range == "24h" else "outline",
                size="sm",
                on_click=GatewayState.filter_24h
            ),
            ShadButton(
                "7 Days",
                variant="default" if GatewayState.time_range == "7d" else "outline",
                size="sm",
                on_click=GatewayState.filter_7d
            ),
            ShadButton(
                "30 Days",
                variant="default" if GatewayState.time_range == "30d" else "outline",
                size="sm",
                on_click=GatewayState.filter_30d
            ),
            gap="xs",
            align="center"
        ),
        justify="between",
        align="center",
        wrap="wrap",
        class_name="gap-4 mb-6"
    )

    # 4 Key Stat Cards
    kpi_grid = Grid(
        MetricCard(
            title="Monthly Recurring Revenue (MRR)",
            value=GatewayState.mrr,
            delta=GatewayState.mrr_delta,
            delta_type="increase",
            icon="💳",
            description="Net ARR run-rate: $1.78M"
        ),
        MetricCard(
            title="Processed LLM Tokens",
            value=GatewayState.active_tokens,
            delta=GatewayState.active_tokens_delta,
            delta_type="increase",
            icon="⚡",
            description="Cross-model token consumption"
        ),
        MetricCard(
            title="Gateway P99 Latency",
            value=GatewayState.p99_latency,
            delta=GatewayState.p99_delta,
            delta_type="decrease",
            icon="⏱️",
            description="Rust Tokio async event-loop core"
        ),
        MetricCard(
            title="Total API Gateway Calls",
            value=GatewayState.total_requests,
            delta="99.98% ok",
            delta_type="neutral",
            icon="📡",
            description="Authenticated multi-tenant traffic"
        ),
        columns=4,
        gap="md",
        class_name="mb-8"
    )

    # Ingestion & Inference Pipeline Tracker
    pipeline_card = ShadCard(
        ShadCardHeader(
            ShadCardTitle("Multi-Model Routing & Guardrail Pipeline"),
            ShadCardDescription("Live inference pipeline stages with sub-millisecond execution checkpoints")
        ),
        ShadCardContent(
            PipelineStatus(steps=[
                {"name": "1. Edge TLS / Ingress Gateway", "status": "success"},
                {"name": "2. HMAC Session & Token Validation", "status": "success"},
                {"name": "3. PII Redaction & Prompt Guardrails", "status": "success"},
                {"name": "4. Semantic Routing & Model Dispatch", "status": "running"},
                {"name": "5. Token Metering & Audit Ledger", "status": "pending"},
            ]),
            Flex(
                HStack(
                    Text("Engine:", class_name="text-xs font-semibold text-muted-foreground"),
                    Text("pyrustapi (Rust Tokio) — Zero Python GIL bottleneck on network I/O",
                         class_name="text-xs text-muted-foreground"),
                    align="center",
                    gap="xs"
                ),
                ShadButton(
                    "Simulate Pipeline Health Check",
                    size="sm",
                    variant="outline",
                    on_click=GatewayState.trigger_benchmark
                ),
                justify="between",
                align="center",
                class_name="mt-6 pt-4 border-t border-border"
            )
        ),
        class_name="mb-8"
    )

    # Quick Action Banner
    benchmark_banner = ShadCard(
        ShadCardContent(
            Flex(
                VStack(
                    HStack(
                        Text("Gateway Benchmark Status:", class_name="text-sm font-semibold"),
                        ShadBadge(GatewayState.benchmark_status, variant="secondary"),
                        align="center",
                        gap="xs"
                    ),
                    Text("Benchmarked against 10,000 concurrent synthetic requests in simulated cluster.",
                         class_name="text-xs text-muted-foreground")
                ),
                ShadButton(
                    "⚡ Run Multi-Worker Latency Benchmark",
                    variant="default",
                    size="sm",
                    on_click=GatewayState.trigger_benchmark
                ),
                justify="between",
                align="center",
                class_name="py-2"
            )
        )
    )

    content = VStack(
        top_bar,
        kpi_grid,
        pipeline_card,
        benchmark_banner,
        gap="none"
    )

    return commercial_shell(content, active_tab="dashboard")


# ==============================================================================
# 5. View: Model Gateway & Observability (`/models`)
# ==============================================================================

@app.page("/models", public=True)
def models_view():
    top_bar = VStack(
        Heading("Model Gateway & Cost Observability", level=2, class_name="font-bold tracking-tight text-2xl"),
        Text("Multi-model routing, token pricing, latency benchmarks, and accuracy evaluation.",
             class_name="text-muted-foreground text-sm mt-1"),
        class_name="mb-6"
    )

    # Model Switcher Buttons
    model_selector = HStack(
        ShadButton(
            "Claude 3.5 Sonnet",
            variant="default" if GatewayState.selected_model == "Claude 3.5 Sonnet" else "outline",
            size="sm",
            on_click=GatewayState.select_claude
        ),
        ShadButton(
            "GPT-4o",
            variant="default" if GatewayState.selected_model == "GPT-4o" else "outline",
            size="sm",
            on_click=GatewayState.select_gpt4o
        ),
        ShadButton(
            "Gemini 1.5 Pro",
            variant="default" if GatewayState.selected_model == "Gemini 1.5 Pro" else "outline",
            size="sm",
            on_click=GatewayState.select_gemini
        ),
        ShadButton(
            "Llama 3.3 70B",
            variant="default" if GatewayState.selected_model == "Llama 3.3 70B" else "outline",
            size="sm",
            on_click=GatewayState.select_llama
        ),
        gap="xs",
        class_name="mb-6"
    )

    # Active Model Detail Card
    selected_card = ShadCard(
        ShadCardHeader(
            Flex(
                VStack(
                    ShadCardTitle(GatewayState.selected_model),
                    ShadCardDescription(f"Provider: {GatewayState.model_provider} • Optimized Gateway Route")
                ),
                ShadBadge("ACTIVE ROUTE", variant="default"),
                justify="between",
                align="start"
            )
        ),
        ShadCardContent(
            Grid(
                MetricCard("Token Pricing (In / Out)", GatewayState.model_cost_per_m, icon="🏷️"),
                MetricCard("Avg Provider TTFT", GatewayState.model_latency, icon="⚡"),
                MetricCard("MMLU Benchmark Score", GatewayState.model_accuracy, format=".1%", icon="🎯"),
                MetricCard("Task F1 Score", GatewayState.model_f1, format=".1%", icon="📊"),
                columns=4,
                gap="md",
                class_name="mb-4"
            )
        ),
        class_name="mb-8"
    )

    # All Models Comparison Table
    table_card = ShadCard(
        ShadCardHeader(
            ShadCardTitle("Enterprise LLM Fleet Performance Matrix"),
            ShadCardDescription("Live routing performance and pricing telemetry across all configured LLM providers.")
        ),
        ShadCardContent(
            Table(
                headers=["Model Name", "Provider", "Input / Output per 1M", "Avg Latency", "Quality Score", "Status"],
                rows=[
                    ["Claude 3.5 Sonnet", "Anthropic", "$3.00 / $15.00", "138ms", "98.4%", ShadBadge("Optimal", variant="default")],
                    ["GPT-4o", "OpenAI", "$2.50 / $10.00", "145ms", "97.8%", ShadBadge("Operational", variant="secondary")],
                    ["Gemini 1.5 Pro", "Google", "$1.75 / $7.00", "128ms", "97.2%", ShadBadge("Operational", variant="secondary")],
                    ["Llama 3.3 70B", "Self-Hosted", "$0.35 / $0.80", "89ms", "94.5%", ShadBadge("High Throughput", variant="outline")],
                ]
            )
        )
    )

    return commercial_shell(VStack(top_bar, model_selector, selected_card, table_card, gap="none"), active_tab="models")


# ==============================================================================
# 6. View: Subscription & Billing Portal (`/billing`)
# ==============================================================================

@app.page("/billing")
def billing_view():
    top_bar = VStack(
        Heading("Subscription & Usage Billing", level=2, class_name="font-bold tracking-tight text-2xl"),
        Text("Manage plan tiers, track token consumption quotas, and view automated invoice history.",
             class_name="text-muted-foreground text-sm mt-1"),
        class_name="mb-6"
    )

    # Current Plan Summary Card
    current_plan_card = ShadCard(
        ShadCardHeader(
            Flex(
                VStack(
                    ShadCardTitle(f"Current Plan: {GatewayState.current_tier}"),
                    ShadCardDescription("Dedicated enterprise gateway with 24/7 SLA and custom LLM guardrails")
                ),
                HStack(
                    Heading(GatewayState.tier_price, level=3, class_name="font-extrabold text-2xl text-primary"),
                    Text(f"/{GatewayState.tier_period}", class_name="text-xs text-muted-foreground self-end mb-1")
                ),
                justify="between",
                align="start"
            )
        ),
        ShadCardContent(
            VStack(
                Flex(
                    Text("Monthly Token Consumption Quota", class_name="text-sm font-medium"),
                    Text(f"{GatewayState.token_usage_pct}% of 250M Quota Used", class_name="text-xs text-muted-foreground font-semibold"),
                    justify="between"
                ),
                ShadProgress(value=GatewayState.token_usage_pct, class_name="my-2 h-2.5"),
                Text("Plan resets in 14 days (Nov 1, 2026). Overages billed at $0.000012/token.",
                     class_name="text-xs text-muted-foreground")
            )
        ),
        class_name="mb-8 border-primary/40 shadow-md"
    )

    # 3 Tier Commercial Cards
    tier_grid = Grid(
        # Starter Tier
        ShadCard(
            ShadCardHeader(
                ShadCardTitle("Starter Plan"),
                ShadCardDescription("For prototype validation and internal research teams."),
                Heading("$99", level=3, class_name="font-bold text-2xl mt-2")
            ),
            ShadCardContent(
                VStack(
                    Text("✓ 5M Tokens / month", class_name="text-xs"),
                    Text("✓ 2 Team Seats", class_name="text-xs"),
                    Text("✓ Shared Ingress Gateway", class_name="text-xs"),
                    Text("✗ Custom Guardrails", class_name="text-xs text-muted-foreground"),
                    ShadButton(
                        "Downgrade to Starter" if GatewayState.current_tier != "Starter" else "Current Plan",
                        variant="outline" if GatewayState.current_tier != "Starter" else "secondary",
                        size="sm",
                        full_width=True,
                        on_click=GatewayState.upgrade_starter,
                        class_name="mt-4"
                    ),
                    gap="xs"
                )
            )
        ),
        # Growth Tier
        ShadCard(
            ShadCardHeader(
                ShadCardTitle("Growth Scale"),
                ShadCardDescription("For scaling applications with live multi-user traffic."),
                Heading("$499", level=3, class_name="font-bold text-2xl mt-2")
            ),
            ShadCardContent(
                VStack(
                    Text("✓ 50M Tokens / month", class_name="text-xs font-semibold"),
                    Text("✓ 10 Team Seats with RBAC", class_name="text-xs"),
                    Text("✓ Priority Model Routing", class_name="text-xs"),
                    Text("✓ Automated PII Masking", class_name="text-xs"),
                    ShadButton(
                        "Switch to Growth" if GatewayState.current_tier != "Growth" else "Current Plan",
                        variant="outline" if GatewayState.current_tier != "Growth" else "secondary",
                        size="sm",
                        full_width=True,
                        on_click=GatewayState.upgrade_growth,
                        class_name="mt-4"
                    ),
                    gap="xs"
                )
            )
        ),
        # Enterprise Scale Tier
        ShadCard(
            ShadCardHeader(
                Flex(
                    ShadCardTitle("Enterprise Scale"),
                    ShadBadge("POPULAR", variant="default", class_name="text-[10px]"),
                    justify="between"
                ),
                ShadCardDescription("For mission-critical production workloads requiring dedicated SLAs."),
                Heading("$1,499", level=3, class_name="font-bold text-2xl mt-2 text-primary")
            ),
            ShadCardContent(
                VStack(
                    Text("✓ 250M Tokens / month", class_name="text-xs font-bold text-primary"),
                    Text("✓ Unlimited RBAC Seats", class_name="text-xs"),
                    Text("✓ Dedicated Rust Cluster", class_name="text-xs"),
                    Text("✓ 99.99% Availability SLA", class_name="text-xs"),
                    ShadButton(
                        "Active Enterprise Tier" if GatewayState.current_tier == "Enterprise Scale" else "Upgrade to Enterprise",
                        variant="default" if GatewayState.current_tier == "Enterprise Scale" else "outline",
                        size="sm",
                        full_width=True,
                        on_click=GatewayState.upgrade_enterprise,
                        class_name="mt-4"
                    ),
                    gap="xs"
                )
            ),
            class_name="border-primary"
        ),
        columns=3,
        gap="md",
        class_name="mb-8"
    )

    # Invoices History Table
    invoices_card = ShadCard(
        ShadCardHeader(
            ShadCardTitle("Invoice & Billing History"),
            ShadCardDescription("Automated monthly charges billed to corporate card ending in •••• 4242.")
        ),
        ShadCardContent(
            Table(
                headers=["Invoice ID", "Billing Period", "Amount", "Payment Method", "Status", "Receipt"],
                rows=[
                    ["INV-2026-009", "Sep 1 - Sep 30, 2026", "$1,499.00", "Visa •••• 4242", ShadBadge("Paid", variant="default"), Link("PDF ⬇", href="#", underline=False, class_name="text-xs text-primary font-medium hover:underline")],
                    ["INV-2026-008", "Aug 1 - Aug 31, 2026", "$1,499.00", "Visa •••• 4242", ShadBadge("Paid", variant="default"), Link("PDF ⬇", href="#", underline=False, class_name="text-xs text-primary font-medium hover:underline")],
                    ["INV-2026-007", "Jul 1 - Jul 31, 2026", "$1,499.00", "Visa •••• 4242", ShadBadge("Paid", variant="default"), Link("PDF ⬇", href="#", underline=False, class_name="text-xs text-primary font-medium hover:underline")],
                ]
            )
        )
    )

    return commercial_shell(VStack(top_bar, current_plan_card, tier_grid, invoices_card, gap="none"), active_tab="billing")


# ==============================================================================
# 7. View: API Key Management (`/keys`)
# ==============================================================================

@app.page("/keys")
def keys_view():
    user = current_user.get()
    keys = auth.list_api_keys(user.id) if user else []

    top_bar = VStack(
        Heading("API Gateway Provisioning & Keys", level=2, class_name="font-bold tracking-tight text-2xl"),
        Text("Generate high-entropy tokens (`pdu_live_...`) to connect your CI/CD pipelines, MLOps scripts, and backend services.",
             class_name="text-muted-foreground text-sm mt-1"),
        class_name="mb-6"
    )

    manager = APIKeyManager(keys=keys)
    
    docs_snippet = ShadCard(
        ShadCardHeader(
            ShadCardTitle("Integration Quickstart"),
            ShadCardDescription("Authenticate programmatic requests using the standard Authorization header:")
        ),
        ShadCardContent(
            CodeBlock(
                code='curl -X POST https://api.aimetrics.ai/v1/chat/completions \\\n'
                     '  -H "Authorization: Bearer pdu_live_9f83a...b24e" \\\n'
                     '  -H "Content-Type: application/json" \\\n'
                     '  -d \'{"model": "claude-3-5-sonnet", "messages": [{"role": "user", "content": "Hello!"}]}\'',
                language="bash"
            )
        ),
        class_name="mt-8"
    )

    return commercial_shell(VStack(top_bar, manager, docs_snippet, gap="none"), active_tab="keys")


# ==============================================================================
# 8. View: Login Page (`/login`)
# ==============================================================================

@app.page("/login")
def login_view():
    return LoginPage(
        title="aiMetrics AI Enterprise",
        subtitle="Sign in to your high-throughput AI Observability & Gateway Portal\n\nDemo Accounts:\n• Admin: admin@ai.com / admin123\n• Developer: developer@ai.com / developer123",
        redirect_to="/"
    )


# ==============================================================================
# 9. CLI Runner
# ==============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  🚀 aiMetrics AI Enterprise Commercial Portal Running!")
    print("=" * 70)
    print("  • Public Dashboard:   http://127.0.0.1:8000/")
    print("  • Model Observatory:  http://127.0.0.1:8000/models")
    print("  • Billing Portal:     http://127.0.0.1:8000/billing")
    print("  • API Key Management: http://127.0.0.1:8000/keys")
    print("  • Interactive Docs:   http://127.0.0.1:8000/docs")
    print("  • Demo Admin Account: admin@ai.com / admin123")
    print("  • Multi-Worker Ready: SQLite WAL backend at .ai_metrics.db")
    print("=" * 70 + "\n")
    app.run(workers=2, share=True, reload=True)
