#!/usr/bin/env python3
"""
Tyck Installation Verification Script

Run this script after installing tyck from PyPI:
    pip install tyck
    python verify_installation.py

This script tests all major features documented in the README.
"""

import sys
from enum import Enum

def test_imports():
    """Test that all documented imports work."""
    print("1. Testing imports...")
    try:
        from tyck import (
            # Primitive types
            string, number, integer, boolean,
            datetime, date, time, uuid,
            bytes_type, decimal, any_type, none_type,
            # Complex type factories
            array, optional, literal, dict_type,
            set_type, tuple_type, union, enum_type,
            # Core functions
            interface, config, model, field,
            # Utility functions
            pick, omit, partial, required, extend, merge,
        )
        print("   [PASS] All imports successful")
        return True
    except ImportError as e:
        print(f"   [FAIL] Import failed: {e}")
        return False


def test_basic_interface():
    """Test basic interface creation."""
    print("2. Testing basic interface...")
    try:
        from tyck import interface, string, integer, number
        
        User = interface({
            'id': integer.positive(),
            'name': string.min(1).max(100),
            'email': string.email(),
            'age': number.gt(0).lt(150).default(None)
        })
        
        user = User(id=1, name="John", email="john@example.com")
        assert user.id == 1
        assert user.name == "John"
        assert user.email == "john@example.com"
        assert user.age is None
        
        print("   [PASS] Basic interface works")
        return True
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
        return False


def test_string_constraints():
    """Test string validation constraints."""
    print("3. Testing string constraints...")
    try:
        from tyck import interface, string
        from pydantic import ValidationError
        
        # Test min/max
        Schema = interface({'code': string.min(2).max(5)})
        obj = Schema(code="ABC")
        assert obj.code == "ABC"
        
        try:
            Schema(code="A")  # Too short
            print("   [FAIL] min() constraint not working")
            return False
        except ValidationError:
            pass
        
        # Test email
        Schema = interface({'email': string.email()})
        Schema(email="test@example.com")
        try:
            Schema(email="invalid")
            print("   [FAIL] email() constraint not working")
            return False
        except ValidationError:
            pass
        
        # Test pattern
        Schema = interface({'code': string.pattern(r'^[A-Z]{3}$')})
        Schema(code="ABC")
        try:
            Schema(code="abc")
            print("   [FAIL] pattern() constraint not working")
            return False
        except ValidationError:
            pass
        
        print("   [PASS] String constraints work")
        return True
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
        return False


def test_string_transformations():
    """Test string transformations (strip, lower, upper)."""
    print("4. Testing string transformations...")
    try:
        from tyck import interface, string
        
        # Test strip + lower
        Schema = interface({'name': string.strip().lower()})
        obj = Schema(name="  HELLO WORLD  ")
        assert obj.name == "hello world", f"Expected 'hello world', got '{obj.name}'"
        
        # Test upper
        Schema = interface({'code': string.upper()})
        obj = Schema(code="hello")
        assert obj.code == "HELLO", f"Expected 'HELLO', got '{obj.code}'"
        
        print("   [PASS] String transformations work")
        return True
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
        return False


def test_string_json():
    """Test JSON string validation."""
    print("5. Testing string.json()...")
    try:
        from tyck import interface, string
        from pydantic import ValidationError
        
        Schema = interface({'data': string.json()})
        
        # Valid JSON
        obj = Schema(data='{"key": "value"}')
        assert obj.data == '{"key": "value"}'
        
        # Invalid JSON
        try:
            Schema(data="not valid json")
            print("   [FAIL] json() validation not working")
            return False
        except ValidationError:
            pass
        
        print("   [PASS] JSON validation works")
        return True
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
        return False


def test_number_constraints():
    """Test number validation constraints."""
    print("6. Testing number constraints...")
    try:
        from tyck import interface, number, integer
        from pydantic import ValidationError
        import math
        
        # Test positive
        Schema = interface({'value': number.positive()})
        Schema(value=5.5)
        try:
            Schema(value=-1)
            print("   [FAIL] positive() constraint not working")
            return False
        except ValidationError:
            pass
        
        # Test range
        Schema = interface({'score': number.range(0, 100)})
        Schema(score=50)
        try:
            Schema(score=101)
            print("   [FAIL] range() constraint not working")
            return False
        except ValidationError:
            pass
        
        # Test finite
        Schema = interface({'value': number.finite()})
        Schema(value=100.5)
        try:
            Schema(value=math.inf)
            print("   [FAIL] finite() constraint not working")
            return False
        except ValidationError:
            pass
        
        # Test integer
        Schema = interface({'count': integer.positive()})
        obj = Schema(count=42)
        assert obj.count == 42
        
        print("   [PASS] Number constraints work")
        return True
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
        return False


