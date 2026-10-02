import pytest
from pydataui.components import Component, Text, Heading, Button, Container, Flex, Input

def test_component_base():
    class Dummy(Component):
        def render(self):
            return "dummy"
    d = Dummy()
    assert d.render() == "dummy"

def test_text_render():
    t = Text("Hello")
    assert t.text == "Hello"

def test_heading_render():
    h = Heading("Title", level=2)
    assert h.text == "Title"
    assert h.level == 2

def test_button_event_handler():
    def my_handler():
        pass
    b = Button("Click Me", on_click=my_handler, variant="danger")
    assert b.label == "Click Me"
    assert b.variant == "danger"
    assert b.on_click == my_handler

def test_container():
    c = Container(Text("A"), Text("B"))
    assert len(c.children) == 2

def test_flex_layout():
    f = Flex(Text("1"), Text("2"), direction="column", gap="lg")
    assert len(f.children) == 2
    assert f.direction == "column"
    assert f.gap == "lg"

def test_input():
    i = Input("Username", placeholder="Enter name")
    assert i.label == "Username"
    assert i.placeholder == "Enter name"
