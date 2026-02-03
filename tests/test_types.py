"""Tests for Tyck types module."""

import pytest
from tyck import (
    String,
    Number,
    Integer,
    Boolean,
    Array,
    OptionalType,
    Literal,
    interface,
    pick_fields,
    omit_fields,
)


class TestString:
    def test_string_basic(self):
        Schema = interface({'name': String})
        obj = Schema(name="John")
        assert obj.name == "John"
    
    def test_string_min_max(self):
        Schema = interface({'code': String.min(2).max(5)})
        
        # Valid
        obj = Schema(code="ABC")
        assert obj.code == "ABC"
        
        # Too short
        with pytest.raises(Exception):
            Schema(code="A")
        
        # Too long
        with pytest.raises(Exception):
            Schema(code="ABCDEF")
    
    def test_string_email(self):
        Schema = interface({'email': String.email()})
        
        # Valid
        obj = Schema(email="test@example.com")
        assert obj.email == "test@example.com"
        
        # Invalid
        with pytest.raises(Exception):
            Schema(email="not-an-email")


class TestNumber:
    def test_number_positive(self):
        Schema = interface({'value': Number.positive()})
        
        obj = Schema(value=5.5)
        assert obj.value == 5.5
        
        with pytest.raises(Exception):
            Schema(value=-1)
    
    def test_number_range(self):
        Schema = interface({'score': Number.range(0, 100)})
        
        obj = Schema(score=85.5)
        assert obj.score == 85.5
        
        with pytest.raises(Exception):
            Schema(score=101)


class TestInteger:
    def test_integer_positive(self):
        Schema = interface({'id': Integer.positive()})
        
        obj = Schema(id=42)
        assert obj.id == 42
        
        with pytest.raises(Exception):
            Schema(id=-1)


class TestOptional:
    def test_optional_with_default(self):
        Schema = interface({'name': String.optional()})
        
        obj1 = Schema(name="John")
        assert obj1.name == "John"
        
        obj2 = Schema()
        assert obj2.name is None


class TestUtils:
    def test_pick_fields(self):
        User = interface({
            'id': int,
            'name': str,
            'email': str
        })
        
        PublicUser = pick_fields(User, 'id', 'name')
        obj = PublicUser(id=1, name="John")
        
        assert obj.id == 1
        assert obj.name == "John"
    
    def test_omit_fields(self):
        User = interface({
            'id': int,
            'name': str,
            'password': str
        })
        
        SafeUser = omit_fields(User, 'password')
        obj = SafeUser(id=1, name="John")
        
        assert hasattr(obj, 'id')
        assert hasattr(obj, 'name')
        assert not hasattr(obj, 'password')
