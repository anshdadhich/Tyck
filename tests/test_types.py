"""Tests for Tyck types module."""

import pytest
from pydantic import ValidationError

from tyck import (
    # Lowercase imports (as documented in README)
    string,
    number,
    integer,
    boolean,
    datetime,
    date,
    time,
    uuid,
    bytes_type,
    decimal,
    any_type,
    none_type,
    array,
    optional,
    literal,
    dict_type,
    set_type,
    tuple_type,
    union,
    enum_type,
    interface,
    config,
    model,
    field,
    pick,
    omit,
    partial,
    required,
    extend,
    merge,
    # PascalCase aliases
    String,
    Number,
    Integer,
    Boolean,
    Array,
    Literal,
)


class TestString:
    def test_string_basic(self):
        Schema = interface({'name': string})
        obj = Schema(name="John")
        assert obj.name == "John"
    
    def test_string_min_max(self):
        Schema = interface({'code': string.min(2).max(5)})
        
        obj = Schema(code="ABC")
        assert obj.code == "ABC"
        
        with pytest.raises(ValidationError):
            Schema(code="A")
        
        with pytest.raises(ValidationError):
            Schema(code="ABCDEF")
    
    def test_string_email(self):
        Schema = interface({'email': string.email()})
        
        obj = Schema(email="test@example.com")
        assert obj.email == "test@example.com"
        
        with pytest.raises(ValidationError):
            Schema(email="not-an-email")
    
    def test_string_url(self):
        Schema = interface({'website': string.url()})
        
        obj = Schema(website="https://example.com")
        assert obj.website == "https://example.com"
        
        with pytest.raises(ValidationError):
            Schema(website="not-a-url")
    
    def test_string_uuid(self):
        Schema = interface({'id': string.uuid()})
        
        obj = Schema(id="550e8400-e29b-41d4-a716-446655440000")
        assert obj.id == "550e8400-e29b-41d4-a716-446655440000"
        
        with pytest.raises(ValidationError):
            Schema(id="not-a-uuid")
    
    def test_string_pattern(self):
        Schema = interface({'code': string.pattern(r'^[A-Z]{3}$')})
        
        obj = Schema(code="ABC")
        assert obj.code == "ABC"
        
        with pytest.raises(ValidationError):
            Schema(code="abc")
    
    def test_string_length(self):
        Schema = interface({'zip': string.length(5)})
        
        obj = Schema(zip="12345")
        assert obj.zip == "12345"
        
        with pytest.raises(ValidationError):
            Schema(zip="1234")
    
    def test_string_default(self):
        Schema = interface({'name': string.default("Anonymous")})
        
        obj = Schema()
        assert obj.name == "Anonymous"
    
    def test_string_optional(self):
        Schema = interface({'bio': string.optional()})
        
        obj = Schema()
        assert obj.bio is None


class TestNumber:
    def test_number_basic(self):
        Schema = interface({'value': number})
        obj = Schema(value=3.14)
        assert obj.value == 3.14
    
    def test_number_positive(self):
        Schema = interface({'value': number.positive()})
        
        obj = Schema(value=5.5)
        assert obj.value == 5.5
        
        with pytest.raises(ValidationError):
            Schema(value=-1)
    
    def test_number_negative(self):
        Schema = interface({'value': number.negative()})
        
        obj = Schema(value=-5.5)
        assert obj.value == -5.5
        
        with pytest.raises(ValidationError):
            Schema(value=1)
    
    def test_number_range(self):
        Schema = interface({'score': number.range(0, 100)})
        
        obj = Schema(score=85.5)
        assert obj.score == 85.5
        
        with pytest.raises(ValidationError):
            Schema(score=101)
    
    def test_number_gt_lt(self):
        Schema = interface({'value': number.gt(10).lt(20)})
        
        obj = Schema(value=15)
        assert obj.value == 15
        
        with pytest.raises(ValidationError):
            Schema(value=10)
        
        with pytest.raises(ValidationError):
            Schema(value=20)
    
    def test_number_gte_lte(self):
        Schema = interface({'value': number.gte(10).lte(20)})
        
        obj = Schema(value=10)
        assert obj.value == 10
        
        obj = Schema(value=20)
        assert obj.value == 20
    
    def test_number_multiple_of(self):
        Schema = interface({'value': number.multiple_of(0.5)})
        
        obj = Schema(value=2.5)
        assert obj.value == 2.5
        
        with pytest.raises(ValidationError):
            Schema(value=2.3)
    
    def test_number_integer(self):
        Schema = interface({'value': number.integer()})
        
        obj = Schema(value=42)
        assert obj.value == 42