def test_array():
    """Test array type."""
    print("7. Testing array type...")
    try:
        from tyck import interface, array, string
        from pydantic import ValidationError
        
        # Basic array
        Schema = interface({'tags': array(string)})
        obj = Schema(tags=["a", "b", "c"])
        assert obj.tags == ["a", "b", "c"]
        
        # With min/max
        Schema = interface({'items': array(string).min(1).max(3)})
        Schema(items=["a", "b"])
        try:
            Schema(items=[])
            print("   [FAIL] array min() not working")
            return False
        except ValidationError:
            pass
        
        # With unique
        Schema = interface({'tags': array(string).unique()})
        Schema(tags=["a", "b", "c"])
        try:
            Schema(tags=["a", "a", "b"])
            print("   [FAIL] array unique() not working")
            return False
        except ValidationError:
            pass
        
        print("   [PASS] Array type works")
        return True
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
        return False


def test_optional():
    """Test optional type."""
    print("8. Testing optional type...")
    try:
        from tyck import interface, optional, string
        
        Schema = interface({'bio': optional(string.max(100))})
        
        # Without value
        obj = Schema()
        assert obj.bio is None
        
        # With value
        obj = Schema(bio="Hello")
        assert obj.bio == "Hello"
        
        print("   [PASS] Optional type works")
        return True
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
        return False


def test_literal():
    """Test literal type."""
    print("9. Testing literal type...")
    try:
        from tyck import interface, literal
        from pydantic import ValidationError
        
        Schema = interface({'role': literal('admin', 'user', 'guest')})
        
        obj = Schema(role='admin')
        assert obj.role == 'admin'
        
        try:
            Schema(role='superuser')
            print("   [FAIL] literal() validation not working")
            return False
        except ValidationError:
            pass
        
        print("   [PASS] Literal type works")
        return True
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
        return False


def test_dict_type():
    """Test dict type."""
    print("10. Testing dict_type...")
    try:
        from tyck import interface, dict_type, string, any_type
        
        Schema = interface({'metadata': dict_type(string, any_type)})
        obj = Schema(metadata={'key': 'value', 'count': 42})
        assert obj.metadata == {'key': 'value', 'count': 42}
        
        print("   [PASS] Dict type works")
        return True
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
        return False


def test_union():
    """Test union type."""
    print("11. Testing union type...")
    try:
        from tyck import interface, union, string, integer
        
        Schema = interface({'id': union(string, integer)})
        
        obj1 = Schema(id="abc")
        assert obj1.id == "abc"
        
        obj2 = Schema(id=123)
        assert obj2.id == 123
        
        print("   [PASS] Union type works")
        return True
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
        return False


def test_enum_type():
    """Test enum type."""
    print("12. Testing enum_type...")
    try:
        from tyck import interface, enum_type
        
        class Color(Enum):
            RED = 'red'
            GREEN = 'green'
            BLUE = 'blue'
        
        Schema = interface({'color': enum_type(Color)})
        obj = Schema(color=Color.RED)
        assert obj.color == Color.RED
        
        print("   [PASS] Enum type works")
        return True
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
        return False


def test_model_decorator():
    """Test @model decorator."""
    print("13. Testing @model decorator...")
    try:
        from tyck import model, string, integer
        
        @model()
        class User:
            id: integer.positive()
            name: string.min(1)
            
            def greet(self) -> str:
                return f"Hello, {self.name}!"
        
        user = User(id=1, name="John")
        assert user.id == 1
        assert user.name == "John"
        assert user.greet() == "Hello, John!"
        
        print("   [PASS] @model decorator works")
        return True
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
        return False


