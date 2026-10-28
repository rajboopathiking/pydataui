import pytest
from pydataui import State, NativeRenderer, NativeWidgetNode, compile_native
from pydataui.components import Button, Container, Heading, Text, Card, Input, HStack, VStack


class NativeCounterState(State):
    count: int = 5
    title: str = "Native Dashboard"

    def increment(self):
        self.count += 1


def test_compile_component_to_native():
    """Verify component tree compilation to intermediate NativeWidgetNode."""
    btn = Button("Click Me", on_click=NativeCounterState.increment)
    node = compile_native(btn)

    assert isinstance(node, NativeWidgetNode)
    assert node.widget_type == "Button"
    assert node.props["text"] == "Click Me"
    assert node.on_click is not None

    d = node.to_dict()
    assert d["type"] == "Button"
    assert d["props"]["text"] == "Click Me"
    assert d["has_click"] is True


def test_compile_hierarchy_with_state():
    """Verify nested layout with reactive StateVarRefs compiles cleanly."""
    def page():
        return Container(
            Heading(NativeCounterState.title),
            Card(
                Text(NativeCounterState.count),
                Button("Increment", on_click=NativeCounterState.increment),
            ),
            Input(name="notes", placeholder="Enter notes..."),
        )

    node = compile_native(page, state_snapshot={"NativeCounterState": {"count": 42, "title": "Live 60fps"}})

    assert node.widget_type == "Container"
    assert len(node.children) == 3

    # 1. Heading
    heading = node.children[0]
    assert heading.widget_type == "Heading"
    assert heading.props["text"] == "Live 60fps"

    # 2. Card
    card = node.children[1]
    assert card.widget_type == "Card"
    assert len(card.children) == 2
    assert card.children[0].widget_type == "Text"
    assert card.children[0].props["text"] == "42"

    # 3. Input
    inp = node.children[2]
    assert inp.widget_type == "Input"
    assert inp.props["placeholder"] == "Enter notes..."

    # Verify JSON export capability for native engine consumption
    node_dict = node.to_dict()
    assert node_dict["type"] == "Container"
    assert len(node_dict["children"]) == 3


def test_native_widget_flet_export_fallback():
    """Verify to_flet compiles or falls back to serialized dict if flet not installed."""
    btn = Button("Save")
    node = compile_native(btn)
    res = node.to_flet()
    assert res is not None
