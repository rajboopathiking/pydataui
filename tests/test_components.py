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

def test_input_binding_falsy():
    from pydataui.state import State
    class TestState(State):
        empty_str: str = ""
        zero_int: int = 0
        false_bool: bool = False

    # Falsy string bind must preserve name attribute
    inp = Input("Name", bind=TestState.empty_str)
    html = inp.render({})
    assert 'name="empty_str"' in html

    inp2 = Input("Count", bind=TestState.zero_int)
    html2 = inp2.render({})
    assert 'name="zero_int"' in html2

def test_checkbox_events():
    from pydataui.state import State
    class TestState(State):
        agreed: bool = False
        def toggle(self): pass

    from pydataui.components import Checkbox
    chk = Checkbox("I Agree", bind=TestState.agreed, on_change=TestState.toggle)
    html = chk.render({})
    assert 'name="agreed"' in html
    # Checkbox input must have hx-post
    assert 'hx-post="/_pdu/event/TestState/toggle"' in html
    # The outer label should NOT have hx-post duplicated
    assert not html.startswith('<label id="') or 'hx-post=' not in html[:html.find('>')]

def test_modal_stacking_and_events():
    from pydataui.state import State
    from pydataui.components import Modal
    class TestModalState(State):
        is_open: bool = True
        def close(self): pass

    m = Modal(
        title="Edit Item",
        is_open=True,
        on_close=TestModalState.close,
        children=[Text("Modal body content")]
    )
    html = m.render({})
    assert 'Edit Item' in html
    assert 'Modal body content' in html
    # Outer wrapper should not have hx-post (which would intercept clicks on inputs)
    wrapper_opening = html[:html.find('>')+1]
    assert 'hx-post' not in wrapper_opening
    # Close button and backdrop must have hx-post
    assert 'hx-post="/_pdu/event/TestModalState/close"' in html
    # Content must have higher z-index than backdrop
    assert 'z-index:10' in html or 'z-10' in html
    assert 'z-index:1' in html