def test_utility_functions():
    """Test utility functions (pick, omit, partial, etc.)."""
    print("14. Testing utility functions...")
    try:
        from tyck import interface, string, integer, array
        from tyck import pick, omit, partial, required, extend, merge
        from pydantic import ValidationError
        
        User = interface({
            'id': integer,
            'name': string,
            'email': string,
            'password': string,
        })
        
        # Test pick
        PublicUser = pick(User, 'id', 'name')
        obj = PublicUser(id=1, name="John")
        assert 'password' not in PublicUser.model_fields
        
        # Test omit
        SafeUser = omit(User, 'password')
        obj = SafeUser(id=1, name="John", email="j@e.com")
        assert 'password' not in SafeUser.model_fields
        
        # Test partial
        UserUpdate = partial(User)
        obj = UserUpdate(name="New Name")
        assert obj.name == "New Name"
        assert obj.id is None
        
        # Test extend
        Admin = extend(User, {
            'role': string.default('admin'),
        })
        obj = Admin(id=1, name="John", email="j@e.com", password="secret")
        assert obj.role == 'admin'
        
        # Test merge
        Profile = interface({'bio': string, 'avatar': string})
        UserWithProfile = merge(User, Profile)
        obj = UserWithProfile(id=1, name="John", email="j@e.com", password="x", bio="Hi", avatar="pic.jpg")
        assert obj.bio == "Hi"
        
        print("   [PASS] Utility functions work")
        return True
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
        return False


def test_nested_models():
    """Test nested model support."""
    print("15. Testing nested models...")
    try:
        from tyck import interface, string, array
        
        Address = interface({
            'street': string,
            'city': string,
        })
        
        User = interface({
            'name': string,
            'addresses': array(Address),
        })
        
        user = User(
            name="John",
            addresses=[
                {'street': '123 Main St', 'city': 'NYC'},
                {'street': '456 Oak Ave', 'city': 'LA'},
            ]
        )
        
        assert user.name == "John"
        assert len(user.addresses) == 2
        assert user.addresses[0].city == "NYC"
        
        print("   [PASS] Nested models work")
        return True
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
        return False


def test_serialization():
    """Test serialization (model_dump, model_dump_json)."""
    print("16. Testing serialization...")
    try:
        from tyck import interface, string, integer
        
        User = interface({
            'id': integer,
            'name': string,
        })
        
        user = User(id=1, name="John")
        
        # To dict
        data = user.model_dump()
        assert data == {'id': 1, 'name': 'John'}
        
        # To JSON
        json_str = user.model_dump_json()
        assert 'John' in json_str
        
        print("   [PASS] Serialization works")
        return True
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
        return False


def test_json_schema():
    """Test JSON schema generation."""
    print("17. Testing JSON schema generation...")
    try:
        from tyck import interface, string, integer
        
        User = interface({
            'id': integer.positive(),
            'name': string.min(1).max(100),
        })
        
        schema = User.model_json_schema()
        
        assert 'properties' in schema
        assert 'id' in schema['properties']
        assert 'name' in schema['properties']
        
        print("   [PASS] JSON schema generation works")
        return True
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
        return False


def test_config():
    """Test config helper."""
    print("18. Testing config helper...")
    try:
        from tyck import interface, string, config
        from pydantic import ValidationError
        
        User = interface({
            'name': string,
        }, config=config(frozen=True))
        
        user = User(name="John")
        
        try:
            user.name = "Jane"
            print("   [FAIL] frozen config not working")
            return False
        except ValidationError:
            pass
        
        print("   [PASS] Config helper works")
        return True
    except Exception as e:
        print(f"   [FAIL] Failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Tyck Installation Verification")
    print("=" * 50)
    print()
    
    tests = [
        test_imports,
        test_basic_interface,
        test_string_constraints,
        test_string_transformations,
        test_string_json,
        test_number_constraints,
        test_array,
        test_optional,
        test_literal,
        test_dict_type,
        test_union,
        test_enum_type,
        test_model_decorator,
        test_utility_functions,
        test_nested_models,
        test_serialization,
        test_json_schema,
        test_config,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print()
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    if failed == 0:
        print("\n[SUCCESS] All tests passed! Tyck is working correctly.")
        return 0
    else:
        print(f"\n[ERROR] {failed} test(s) failed. Please check your installation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
