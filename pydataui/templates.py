"""Low-code page templates for common data-team workflows.

The templates are ordinary PyDataUI components, so they can be returned from an
``App.page`` handler and combined with state-driven actions.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Iterable, Optional

from .components import (
    Alert,
    Badge,
    Box,
    Card,
    Container,
    Flex,
    Grid,
    Heading,
    Progress,
    Table,
    Text,
)
from .components.base import Component
from .components.data_science import (
    ConfusionMatrix,
    DataFrameTable,
    DataTimeline,
    FeatureImportance,
    MetricCard,
    ModelMetrics,
    PipelineStatus,
    SchemaViewer,
)
from .state import StateVarRef

__all__ = [
    "analyst_dashboard",
    "data_quality_dashboard",
    "pipeline_operations",
    "model_registry",
    "quality_dashboard",
    "pipeline_dashboard",
    "ml_registry",
]

_RESPONSIVE_GRID = "repeat(auto-fit, minmax(min(100%, 320px), 1fr))"
_METRIC_GRID = "repeat(auto-fit, minmax(min(100%, 210px), 1fr))"

_STATUS_VARIANTS = {
    "active": "success",
    "archived": "primary",
    "canary": "warning",
    "closed": "success",
    "critical": "danger",
    "degraded": "warning",
    "development": "primary",
    "draft": "primary",
    "error": "danger",
    "failed": "danger",
    "fail": "danger",
    "healthy": "success",
    "high": "danger",
    "info": "info",
    "live": "success",
    "low": "info",
    "medium": "warning",
    "open": "warning",
    "passing": "success",
    "pass": "success",
    "pending": "warning",
    "production": "success",
    "ready": "success",
    "resolved": "success",
    "retired": "danger",
    "running": "info",
    "shadow": "warning",
    "staging": "info",
    "stale": "warning",
    "success": "success",
    "warning": "warning",
}


def _materialize(value: Any) -> Any:
    if isinstance(value, StateVarRef):
        return value._get_val()
    return value


def _as_component(value: Any) -> Component:
    value = _materialize(value)
    if isinstance(value, Component):
        return value
    return Text(str(value))


def _action_row(actions: Optional[Iterable[Any]]) -> Optional[Flex]:
    actions = _materialize(actions)
    if not actions:
        return None
    if isinstance(actions, Component):
        actions = [actions]
    children = [_as_component(action) for action in actions if action is not None]
    if not children:
        return None
    return Flex(*children, gap="sm", align="center", wrap="wrap")


def _page_header(
    title: str,
    subtitle: Optional[str],
    actions: Optional[Iterable[Any]] = None,
) -> Flex:
    left = Flex(
        Heading(title, level=1),
        Text(subtitle, size="sm") if subtitle else None,
        direction="column",
        gap="xs",
        align="start",
    )
    action_row = _action_row(actions)
    if action_row is None:
        return Flex(left, class_name="pdu-mb-lg")
    return Flex(
        left,
        action_row,
        justify="space-between",
        align="start",
        wrap="wrap",
        gap="md",
        class_name="pdu-mb-lg",
    )


def _status_badge(value: Any) -> Badge:
    label = str(value).replace("_", " ").replace("-", " ").title()
    variant = _STATUS_VARIANTS.get(str(value).lower(), "primary")
    return Badge(label, variant=variant)


def _status_keys(row: Mapping[str, Any]) -> set[str]:
    return {
        key
        for key in row
        if str(key).lower() in {"status", "state", "health", "severity", "stage"}
    }


def _rows_with_badges(
    rows: Any,
    columns: Optional[Sequence[str]] = None,
    badge_keys: Optional[set[str]] = None,
) -> Component:
    rows = _materialize(rows)
    if isinstance(rows, Component):
        return rows
    if rows is None:
        rows = []
    if hasattr(rows, "to_html") and hasattr(rows, "columns"):
        return DataFrameTable(df=rows)
    if isinstance(rows, Mapping):
        rows = [rows]
    normalized = []
    for row in rows:
        if not isinstance(row, Mapping):
            normalized.append(row)
            continue
        keys = badge_keys if badge_keys is not None else _status_keys(row)
        normalized.append(
            {
                key: (
                    _status_badge(value)
                    if key in keys and value not in (None, "")
                    else value
                )
                for key, value in row.items()
            }
        )
    return Box(
        Table(data=normalized, columns=columns),
        style={"overflow-x": "auto", "max-width": "100%"},
    )


def _metrics_grid(metrics: Any) -> Optional[Grid]:
    metrics = _materialize(metrics)
    if not metrics:
        return None
    if isinstance(metrics, Component):
        return Grid(metrics, template_columns=_METRIC_GRID, gap="md", class_name="pdu-mb-lg")
    if isinstance(metrics, Mapping):
        entries = [
            {
                "title": metric_title,
                "value": metric_value,
            }
            for metric_title, metric_value in metrics.items()
        ]
    else:
        entries = list(metrics)

    cards = []
    for entry in entries:
        if isinstance(entry, Component):
            cards.append(entry)
            continue
        if not isinstance(entry, Mapping):
            cards.append(MetricCard(title=str(entry), value=""))
            continue
        title = entry.get("title", entry.get("label", entry.get("name", "Metric")))
        cards.append(
            MetricCard(
                title=str(title),
                value=entry.get("value", ""),
                format=entry.get("format", entry.get("fmt", "")),
                delta=str(entry.get("delta", entry.get("change", ""))),
                delta_type=entry.get("delta_type", "neutral"),
                icon=str(entry.get("icon", "")),
                description=str(entry.get("description", entry.get("help_text", ""))),
            )
        )
    if not cards:
        return None
    return Grid(*cards, template_columns=_METRIC_GRID, gap="md", class_name="pdu-mb-lg")


def _section(
    title: str,
    body: Optional[Component],
    subtitle: Optional[str] = None,
) -> Optional[Card]:
    if body is None:
        return None
    return Card(
        body,
        title=title,
        subtitle=subtitle,
        class_name="pdu-mb-lg",
    )


def _coerce_chart(chart: Any, title: str) -> Optional[Card]:
    chart = _materialize(chart)
    if chart is None:
        return None
    return _section(title, _as_component(chart))


def _schema_component(schema: Any) -> Optional[Component]:
    schema = _materialize(schema)
    if schema is None:
        return None
    if isinstance(schema, Component):
        return schema
    if isinstance(schema, Mapping):
        return SchemaViewer(schema=dict(schema))
    return SchemaViewer(df=schema)


def _confusion_component(value: Any) -> Optional[Component]:
    value = _materialize(value)
    if value is None:
        return None
    if isinstance(value, Component):
        return value
    if isinstance(value, Mapping):
        matrix = value.get("matrix")
        labels = value.get("labels")
        if matrix is not None and labels is not None:
            return ConfusionMatrix(matrix=matrix, labels=labels)
    if isinstance(value, (tuple, list)) and len(value) == 2:
        matrix, labels = value
        if isinstance(matrix, Sequence) and isinstance(labels, Sequence):
            return ConfusionMatrix(matrix=matrix, labels=labels)
    return None


def _feature_importance_component(value: Any, title: str) -> Optional[Component]:
    value = _materialize(value)
    if value is None:
        return None
    if isinstance(value, Component):
        return value
    if isinstance(value, Mapping):
        return FeatureImportance(features=dict(value), title=title)
    return None


def _filters(filters: Optional[Iterable[Any]]) -> Optional[Flex]:
    filters = _materialize(filters)
    if not filters:
        return None
    if isinstance(filters, Component):
        filters = [filters]
    children = [_as_component(item) for item in filters if item is not None]
    if not children:
        return None
    return Flex(
        Text("Filters", size="sm"),
        *children,
        gap="sm",
        align="end",
        wrap="wrap",
        class_name="pdu-mb-lg",
    )


def analyst_dashboard(
    *,
    title: str = "Analyst Dashboard",
    subtitle: Optional[str] = "Track the metrics, trends, and records that matter most.",
    metrics: Any = None,
    filters: Optional[Iterable[Any]] = None,
    chart: Any = None,
    chart_title: str = "Performance trend",
    table: Any = None,
    table_columns: Optional[Sequence[str]] = None,
    table_title: str = "Latest records",
    export: Optional[Component] = None,
    actions: Optional[Iterable[Any]] = None,
    **container_props: Any,
) -> Container:
    """Compose a KPI, chart, filters, and table page for analysts."""
    header_actions = list(actions or [])
    if export is not None:
        header_actions.append(export)

    sections = [
        _page_header(title, subtitle, header_actions),
        _filters(filters),
        _metrics_grid(metrics),
        _coerce_chart(chart, chart_title),
        _section(
            table_title,
            _rows_with_badges(table, table_columns) if table is not None else None,
        ),
    ]
    if all(section is None for section in sections[1:]):
        sections.append(Alert("Add metrics, a chart, or a table to start.", variant="info"))
    return Container(*sections, padding="lg", **container_props)


def data_quality_dashboard(
    *,
    title: str = "Data Quality & Catalog",
    subtitle: Optional[str] = "Monitor freshness, schema drift, and open quality checks.",
    metrics: Any = None,
    score: Optional[float] = None,
    score_label: str = "Overall quality score",
    datasets: Any = None,
    dataset_columns: Optional[Sequence[str]] = None,
    schema: Any = None,
    issues: Any = None,
    issue_columns: Optional[Sequence[str]] = None,
    upload: Optional[Component] = None,
    actions: Optional[Iterable[Any]] = None,
    **container_props: Any,
) -> Container:
    """Compose a data-quality scorecard, catalog, schema, and issue view."""
    children: list[Any] = [_page_header(title, subtitle, actions)]
    children.append(_metrics_grid(metrics))

    score = _materialize(score)
    if score is not None:
        try:
            score_value = max(0.0, min(100.0, float(score)))
            children.append(
                Card(
                    Heading(f"{score_value:.1f}%", level=2),
                    Progress(value=score_value, max=100, show_label=True),
                    title=score_label,
                    class_name="pdu-mb-lg",
                )
            )
        except (TypeError, ValueError):
            pass

    if datasets is not None:
        children.append(
            _section(
                "Dataset catalog",
                _rows_with_badges(datasets, dataset_columns),
            )
        )

    schema_component = _schema_component(schema)
    if schema_component is not None:
        children.append(_section("Schema health", schema_component))

    if issues is not None:
        empty_issues = isinstance(issues, (list, tuple)) and not issues
        if empty_issues:
            children.append(Alert("No open quality issues.", variant="success"))
        else:
            children.append(
                _section("Quality checks", _rows_with_badges(issues, issue_columns))
            )

    if upload is not None:
        children.append(_section("Add data", upload))

    if all(child is None for child in children[1:]):
        children.append(Alert("Configure quality metrics, datasets, or checks.", variant="info"))
    return Container(*children, padding="lg", **container_props)


def pipeline_operations(
    *,
    title: str = "Pipeline Operations",
    subtitle: Optional[str] = "Run status, throughput, and recent pipeline activity.",
    metrics: Any = None,
    pipeline: Optional[Mapping[str, Any]] = None,
    steps: Optional[Sequence[Mapping[str, Any]]] = None,
    pipelines: Any = None,
    pipeline_columns: Optional[Sequence[str]] = None,
    events: Optional[Sequence[Mapping[str, str]]] = None,
    runs: Any = None,
    run_columns: Optional[Sequence[str]] = None,
    actions: Optional[Iterable[Any]] = None,
    **container_props: Any,
) -> Container:
    """Compose an operations view with pipeline steps, runs, and activity."""
    children: list[Any] = [_page_header(title, subtitle, actions)]
    children.append(_metrics_grid(metrics))

    pipeline = _materialize(pipeline) or {}
    steps = _materialize(steps)
    pipeline_steps = steps if steps is not None else _materialize(pipeline.get("steps"))
    if pipeline or pipeline_steps:
        pipeline_title = str(pipeline.get("name", "Active pipeline"))
        summary = []
        if pipeline.get("status") is not None:
            summary.append(_status_badge(pipeline["status"]))
        if pipeline.get("schedule"):
            summary.append(Text(f"Schedule: {pipeline['schedule']}", size="sm"))
        if pipeline.get("owner"):
            summary.append(Text(f"Owner: {pipeline['owner']}", size="sm"))
        body_children = []
        if summary:
            body_children.append(
                Flex(*summary, gap="sm", align="center", wrap="wrap")
            )
        if pipeline_steps:
            body_children.append(PipelineStatus(steps=list(pipeline_steps)))
        children.append(
            _section(
                pipeline_title,
                Flex(*body_children, direction="column", gap="md"),
                subtitle=pipeline.get("description"),
            )
        )

    if pipelines is not None:
        children.append(
            _section(
                "Pipelines",
                _rows_with_badges(pipelines, pipeline_columns),
            )
        )

    events = _materialize(events)
    if events is not None:
        if events:
            children.append(_section("Recent activity", DataTimeline(events=list(events))))
        else:
            children.append(Alert("No recent pipeline activity.", variant="info"))

    if runs is not None:
        children.append(_section("Recent runs", _rows_with_badges(runs, run_columns)))

    if all(child is None for child in children[1:]):
        children.append(Alert("Add metrics, pipeline steps, or run history.", variant="info"))
    return Container(*children, padding="lg", **container_props)


def model_registry(
    *,
    title: str = "Model Registry",
    subtitle: Optional[str] = "Compare model versions, evaluation metrics, and deployment stages.",
    model: Optional[Mapping[str, Any]] = None,
    models: Any = None,
    model_columns: Optional[Sequence[str]] = None,
    metrics: Any = None,
    confusion_matrix: Any = None,
    feature_importance: Any = None,
    feature_title: str = "Feature importance",
    actions: Optional[Iterable[Any]] = None,
    **container_props: Any,
) -> Container:
    """Compose a model registry with a selected model evaluation panel."""
    children: list[Any] = [_page_header(title, subtitle, actions)]
    model = _materialize(model) or {}
    metrics = _materialize(metrics)

    selected_metrics = _materialize(
        metrics if metrics is not None else model.get("metrics")
    )
    if model or selected_metrics:
        name = str(model.get("name", "Selected model"))
        summary_parts = []
        if model.get("stage") is not None:
            summary_parts.append(_status_badge(model["stage"]))
        if model.get("version") is not None:
            summary_parts.append(Text(f"Version {model['version']}", size="sm"))
        if model.get("owner") is not None:
            summary_parts.append(Text(f"Owner: {model['owner']}", size="sm"))
        if model.get("updated") is not None:
            summary_parts.append(Text(f"Updated: {model['updated']}", size="sm"))

        body_children = []
        if summary_parts:
            body_children.append(
                Flex(*summary_parts, gap="sm", align="center", wrap="wrap")
            )
        if isinstance(selected_metrics, Component):
            body_children.append(selected_metrics)
        elif selected_metrics:
            body_children.append(ModelMetrics(metrics=dict(selected_metrics)))
        children.append(_section(name, Flex(*body_children, direction="column", gap="md")))

    confusion = _confusion_component(confusion_matrix)
    features = _feature_importance_component(feature_importance, feature_title)
    evaluation = [item for item in (confusion, features) if item is not None]
    if evaluation:
        children.append(
            Grid(
                *evaluation,
                template_columns=_RESPONSIVE_GRID,
                gap="lg",
                class_name="pdu-mb-lg",
            )
        )

    if models is not None:
        children.append(_section("Registered models", _rows_with_badges(models, model_columns)))

    if len(children) == 1:
        children.append(Alert("Register a model or add evaluation metrics.", variant="info"))
    return Container(*children, padding="lg", **container_props)


quality_dashboard = data_quality_dashboard
pipeline_dashboard = pipeline_operations
ml_registry = model_registry
