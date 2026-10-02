import pytest
from pydataui import State

def test_state_creation():
    class TestState(State):
        val: int = 10
    
    assert TestState.val == 10

def test_state_mutation():
    class MutateState(State):
        count: int = 0
        def inc(self):
            self.count += 1
            
    assert MutateState.count == 0
    MutateState.inc()
    assert MutateState.count == 1

def test_state_serialization():
    class SerialState(State):
        msg: str = "hello"
        
    data = SerialState.to_dict()
    assert data["msg"] == "hello"

def test_state_reset():
    class ResetState(State):
        num: int = 5
        
    ResetState.num = 100
    assert ResetState.num == 100
    ResetState.reset()
    assert ResetState.num == 5
