# 🌐 Community Components & JSX Guide: Build, Publish & Contribute

PyDataUI enables Python developers to build, publish, and share reusable UI components just like the **React, Angular, and Shadcn** communities—powered by **`pdu.from_jsx()`** with **zero Node.js, zero npm, and zero build toolchains**.

---

## 1. The Vision: Growing a Thriving Component Ecosystem

React and modern frontend frameworks exploded in adoption because developers could install, copy, and share thousands of open-source UI blocks from npm. 

Today, the largest component registries in the world (**Shadcn UI**, **Tailwind UI**, **v0.dev**, **Magic UI**) author components in **JSX / Tailwind format**.

With **`pdu.from_jsx()`**, PyDataUI bridges this ecosystem directly into Python:
- Copy any JSX snippet directly from Shadcn or v0.
- Transpile it on the server into a native hypermedia component factory.
- Bind `{props}` to Python arguments and `onClick` events to Python server actions.
- Package and publish your components to PyPI or GitHub for other developers to use.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        HOW pdu.from_jsx() WORKS                        │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Raw React / Shadcn JSX Snippet (from v0.dev, Shadcn UI, or GitHub)  │
│    <Card className="p-6 bg-card">                                      │
│      <Badge variant="outline">{status}</Badge>                         │
│      <h3 className="text-xl font-bold">{title}</h3>                    │
│      <Button onClick={on_deploy}>Deploy Pod</Button>                   │
│    </Card>                                                             │
├────────────────────────────────────────────────────────────────────────┤
│                                  │ (Pure Python AST Parser & Transpiler)
│                                  ▼                                     │
│ 2. Native PyDataUI Component Tree (FastHTML + HTMX DOM Morphing)       │
│    • className automatically mapped to Tailwind utility class          │
│    • Dynamic {props} bound to Python arguments                         │
│    • onClick={fn} automatically mapped to server action                │
│    • Zero Node.js / Zero npm compile process                           │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Authoring a Component with `pdu.from_jsx()`

`pdu.from_jsx()` compiles raw JSX or HTML into a callable Python component factory in a single line:

```python
import pydataui as pdu

# 1. Create a component factory from raw JSX
MetricCard = pdu.from_jsx("""
<div className="relative overflow-hidden rounded-xl border border-border bg-card p-6 shadow-sm hover:shadow-md transition">
    <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{title}</span>
        <span className="rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-medium text-emerald-500 border border-emerald-500/20">
            {badge}
        </span>
    </div>
    <div className="mt-3 flex items-baseline gap-2">
        <span className="text-3xl font-extrabold tracking-tight text-card-foreground">{value}</span>
        <span className="text-xs font-semibold text-emerald-500">{delta}</span>
    </div>
    <p className="mt-2 text-xs text-muted-foreground">{caption}</p>
</div>
""")

# 2. Use it in procedural Track 1 or declarative Track 2:
with pdu.grid(columns=3, gap=4):
    pdu.write(MetricCard(title="Active GPU Nodes", value="16 / 16", delta="+2 nodes", badge="Healthy", caption="SXM5 H100 Cluster"))
    pdu.write(MetricCard(title="P99 Inference Latency", value="12.4ms", delta="-1.8ms", badge="Optimal", caption="Measured over 50k reqs"))
    pdu.write(MetricCard(title="Token Throughput", value="8.4k t/s", delta="+14.2%", badge="Streaming", caption="Real-time telemetry"))

if __name__ == "__main__":
    pdu.run(port=8000)
```

---

## 3. Interactive Callbacks: Binding JSX to Python Actions

`pdu.from_jsx` seamlessly binds React-style `onClick`, `onChange`, and `onSubmit` attributes directly to Python server functions:

```python
import pydataui as pdu

s = pdu.state(counter=0)

@s.action
def increment():
    s.counter += 1

# JSX button wired directly to Python server action
InteractiveCounter = pdu.from_jsx("""
<div className="flex items-center gap-4 p-4 border rounded-lg bg-card">
    <span className="text-lg font-bold">Count: {count}</span>
    <button onClick={on_click} className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium">
        Increment +1
    </button>
</div>
""")

pdu.write(InteractiveCounter(count=s.counter, on_click=increment))
```

---

## 4. How to Build & Publish Your Own Component Library

You can build a standalone component library in your own GitHub repository and publish it to PyPI so any PyDataUI user can install it.

### Step 1: Package Structure
```text
pydataui_awesome_cards/
├── pyproject.toml
├── README.md
└── pydataui_awesome_cards/
    ├── __init__.py
    └── components.py
```

### Step 2: Implement Your Components (`components.py`)
```python
import pydataui as pdu

SpotlightCard = pdu.from_jsx("""
<div className="group relative rounded-2xl border border-border bg-card p-6 shadow-sm hover:border-primary/50 transition duration-300">
  <div className="flex items-center justify-between">
    <h3 className="text-lg font-semibold text-card-foreground">{title}</h3>
    <span className="text-xs text-muted-foreground">{category}</span>
  </div>
  <p className="mt-2 text-sm text-muted-foreground">{description}</p>
</div>
""")

AgentThoughtBox = pdu.from_jsx("""
<div className="rounded-lg border border-purple-500/20 bg-purple-500/5 p-4 font-mono text-xs">
  <div className="flex items-center gap-2 text-purple-400 font-semibold mb-2">
    <span>🧠 Agent Reasoning</span>
    <span className="animate-pulse">●</span>
  </div>
  <p className="text-foreground/90">{thought}</p>
</div>
""")
```

### Step 3: Export in `__init__.py`
```python
from .components import SpotlightCard, AgentThoughtBox

__all__ = ["SpotlightCard", "AgentThoughtBox"]
```

### Step 4: Publish to PyPI
```bash
python -m build
twine upload dist/*
```

Now any developer in the world can install and use your components:
```bash
pip install pydataui pydataui_awesome_cards
```
```python
import pydataui as pdu
from pydataui_awesome_cards import SpotlightCard

pdu.write(SpotlightCard(title="Autonomous Agent", category="AI Ops", description="Running inference pipeline"))
```

---

## 5. Submit Your Components to the Official Showcase

Have you published a PyDataUI component package or template repository on GitHub?

1. Open an issue or Pull Request on [github.com/rajboopathiking/pydataui](https://github.com/rajboopathiking/pydataui).
2. Add your repository and package link to the **Community Components Registry**.
3. We will feature your component in the official PyDataUI Component Showcase!
