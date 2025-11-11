import pytest
from src.hello import Hello

def test_greet():
    hello = Hello()
    result = hello.greet("World")
    assert result == "Hello, World!"

def test_add():
    hello = Hello()
    result = hello.add(5, 3)
    assert result == 8