class TestInteger:
    def test_integer_basic(self):
        Schema = interface({'id': integer})
        obj = Schema(id=42)
        assert obj.id == 42
    
    def test_integer_positive(self):
        Schema = interface({'id': integer.positive()})
        
        obj = Schema(id=42)
        assert obj.id == 42
        
        with pytest.raises(ValidationError):
            Schema(id=-1)
    
    def test_integer_range(self):
        Schema = interface({'age': integer.range(0, 150)})
        
        obj = Schema(age=25)
        assert obj.age == 25
        
        with pytest.raises(ValidationError):
            Schema(age=200)


class TestBoolean:
    def test_boolean_basic(self):
        Schema = interface({'active': boolean})
        
        obj = Schema(active=True)
        assert obj.active is True
    
    def test_boolean_default(self):
        Schema = interface({'active': boolean.default(False)})
        
        obj = Schema()
        assert obj.active is False


class TestArray:
    def test_array_basic(self):
        Schema = interface({'tags': array(string)})
        
        obj = Schema(tags=["a", "b", "c"])
        assert obj.tags == ["a", "b", "c"]
    
    def test_array_min_max(self):
        Schema = interface({'items': array(string).min(1).max(3)})
        
        obj = Schema(items=["a", "b"])
        assert len(obj.items) == 2
        
        with pytest.raises(ValidationError):
            Schema(items=[])
        
        with pytest.raises(ValidationError):
            Schema(items=["a", "b", "c", "d"])
    
    def test_array_of_integers(self):
        Schema = interface({'scores': array(integer)})
        
        obj = Schema(scores=[1, 2, 3])
        assert obj.scores == [1, 2, 3]
    
    def test_array_nested(self):
        Address = interface({
            'street': string,
            'city': string,
        })
        Schema = interface({'addresses': array(Address)})
        
        obj = Schema(addresses=[
            {'street': '123 Main St', 'city': 'NYC'},
            {'street': '456 Oak Ave', 'city': 'LA'},
        ])
        assert len(obj.addresses) == 2


class TestOptional:
    def test_optional_basic(self):
        Schema = interface({'bio': optional(string)})
        
        obj = Schema()
        assert obj.bio is None
        
        obj = Schema(bio="Hello")
        assert obj.bio == "Hello"
    
    def test_optional_with_constraints(self):
        Schema = interface({'bio': optional(string.max(100))})
        
        obj = Schema()
        assert obj.bio is None
        
        obj = Schema(bio="Short bio")
        assert obj.bio == "Short bio"


class TestLiteral:
    def test_literal_basic(self):
        Schema = interface({'role': literal('admin', 'user', 'guest')})
        
        obj = Schema(role='admin')
        assert obj.role == 'admin'
        
        with pytest.raises(ValidationError):
            Schema(role='superuser')
    
    def test_literal_with_default(self):
        Schema = interface({'status': literal('active', 'inactive').default('active')})
        
        obj = Schema()
        assert obj.status == 'active'


class TestDictType:
    def test_dict_basic(self):
        Schema = interface({'metadata': dict_type(string, any_type)})
        
        obj = Schema(metadata={'key': 'value', 'count': 42})
        assert obj.metadata == {'key': 'value', 'count': 42}


class TestUnion:
    def test_union_basic(self):
        Schema = interface({'id': union(string, integer)})
        
        obj1 = Schema(id="abc")
        assert obj1.id == "abc"
        
        obj2 = Schema(id=123)
        assert obj2.id == 123


class TestEnumType:
    def test_enum_basic(self):
        from enum import Enum
        
        class Color(Enum):
            RED = 'red'
            GREEN = 'green'
            BLUE = 'blue'
        
        Schema = interface({'color': enum_type(Color)})
        
        obj = Schema(color=Color.RED)
        assert obj.color == Color.RED


class TestInterface:
    def test_interface_basic(self):
        User = interface({
            'id': integer.positive(),
            'name': string.min(1).max(100),
            'email': string.email(),
        })
        
        user = User(id=1, name="John", email="john@example.com")
        assert user.id == 1
        assert user.name == "John"
        assert user.email == "john@example.com"
    
    def test_interface_with_config(self):
        User = interface({
            'name': string,
        }, config=config(frozen=True))
        
        user = User(name="John")
        assert user.name == "John"
    
    def test_interface_nested(self):
        Address = interface({
            'street': string,
            'city': string,
        })
        User = interface({
            'name': string,
            'address': Address,
        })
        
        user = User(name="John", address={'street': '123 Main', 'city': 'NYC'})
        assert user.address.city == "NYC"
    
    def test_interface_serialization(self):
        User = interface({
            'id': integer,
            'name': string,
        })
        
        user = User(id=1, name="John")
        
        data = user.model_dump()
        assert data == {'id': 1, 'name': 'John'}
        
        json_str = user.model_dump_json()
        assert 'John' in json_str


