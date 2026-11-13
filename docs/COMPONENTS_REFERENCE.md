# PyDataUI Complete Component Reference

Welcome to the comprehensive, production-grade component catalog for **PyDataUI**. This reference documents every component in the framework with its import statement, constructor signature, parameters table, reactive state binding guidelines, and runnable code examples.

---

## Table of Contents

1. [Component Architecture & Base](#component-architecture-base)
2. [Layout Primitives](#layout-primitives)
    - [Container](#container)
    - [Row](#row)
    - [Col](#col)
    - [Grid](#grid)
    - [Card](#card)
    - [Box](#box)
    - [Flex](#flex)
    - [Stack](#stack)
    - [HStack](#hstack)
    - [VStack](#vstack)
    - [Spacer](#spacer)
    - [Divider](#divider)
    - [Center](#center)
    - [Wrap](#wrap)
3. [Typography](#typography)
    - [Heading](#heading)
    - [Text](#text)
    - [Paragraph](#paragraph)
    - [Link](#link)
    - [Code](#code)
    - [Blockquote](#blockquote)
    - [Label](#label)
4. [Forms & Input Controls](#forms-input-controls)
    - [Button](#button)
    - [Input](#input)
    - [TextArea](#textarea)
    - [Select](#select)
    - [Checkbox](#checkbox)
    - [Radio](#radio)
    - [RadioGroup](#radiogroup)
    - [Switch](#switch)
    - [Slider](#slider)
    - [FileUpload](#fileupload)
    - [Form](#form)
    - [ShadForm (Pydantic Auto-Form)](#shadform)
5. [Data Display & Tabular Visualization](#data-display-tabular-visualization)
    - [DataTable (Universal Sniffing)](#datatable)
    - [Table](#table)
    - [Badge](#badge)
    - [Tag](#tag)
    - [Stat](#stat)
    - [KeyValue](#keyvalue)
    - [Avatar](#avatar)
    - [Tooltip](#tooltip)
    - [List & ListItem](#list-listitem)
    - [DescriptionList](#descriptionlist)
6. [Advanced AI & Developer Tools](#advanced-ai-developer-tools)
    - [Chat (Commercial AI Chatbot)](#chat)
    - [Markdown](#markdown)
    - [CodeEditor](#codeeditor)
7. [Feedback & Indicators](#feedback-indicators)
    - [Alert](#alert)
    - [Progress](#progress)
    - [Spinner](#spinner)
    - [Skeleton](#skeleton)
    - [Toast](#toast)
    - [Empty](#empty)
8. [Navigation & Shell Architecture](#navigation-shell-architecture)
    - [DashboardLayout](#dashboardlayout)
    - [Sidebar](#sidebar)
    - [Header](#header)
    - [Navbar](#navbar)
    - [NavLink](#navlink)
    - [Breadcrumb](#breadcrumb)
    - [Tabs & Tab](#tabs-tab)
    - [Pagination](#pagination)
    - [Menu](#menu)
9. [Overlays & Dialogs](#overlays-dialogs)
    - [Modal](#modal)
    - [Drawer](#drawer)
    - [Popover](#popover)
    - [Dropdown](#dropdown)
10. [Media & Charts](#media-charts)
    - [BarChart](#barchart)
    - [LineChart](#linechart)
    - [PieChart & DoughnutChart](#piechart-doughnutchart)
    - [Sparkline](#sparkline)
    - [PlotlyChart](#plotlychart)
    - [Image, Video, Audio, Icon](#image-video-audio-icon)
11. [Data Science & ML Engineering Components](#data-science-ml-engineering-components)
    - [MetricCard](#metriccard)
    - [DataFrameTable](#dataframetable)
    - [ModelMetrics](#modelmetrics)
    - [PipelineStatus](#pipelinestatus)
    - [ConfusionMatrix](#confusionmatrix)
    - [JSONViewer](#jsonviewer)
    - [CodeBlock](#codeblock)
    - [FileDownload & DataUpload](#filedownload-dataupload)
    - [SQLEditor](#sqleditor)
    - [FeatureImportance & SchemaViewer](#featureimportance-schemaviewer)
12. [Shadcn Enterprise Suite](#shadcn-enterprise-suite)
    - [ShadButton](#shadbutton)
    - [ShadCard](#shadcard)
    - [ShadInput](#shadinput)
    - [ShadBadge](#shadbadge)
    - [ShadAlert](#shadalert)
    - [ShadProgress](#shadprogress)
    - [ShadTabs](#shadtabs)
    - [ShadDialog](#shaddialog)
    - [ShadCommandPalette](#shadcommandpalette)
    - [ShadDatePicker](#shaddatepicker)

---

## Component Architecture & Base

All visual components inherit from `Component` (`pydataui.components.base.Component`).

### Universal Constructor Options
Every component accepts the following standard base parameters:

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `id` | `Optional[str]` | `None` | HTML element identifier (auto-generated if omitted). |
| `class_name` | `Optional[str]` | `None` | Additional CSS class names or Tailwind utility classes. |
| `style` | `Optional[Union[str, dict]]` | `None` | Inline styles as CSS string or dictionary of property-value pairs. |
| `hidden` | `bool` | `False` | When `True`, suppresses rendering completely. |
| `**props` | `Any` | `{}` | Additional HTML attributes (`data-*`, `aria-*`, `title`, etc.). |

---

## Layout Primitives

### Container
A centered, responsive content wrapper that limits content width and adds horizontal padding.

```python
from pydataui import Container, Heading, Text

Container(
    Heading("Operations Center", level=1),
    Text("Manage cluster nodes and model deployments."),
    max_width="xl",
    padding="lg",
    center=True
)
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `*children` | `Children` | `()` | Child components or text strings. |
| `max_width` | `str` | `'lg'` | Max width constraint: `'sm'`, `'md'`, `'lg'`, `'xl'`, `'2xl'`, `'full'`. |
| `padding` | `str` | `'md'` | Padding token: `'none'`, `'sm'`, `'md'`, `'lg'`, `'xl'`. |
| `center` | `bool` | `True` | Center horizontally using auto margins. |

---

### Row
A horizontal flex container shorthand with intuitive gap, alignment, and wrapping controls.

```python
from pydataui import Row, Button, Badge

Row(
    Button("Scale Cluster", variant="primary"),
    Button("Flush Cache", variant="outline"),
    Badge("Running (8 nodes)", variant="success"),
    gap="4",
    align="center",
    justify="between",
    wrap=True
)
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `*children` | `Children` | `()` | Elements arranged in a horizontal row. |
| `gap` | `Union[str, int]` | `'4'` | Spacing between items (`'4'` = 1rem, or CSS size). |
| `align` | `str` | `'center'` | Vertical alignment: `'start'`, `'center'`, `'end'`, `'stretch'`. |
| `justify` | `str` | `'start'` | Horizontal distribution: `'start'`, `'center'`, `'end'`, `'between'`, `'around'`. |
| `wrap` | `bool` | `False` | Whether children wrap onto multiple lines. |

---

### Col
A vertical flex column shorthand with 12-column grid span or fractional width support.

```python
from pydataui import Col, Card, Text

Col(
    Card(title="Worker 01", children=[Text("Status: Healthy")]),
    span=6,
    gap="4"
)
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `*children` | `Children` | `()` | Elements arranged vertically. |
| `span` | `Optional[int]` | `None` | Grid column span from 1 to 12 (`span=6` is 50% width). |
| `width` | `Optional[str]` | `None` | Fractional width (`'1/2'`, `'1/3'`, `'full'`) or CSS measurement. |
| `gap` | `Union[str, int]` | `'4'` | Spacing between child elements. |
| `align` | `str` | `'stretch'` | Cross-axis item alignment. |
| `justify` | `str` | `'start'` | Main-axis item alignment. |

---

### Grid
CSS Grid container for structured multi-column dashboards.

```python
from pydataui import Grid, Card, Text

Grid(
    Card(title="Node A", children=[Text("Load: 45%")]),
    Card(title="Node B", children=[Text("Load: 62%")]),
    Card(title="Node C", children=[Text("Load: 31%")]),
    columns=3,
    gap="6"
)
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `*children` | `Children` | `()` | Grid items. |
| `columns` | `Union[int, str]` | `1` | Number of columns (`1`, `2`, `3`, `4`, etc.). |
| `gap` | `Union[str, int]` | `'md'` | Spacing between grid cells. |
| `template_columns`| `Optional[str]` | `None` | Custom CSS `grid-template-columns` override. |
| `template_rows` | `Optional[str]` | `None` | Custom CSS `grid-template-rows` override. |

---

### Card
Elevated card container with header, title, subtitle, and body.

```python
from pydataui import Card, Text, Button

Card(
    Text("Memory allocation: 14.2 GB / 32 GB"),
    Button("Manage", variant="secondary"),
    title="Memory Utilization",
    subtitle="Cluster Node Alpha",
    padding="lg",
    shadow="sm",
    radius="lg",
    bordered=True
)
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `*children` | `Children` | `()` | Card body content. |
| `title` | `Optional[str]` | `None` | Card header title text. |
| `subtitle` | `Optional[str]` | `None` | Secondary subtitle under header title. |
| `padding` | `str` | `'lg'` | Padding token: `'none'`, `'sm'`, `'md'`, `'lg'`, `'xl'`. |
| `shadow` | `str` | `'md'` | Box shadow: `'none'`, `'sm'`, `'md'`, `'lg'`. |
| `radius` | `str` | `'md'` | Border radius: `'none'`, `'sm'`, `'md'`, `'lg'`, `'full'`. |
| `bordered` | `bool` | `True` | Whether to display a border line. |

---

### Box
Generic HTML `<div>` container for custom CSS and structural grouping.

```python
from pydataui import Box, Text

Box(
    Text("Raw container block"),
    class_name="bg-muted p-4 rounded-lg"
)
```

---

### Flex
Low-level CSS Flexbox container with full directional and distribution properties.

```python
from pydataui.components import Flex, Text

Flex(
    Text("Left"), Text("Right"),
    direction="row",
    justify="space-between",
    align="center",
    gap="md"
)
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `direction` | `str` | `'row'` | `'row'`, `'column'`, `'row-reverse'`, `'column-reverse'`. |
| `align` | `str` | `'stretch'` | `'start'`, `'center'`, `'end'`, `'stretch'`, `'baseline'`. |
| `justify` | `str` | `'start'` | `'start'`, `'center'`, `'end'`, `'space-between'`, `'space-around'`. |
| `gap` | `str` | `'md'` | Gap token or spacing measurement. |
| `wrap` | `str` | `'nowrap'` | `'nowrap'`, `'wrap'`, `'wrap-reverse'`. |

---

### Stack
Base class for directional stacked flex items.

```python
from pydataui.components import Stack, Text

Stack(Text("Item 1"), Text("Item 2"), gap="sm")
```

---

### HStack
Horizontal layout stack (Flex with `direction="row"`).

```python
from pydataui import HStack, Badge, Text

HStack(
    Badge("Status: Normal"),
    Text("All health checks passing."),
    gap="md",
    align="center"
)
```

---

### VStack
Vertical layout stack (Flex with `direction="column"`).

```python
from pydataui import VStack, Heading, Text

VStack(
    Heading("Model Performance", level=2),
    Text("Evaluation conducted against 10,000 holdout records."),
    gap="sm"
)
```

---

### Spacer
Auto-expanding flexible spacer that pushes sibling items apart.

```python
from pydataui import Row, Heading, Button, Spacer

Row(
    Heading("Fleet Management", level=3),
    Spacer(),  # Pushes button to far right edge
    Button("New Server", variant="primary")
)
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `size` | `Optional[Any]` | `None` | Fixed width/height in px. If `None`, acts as auto-expanding `flex: 1 1 auto`. |
| `flex` | `int` | `1` | Flex-grow factor when size is omitted. |

---

### Divider
Horizontal or vertical divider line.

```python
from pydataui import Divider

Divider(orientation="horizontal")
Divider(orientation="vertical")
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `orientation` | `str` | `'horizontal'` | `'horizontal'` or `'vertical'`. |
| `color` | `Optional[str]` | `None` | CSS border color override. |
| `thickness` | `Optional[str]` | `None` | Line thickness (e.g. `'2px'`). |

---

### Center
Centers children both horizontally and vertically.

```python
from pydataui.components import Center, Spinner

Center(Spinner(size="lg"), style="height: 300px;")
```

---

### Wrap
Flexbox container with automatic line wrapping.

```python
from pydataui.components import Wrap, Tag

Wrap(
    Tag("Python"), Tag("DuckDB"), Tag("Polars"), Tag("FastAPI"), Tag("Rust"),
    gap="sm"
)
```

---

## Typography

### Heading
Semantic heading tag (`<h1>` to `<h6>`) with scaled font weights and sizes.

```python
from pydataui import Heading

Heading("Enterprise Fleet Telemetry", level=1)
Heading("Active Workers", level=2)
Heading("Latency Breakdown", level=3)
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `*children` | `Children` | `()` | Heading text or inline elements. |
| `level` | `int` | `1` | Heading level: `1` (`<h1>`) through `6` (`<h6>`). |

---

### Text
General-purpose inline or block text with size and semantic styling variants.

```python
from pydataui import Text

Text("Standard body copy.")
Text("Secondary muted details", variant="muted", size="sm")
Text("Warning: quota threshold near capacity", color="danger", weight="semibold")
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `*children` | `Children` | `()` | Text string. |
| `size` | `str` | `'md'` | Font size: `'xs'`, `'sm'`, `'md'`, `'lg'`, `'xl'`, `'2xl'`. |
| `variant` | `str` | `'default'` | `'default'`, `'muted'`, `'primary'`, `'secondary'`. |
| `weight` | `str` | `'normal'` | `'normal'`, `'medium'`, `'semibold'`, `'bold'`. |
| `color` | `Optional[str]` | `None` | Color accent: `'success'`, `'danger'`, `'warning'`, `'info'`. |

---

### Paragraph
Text paragraph `<p>` with comfortable line spacing and bottom margin.

```python
from pydataui import Paragraph

Paragraph("PyDataUI compiles declarative Python layouts into lightning-fast server-side HTML responses.")
```

---

### Link
Hyperlink anchor tag `<a>` with internal route and external URL support.

```python
from pydataui.components import Link

Link("Documentation", href="/docs", external=False)
Link("GitHub", href="https://github.com/rajboopathiking/pydataui", external=True)
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `*children` | `Children` | `()` | Link text or inner component. |
| `href` | `str` | `'#'` | Target URL or page route. |
| `external` | `bool` | `False` | Opens in new tab with `target="_blank"` and `rel="noopener"`. |

---

### Code
Monospace code display for inline snippets or multi-line blocks.

```python
from pydataui.components import Code

Code("pip install pydataui", inline=True)
Code("pydataui run app.py --workers 4", inline=False)
```

---

### Blockquote
Styled quotation block with citation.

```python
from pydataui.components import Blockquote

Blockquote("Speed is a feature, not an afterthought.", cite="Architecture Lead")
```

---

### Label
Accessible form field label.

```python
from pydataui.components import Label

Label("API Secret Key", for_id="key-input")
```

---

## Forms & Input Controls

### Button
Interactive button trigger with semantic variants, loading indicators, and HTMX action dispatch.

```python
from pydataui import Button, state

s = state(count=0)

@s.action
def on_increment():
    s.count += 1

Button(
    "Increment Count",
    on_click=on_increment,
    variant="primary",
    size="md",
    loading=False,
    full_width=False
)
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `*children` | `Children` | `()` | Button label or inner icon. |
| `variant` | `str` | `'primary'` | `'primary'`, `'secondary'`, `'outline'`, `'ghost'`, `'danger'`. |
| `size` | `str` | `'md'` | Size token: `'sm'`, `'md'`, `'lg'`. |
| `on_click` | `Optional[Callable]`| `None` | Python function or `@s.action` executed on click. |
| `disabled` | `bool` | `False` | Disables interaction when `True`. |
| `loading` | `bool` | `False` | Shows loading spinner and prevents clicking. |
| `full_width` | `bool` | `False` | Stretches button across container width. |

---

### Input
Single-line text input with label, placeholder, error message, and two-way state binding.

```python
from pydataui import Input, state

s = state(search_query="")

@s.action
def on_search(value: str = "", **kwargs):
    s.search_query = value or kwargs.get("search_query", "")

Input(
    label="Search Fleet",
    placeholder="Filter by node name or IP...",
    bind=s.search_query,
    on_change=on_search,
    required=True
)
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `label` | `Optional[str]` | `None` | Accessible label placed above input. |
| `placeholder` | `str` | `""` | Ghost prompt text. |
| `bind` | `Optional[StateVar]` | `None` | Two-way reactive binding to state variable. |
| `value` | `Optional[Any]` | `None` | Value override. |
| `name` | `Optional[str]` | `None` | Form POST parameter name. |
| `type` | `str` | `'text'` | Input type: `'text'`, `'password'`, `'email'`, `'number'`, etc. |
| `on_change` | `Optional[Callable]`| `None` | Triggered on blur or Enter key with current value. |
| `on_input` | `Optional[Callable]` | `None` | Triggered with 300ms debounce as user types. |
| `error` | `Optional[str]` | `None` | Error text rendered in red with alert border. |
| `helper_text` | `Optional[str]`| `None` | Small instructional text rendered below. |
| `disabled` | `bool` | `False` | Disables input. |

---

### TextArea
Multiline text entry with auto-expansion support.

```python
from pydataui import TextArea, state

s = state(notes="")

TextArea(
    label="Incident Notes",
    placeholder="Describe operational event...",
    rows=4,
    bind=s.notes
)
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `label` | `Optional[str]` | `None` | Field label. |
| `placeholder` | `str` | `""` | Ghost prompt text. |
| `rows` | `int` | `3` | Visible text row height. |
| `bind` | `Optional[StateVar]` | `None` | Two-way state binding. |

---

### Select
HTML dropdown selector for choosing from a list of options.

```python
from pydataui import Select

Select(
    options=[
        {"value": "us-east-1", "label": "US East (N. Virginia)"},
        {"value": "eu-central-1", "label": "EU Central (Frankfurt)"},
        {"value": "ap-southeast-1", "label": "Asia Pacific (Singapore)"}
    ],
    label="Target Deployment Region",
    value="us-east-1"
)
```

---

### Checkbox
Boolean checkbox control with label.

```python
from pydataui import Checkbox

Checkbox("Enable verbose debug logging", checked=True)
```

---

### Radio
Single radio button option.

```python
from pydataui.components import Radio

Radio("Option A", name="group1", value="a", checked=True)
```

---

### RadioGroup
Group of mutually exclusive radio options.

```python
from pydataui.components import RadioGroup

RadioGroup(
    options=[
        {"value": "small", "label": "2 vCPU / 4GB RAM"},
        {"value": "medium", "label": "4 vCPU / 8GB RAM"},
        {"value": "large", "label": "8 vCPU / 16GB RAM"}
    ],
    value="medium",
    label="Cluster Node Size"
)
```

---

### Switch
Toggle switch slider for boolean feature flags.

```python
from pydataui import Switch

Switch("Maintenance Mode", checked=False)
```

---

### Slider
Numeric range slider control.

```python
from pydataui.components import Slider

Slider(min=0, max=100, step=5, value=75, label="CPU Allocation (%)")
```

---

### FileUpload
File selection input for uploads.

```python
from pydataui.components import FileUpload

FileUpload(label="Upload Dataset (CSV/Parquet)", accept=".csv,.parquet")
```

---

### Form
HTML `<form>` wrapper that groups inputs and handles submission.

```python
from pydataui import Form, Input, Button, state

s = state()

@s.action
def on_submit(form_data: dict = None, **kwargs):
    print("Form data received:", form_data)

Form(
    Input(name="email", label="Email", required=True),
    Input(name="password", label="Password", type="password", required=True),
    Button("Sign In", type="submit"),
    on_submit=on_submit
)
```

---

### ShadForm
Pydantic auto-form generator that transforms any Pydantic model into a complete, validated enterprise form.

```python
from pydantic import BaseModel, Field
from pydataui import ShadForm, state

class WorkerConfig(BaseModel):
    worker_name: str = Field(..., description="Unique worker node identifier")
    max_concurrency: int = Field(8, ge=1, le=64, description="Simultaneous tasks")
    auto_restart: bool = Field(True, description="Restart automatically on failure")

s = state()

@s.action
def save_worker(form_data: dict = None, **kwargs):
    # Validated payload
    print("New worker created:", form_data)

ShadForm.from_pydantic(
    WorkerConfig,
    on_submit=save_worker,
    submit_label="Provision Worker"
)
```

---

## Data Display & Tabular Visualization

### DataTable
Universal tabular component that automatically sniffs, normalizes, sorts, filters, and paginates datasets.

Supports:
- **Pandas DataFrames** (`pandas.DataFrame`)
- **Polars DataFrames** (`polars.DataFrame`)
- **DuckDB Relations** (`duckdb.PyRelation`)
- **PyArrow Tables** (`pyarrow.Table`)
- **Pydantic Model Lists** (`list[BaseModel]`)
- **Dictionaries** (`list[dict]`)

```python
import duckdb
from pydataui import DataTable

rel = duckdb.sql("SELECT 'Worker-01' as node, 88.5 as cpu, 99.9 as uptime UNION SELECT 'Worker-02', 42.1, 100.0")

DataTable(
    data=rel,
    searchable=True,
    paginated=True,
    page_size=10,
    bordered=True
)
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `data` | `Any` | `None` | Dataset object (Polars, Pandas, DuckDB, Arrow, or dicts). |
| `columns` | `Optional[List[str]]` | `None` | Columns to display (auto-detected if omitted). |
| `searchable` | `bool` | `True` | Search filtering input box above table. |
| `paginated` | `bool` | `True` | Page navigation controls. |
| `page_size` | `int` | `10` | Number of rows per page. |
| `sortable` | `bool` | `True` | Clickable column header sorting. |
| `bordered` | `bool` | `True` | Table borders. |

---

### Table
Low-level HTML table container.

```python
from pydataui.components import Table

Table(headers=["Cluster", "Nodes", "Status"], rows=[["us-east", "12", "ACTIVE"], ["eu-west", "8", "ACTIVE"]])
```

---

### Badge
Status indicator pill with semantic variants.

```python
from pydataui import Badge

Badge("Online", variant="success")
Badge("Critical Error", variant="danger")
Badge("Staging", variant="secondary")
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `*children` | `Children` | `()` | Badge label text. |
| `variant` | `str` | `'default'` | `'default'`, `'primary'`, `'secondary'`, `'success'`, `'warning'`, `'danger'`. |

---

### Tag
Categorization pill tag.

```python
from pydataui.components import Tag

Tag("FastAPI", color="emerald")
Tag("Python 3.12", color="blue")
```

---

### Stat
KPI scorecard block with value, trend, and subtitle.

```python
from pydataui.components import Stat

Stat(
    title="Throughput",
    value="1,420 req/s",
    change="+14.2%",
    trend="up",
    help_text="vs. 1 hour ago"
)
```

---

### KeyValue
Aligned metadata key-value row.

```python
from pydataui.components import KeyValue

KeyValue("Cluster ID", "clst_994827104")
KeyValue("API Host", "api.internal:8000")
```

---

### Avatar
User profile picture or initials circle.

```python
from pydataui.components import Avatar

Avatar(name="Alex Miller", size="md")
Avatar(src="https://images.unsplash.com/photo-1534528741775-53994a69daeb", size="lg")
```

---

### Tooltip
Hover tooltip popover.

```python
from pydataui.components import Tooltip, Button

Tooltip(
    Button("Terminate", variant="danger"),
    content="This will permanently delete the server instance."
)
```

---

### List & ListItem
Ordered or unordered list container and items.

```python
from pydataui.components import List, ListItem

List(
    ListItem("Ingest data stream"),
    ListItem("Execute tokenization pipeline"),
    ListItem("Save checkpoint to S3"),
    ordered=True
)
```

---

### DescriptionList
Two-column definition / description list.

```python
from pydataui.components import DescriptionList

DescriptionList(
    items=[
        {"term": "Operating System", "description": "Linux (Debian 12)"},
        {"term": "Python Version", "description": "3.12.7"},
        {"term": "Compiled Core", "description": "FastAPI + Rust"}
    ]
)
```

---

## Advanced AI & Developer Tools

### Chat
Commercial-grade AI chatbot component. Features:
- **IME-Safe Multiline Textarea**: Auto-expanding with `Shift+Enter` for newlines and `Enter` to submit.
- **Suggestion Chips**: Clickable prompt pills (`suggestions=[...]`) that auto-fill and submit.
- **Pulsing Typing Indicators**: 3-dot animation (`animate-bounce`) and submit button spinner during pending requests.
- **Auto-Scroll to Bottom**: Smoothly keeps the newest messages in view on render and updates.
- **Markdown & Code Rendering**: Assistant responses are parsed with syntax highlighting and copy button.
- **Dual Mode (Web & TUI)**: Runs in browser and in terminal with suggestion indices (`1`, `2`) and single-key `q` exit.

```python
import httpx
from pydataui import Chat, state

s = state(
    messages=[{"role": "assistant", "content": "How can I assist your team today?"}],
    session_id="chat_01",
    loading=False
)

@s.action
async def handle_message(message: str = "", **kwargs):
    user_msg = (message or kwargs.get("message", "")).strip()
    if not user_msg:
        return

    s.messages.append({"role": "user", "content": user_msg})
    s.loading = True

    try:
        async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=60.0) as client:
            res = await client.post("/chat/invoke", json={"id": s.session_id, "message": user_msg})
            reply = res.json().get("response", "No response")
    except Exception as e:
        reply = f"Error: {e}"
    finally:
        s.loading = False

    s.messages.append({"role": "assistant", "content": reply})

@s.action
def clear_history():
    s.messages = [{"role": "assistant", "content": "History cleared. How can I help?"}]

Chat(
    messages=s.messages,
    title="Customer Support AI",
    subtitle="SLM Agent • Llama-3-8B • Context 8k",
    placeholder="Type your message... (Shift+Enter for newline)",
    on_send=handle_message,
    on_clear=clear_history,
    suggestions=[
        "How do I reset my API key?",
        "Show cluster telemetry",
        "Explain rate limit policies"
    ],
    loading=s.loading,
    height="650px",
    show_clear=True
)
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `messages` | `List[Dict[str, Any]]` | `[]` | Message list: `[{"role": "user"\|"assistant", "content": "...", "timestamp": "..."}]`. |
| `title` | `str` | `'Agent Chat'` | Header title. |
| `subtitle` | `Optional[str]` | `None` | Model subtitle / cluster status in header. |
| `placeholder` | `str` | `'Type your message...'` | Input placeholder text. |
| `on_send` | `Callable` | `None` | Async or sync function triggered when user submits a message. |
| `on_clear` | `Callable` | `None` | Function triggered when trash / clear button is clicked. |
| `suggestions` | `List[str]` | `[]` | Clickable suggestion prompt pills rendered above input. |
| `loading` | `Union[bool, StateVar]`| `None` | Triggers animated typing bubble and button spinner during API calls. |
| `height` | `str` | `'600px'` | Fixed container height with scrollable message container. |
| `show_clear` | `bool` | `True` | Displays trash icon in chat header. |
| `user_avatar` | `Optional[str]` | `None` | Image URL for user avatar. |
| `assistant_avatar` | `Optional[str]` | `None` | Image URL for AI assistant avatar. |
| `enable_markdown` | `bool` | `True` | Parses assistant messages as markdown with code syntax highlighting. |

---

### Markdown
Parses and renders GitHub Flavored Markdown with fenced code blocks and tables.

```python
from pydataui import Markdown

Markdown("""
### Production Architecture
- **Web Engine**: Compiled FastAPI / Rust Core
- **Database**: DuckDB + PostgreSQL
""")
```

---

### CodeEditor
Interactive syntax-highlighted code editor.

```python
from pydataui import CodeEditor

CodeEditor(
    value="def health_check():\n    return {'status': 'healthy'}",
    language="python",
    height="300px"
)
```

---

## Feedback & Indicators

### Alert
Notice callout box with icon and semantic styling.

```python
from pydataui import Alert

Alert("Database migrations completed successfully.", variant="success", title="Migration Success")
Alert("Disk utilization exceeds 90%.", variant="warning", title="Storage Warning")
Alert("Authentication expired.", variant="danger")
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `*children` | `Children` | `()` | Alert body message. |
| `title` | `Optional[str]` | `None` | Bold header title in banner. |
| `variant` | `str` | `'info'` | `'info'`, `'success'`, `'warning'`, `'danger'`. |
| `dismissible` | `bool` | `False` | Displays close `[x]` button. |

---

### Progress
Task progress bar indicator.

```python
from pydataui.components import Progress

Progress(value=75, max=100, variant="primary")
```

---

### Spinner
Animated CSS loading spinner.

```python
from pydataui.components import Spinner

Spinner(size="lg", variant="primary")
```

---

### Skeleton
Content loading placeholder skeleton.

```python
from pydataui.components import Skeleton

Skeleton(height="24px", width="280px")
```

---

### Toast
Transient toast notification banner.

```python
from pydataui.components import Toast

Toast("API key generated successfully.", variant="success")
```

---

### Empty
Empty state placeholder graphic and text for empty tables and search results.

```python
from pydataui.components import Empty, Button

Empty(
    title="No Deployments Found",
    description="Get started by deploying your first model instance.",
    action=Button("Create Deployment", variant="primary")
)
```

---

## Navigation & Shell Architecture

### DashboardLayout
Enterprise application shell with collapsible sidebar navigation, top header, and fluid content area.

```python
from pydataui import DashboardLayout, Sidebar, Header, NavGroup, NavItem, Card, Text

DashboardLayout(
    sidebar=Sidebar(
        NavGroup(
            "Fleet",
            NavItem("Overview", href="/", icon="home", active=True),
            NavItem("Nodes", href="/nodes", icon="server"),
            NavItem("Settings", href="/settings", icon="settings")
        ),
        title="PyDataUI Cloud"
    ),
    header=Header(title="Operations Center", subtitle="Production Cluster"),
    children=[
        Card(title="Node Summary", children=[Text("All 8 nodes healthy.")])
    ]
)
```

---

### Sidebar
Sidebar container for navigation groups and items.

```python
from pydataui.components.navigation import Sidebar, NavLink

Sidebar(
    NavLink("Dashboard", href="/"),
    NavLink("Models", href="/models"),
    title="Navigation"
)
```

---

### Header
Top app bar with title and action controls.

```python
from pydataui.shadcn import Header

Header(title="Operations Center", subtitle="Cluster us-east-1")
```

---

### Navbar
Horizontal navigation bar.

```python
from pydataui.components import Navbar, NavLink

Navbar(
    brand="PyDataUI Enterprise",
    links=[NavLink("Home", href="/"), NavLink("Docs", href="/docs")]
)
```

---

### NavLink
Individual navigation link item.

```python
from pydataui.components.navigation import NavLink

NavLink("Dashboard", href="/dashboard", active=True)
```

---

### Breadcrumb
Hierarchical location navigation trail.

```python
from pydataui.components import Breadcrumb

Breadcrumb(
    items=[
        {"label": "Home", "href": "/"},
        {"label": "Clusters", "href": "/clusters"},
        {"label": "Alpha-01", "href": None}
    ]
)
```

---

### Tabs & Tab
Panel switcher that toggles active views without refreshing the page.

```python
from pydataui import Tabs, Tab, Text

Tabs(
    Tab("Overview", Text("High-level system metrics.")),
    Tab("Configuration", Text("Cluster environment variables.")),
    Tab("Audit Logs", Text("Security events and access records.")),
    default_tab="Overview"
)
```

---

### Pagination
Page navigation control strip.

```python
from pydataui.components import Pagination

Pagination(current_page=2, total_pages=10, on_page_change=None)
```

---

### Menu
Vertical or dropdown menu container.

```python
from pydataui.components.navigation import Menu

Menu(items=[{"label": "Account", "href": "/account"}, {"label": "Sign Out", "href": "/logout"}])
```

---

## Overlays & Dialogs

### Modal
Accessible dialog overlay that focuses the user on a specific action.

```python
from pydataui import Modal, Button, Text

Modal(
    Text("Are you sure you want to restart this cluster node?"),
    title="Confirm Restart",
    trigger=Button("Restart Node", variant="danger"),
    action_button=Button("Yes, Restart", variant="danger")
)
```

---

### Drawer
Sliding side sheet overlay.

```python
from pydataui import Drawer, Text

Drawer(
    Text("Detailed hardware telemetry and memory profiles."),
    title="Node Diagnostics",
    side="right"
)
```

---

### Popover
Positioned overlay anchored to a trigger element.

```python
from pydataui.components import Popover, Button, Text

Popover(
    trigger=Button("View Info"),
    content=Text("Detailed build version information.")
)
```

---

### Dropdown
Contextual action menu anchored to a trigger button.

```python
from pydataui.components import Dropdown, Button

Dropdown(
    trigger=Button("Actions", variant="outline"),
    items=[
        {"label": "Export CSV", "href": "/export/csv"},
        {"label": "Restart Workers", "action": "restart"}
    ]
)
```

---

## Media & Charts

### BarChart
Vertical bar chart rendered with lightweight SVG.

```python
from pydataui import BarChart

BarChart(
    data=[{"label": "Mon", "value": 140}, {"label": "Tue", "value": 220}, {"label": "Wed", "value": 310}],
    title="Daily Requests",
    height="300px"
)
```

---

### LineChart
Continuous time series or trendline chart.

```python
from pydataui import LineChart

LineChart(
    data=[{"x": 1, "y": 10}, {"x": 2, "y": 25}, {"x": 3, "y": 45}],
    title="Response Latency"
)
```

---

### PieChart & DoughnutChart
Proportional pie and doughnut charts.

```python
from pydataui.components import PieChart, DoughnutChart

PieChart(data=[{"label": "Success", "value": 98}, {"label": "Error", "value": 2}])
DoughnutChart(data=[{"label": "CPU", "value": 45}, {"label": "Free", "value": 55}])
```

---

### Sparkline
Inline miniature trendline for data tables and metric scorecards.

```python
from pydataui import Sparkline

Sparkline(values=[12, 14, 18, 15, 22, 28, 35], color="green")
```

---

### PlotlyChart
Renders interactive Plotly JSON / figure specifications.

```python
from pydataui.components.data_science import PlotlyChart

PlotlyChart(figure_json="{}")
```

---

### Image, Video, Audio, Icon
Multimedia content embeds.

```python
from pydataui.components.media import Image, Video, Audio, Icon

Image(src="/static/logo.svg", alt="Logo", width="120px")
Icon(name="server", size="lg")
```

---

## Data Science & ML Engineering Components

### MetricCard
Scorecard displaying KPI values, trend change percentages, and sparklines.

```python
from pydataui import MetricCard

MetricCard(
    title="Inference Latency (p99)",
    value="42.4 ms",
    change="-12.3%",
    trend="down",
    sparkline=[48, 47, 45, 44, 43, 42.4]
)
```

---

### DataFrameTable
Specialized tabular viewer for large Pandas and Polars DataFrames.

```python
import pandas as pd
from pydataui.components.data_science import DataFrameTable

df = pd.DataFrame({"model": ["Llama-3", "Mistral"], "f1": [0.94, 0.92]})
DataFrameTable(df)
```

---

### ModelMetrics
Machine learning evaluation dashboard summarizing accuracy, precision, recall, and F1.

```python
from pydataui.components.data_science import ModelMetrics

ModelMetrics(accuracy=0.984, precision=0.978, recall=0.991, f1_score=0.984)
```

---

### PipelineStatus
Visual status stepper for ETL and data pipelines.

```python
from pydataui.components.data_science import PipelineStatus

PipelineStatus(
    steps=[
        {"name": "Data Ingestion", "status": "completed", "duration": "32s"},
        {"name": "Tokenization", "status": "running", "duration": "1m 14s"},
        {"name": "Model Inference", "status": "pending", "duration": "-"}
    ]
)
```

---

### ConfusionMatrix
Interactive confusion matrix heatmap for classification models.

```python
from pydataui.components.data_science import ConfusionMatrix

ConfusionMatrix(
    matrix=[[1420, 25], [18, 1280]],
    labels=["Negative", "Positive"],
    title="Validation Matrix"
)
```

---

### JSONViewer
Collapsible JSON tree explorer.

```python
from pydataui.components.data_science import JSONViewer

JSONViewer(data={"cluster": "alpha", "metrics": {"p99": 42.4, "qps": 1420}})
```

---

### CodeBlock
Syntax-highlighted code block with copy button.

```python
from pydataui.components.data_science import CodeBlock

CodeBlock(code="select * from telemetry limit 10;", language="sql")
```

---

### FileDownload & DataUpload
Data exchange components for downloading and uploading datasets.

```python
from pydataui.components.data_science import FileDownload, DataUpload

FileDownload(label="Export Parquet", file_url="/api/export")
DataUpload(label="Import Training Set")
```

---

### SQLEditor
SQL query input area with execution trigger.

```python
from pydataui.components.data_science import SQLEditor

SQLEditor(initial_query="SELECT date, count(*) FROM logs GROUP BY 1;")
```

---

### FeatureImportance & SchemaViewer
Machine learning feature weight bar chart and database schema visualizer.

```python
from pydataui.components.data_science import FeatureImportance, SchemaViewer

FeatureImportance(features=[{"name": "user_tenure", "importance": 0.42}, {"name": "session_count", "importance": 0.38}])
SchemaViewer(schema={"id": "INTEGER", "username": "VARCHAR(255)", "created_at": "TIMESTAMP"})
```

---

## Shadcn Enterprise Suite

Modern accessible UI components following shadcn design patterns:

### ShadButton
```python
from pydataui.shadcn import ShadButton
ShadButton("Deploy to Cluster", variant="default", size="default")
```

### ShadCard
```python
from pydataui.shadcn import ShadCard, ShadCardHeader, ShadCardTitle, ShadCardContent
ShadCard(
    ShadCardHeader(ShadCardTitle("Cluster Overview")),
    ShadCardContent("All 8 instances operational.")
)
```

### ShadInput
```python
from pydataui.shadcn import ShadInput
ShadInput(placeholder="Enter search query...")
```

### ShadBadge
```python
from pydataui.shadcn import ShadBadge
ShadBadge("Online", variant="default")
```

### ShadAlert
```python
from pydataui.shadcn import ShadAlert
ShadAlert("Cluster restarted successfully.", title="Notification")
```

### ShadProgress
```python
from pydataui.shadcn import ShadProgress
ShadProgress(value=75)
```

### ShadTabs
```python
from pydataui.shadcn import ShadTabs
ShadTabs(tabs=[{"id": "t1", "label": "Metrics", "content": "Latency: 4.2ms"}])
```

### ShadDialog
```python
from pydataui.shadcn import ShadDialog, ShadButton, Text
ShadDialog(
    Text("Are you sure?"),
    trigger=ShadButton("Delete"),
    title="Confirm Action"
)
```

### ShadCommandPalette
```python
from pydataui.shadcn import ShadCommandPalette
ShadCommandPalette(
    items=[
        {"id": "1", "label": "Deploy App", "shortcut": "⌘D"},
        {"id": "2", "label": "Restart Server", "shortcut": "⌘R"}
    ]
)
```

### ShadDatePicker
```python
from pydataui.shadcn import ShadDatePicker
ShadDatePicker(label="Select Evaluation Date")
```