class TestModel:
    def test_model_basic(self):
        @model()
        class User:
            id: integer.positive()
            name: string.min(1)
        
        user = User(id=1, name="John")
        assert user.id == 1
        assert user.name == "John"
    
    def test_model_with_method(self):
        @model()
        class User:
            name: string
            
            def greet(self) -> str:
                return f"Hello, {self.name}!"
        
        user = User(name="John")
        assert user.greet() == "Hello, John!"
    
    def test_model_frozen(self):
        @model(frozen=True)
        class User:
            name: string
        
        user = User(name="John")
        
        with pytest.raises(ValidationError):
            user.name = "Jane"


class TestUtilities:
    def test_pick(self):
        User = interface({
            'id': integer,
            'name': string,
            'email': string,
            'password': string,
        })
        
        PublicUser = pick(User, 'id', 'name', 'email')
        
        obj = PublicUser(id=1, name="John", email="john@example.com")
        assert obj.id == 1
        assert obj.name == "John"
        assert not hasattr(obj, 'password') or 'password' not in obj.model_fields
    
    def test_omit(self):
        User = interface({
            'id': integer,
            'name': string,
            'password': string,
        })
        
        SafeUser = omit(User, 'password')
        
        obj = SafeUser(id=1, name="John")
        assert obj.id == 1
        assert not hasattr(obj, 'password') or 'password' not in obj.model_fields
    
    def test_partial(self):
        User = interface({
            'id': integer,
            'name': string,
            'email': string,
        })
        
        UserUpdate = partial(User)
        
        update = UserUpdate(name="New Name")
        assert update.name == "New Name"
        assert update.id is None
        assert update.email is None
    
    def test_required(self):
        User = interface({
            'id': integer,
            'name': string.default("Anonymous"),
        })
        
        StrictUser = required(User)
        
        with pytest.raises(ValidationError):
            StrictUser(id=1)
    
    def test_extend(self):
        User = interface({
            'id': integer,
            'name': string,
        })
        
        Admin = extend(User, {
            'role': string.default('admin'),
            'permissions': array(string),
        })
        
        admin = Admin(id=1, name="John", permissions=['read', 'write'])
        assert admin.id == 1
        assert admin.role == 'admin'
        assert admin.permissions == ['read', 'write']
    
    def test_merge(self):
        User = interface({'id': integer, 'name': string})
        Profile = interface({'bio': string, 'avatar': string})
        
        UserWithProfile = merge(User, Profile)
        
        obj = UserWithProfile(id=1, name="John", bio="Hello", avatar="pic.jpg")
        assert obj.id == 1
        assert obj.bio == "Hello"


class TestPascalCaseAliases:
    """Test that PascalCase aliases work for backwards compatibility."""
    
    def test_string_alias(self):
        Schema = interface({'name': String})
        obj = Schema(name="John")
        assert obj.name == "John"
    
    def test_number_alias(self):
        Schema = interface({'value': Number.positive()})
        obj = Schema(value=5.5)
        assert obj.value == 5.5
    
    def test_integer_alias(self):
        Schema = interface({'id': Integer.positive()})
        obj = Schema(id=42)
        assert obj.id == 42
    
    def test_array_alias(self):
        Schema = interface({'tags': Array(String)})
        obj = Schema(tags=["a", "b"])
        assert obj.tags == ["a", "b"]
    
    def test_literal_alias(self):
        Schema = interface({'role': Literal('admin', 'user')})
        obj = Schema(role='admin')
        assert obj.role == 'admin'


class TestComplexExamples:
    """Test complex real-world examples from README."""
    
    def test_api_request_model(self):
        CreateUserRequest = interface({
            'name': string.min(1).max(100),
            'email': string.email(),
            'age': optional(number.gt(0).lt(150))
        })
        
        req = CreateUserRequest(name="John", email="john@example.com")
        assert req.name == "John"
        assert req.age is None
    
    def test_nested_models(self):
        Address = interface({
            'street': string,
            'city': string,
            'zip': string.pattern(r'^\d{5}$'),
            'country': string.default('USA')
        })
        
        Customer = interface({
            'id': number.integer().positive(),
            'name': string.min(1),
            'email': string.email(),
            'addresses': array(Address),
        })
        
        customer = Customer(
            id=1,
            name="John Doe",
            email="john@example.com",
            addresses=[{
                'street': "123 Main St",
                'city': "New York",
                'zip': "10001"
            }]
        )
        
        assert customer.id == 1
        assert customer.addresses[0].country == "USA"
    
    def test_json_schema_generation(self):
        User = interface({
            'id': integer.positive(),
            'name': string.min(1).max(100),
            'email': string.email(),
        })
        
        schema = User.model_json_schema()
        
        assert 'properties' in schema
        assert 'id' in schema['properties']
        assert 'name' in schema['properties']
        assert 'email' in schema['properties']
