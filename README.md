# Tyck (Type Check) - TypeScript-style Pydantic Wrapper

A Simplified API for Pydantic validation that makes it easier to define schemas with method chaining while maintaining full compatibility with Pydantic's features.

## Installation

```bash
pip install tyck
```

## Quick Start

```python
from tyck import interface, string, number, integer

# Define a schema with fluent API
User = interface({
    'id': integer.positive(),
    'name': string.min(1).max(100),
    'email': string.email(),
    'age': number.gt(0).lt(150).default(None)
})

# Create and validate
user = User(
        id=1, name="John",
        email="john@example.com"
        )
        
print(user.model_dump())
#  {'id': 1,
#  'name': 'John',
#  'email': 'john@example.com', 
#  'age': None
#   }
```

## Table of Contents

- [Data Types](#data-types)
  - [Primitive Types](#primitive-types)
  - [String Constraints](#string-constraints)
  - [Number Constraints](#number-constraints)
  - [Complex Types](#complex-types)
- [APIs](#apis)
  - [Functional API](#functional-api)
  - [Class-Based API](#class-based-api)
- [Utility Functions](#utility-functions)
- [Configuration](#configuration)
- [Validation & Serialization](#validation--serialization)
- [JSON Schema](#json-schema)
- [Examples](#examples)

---

## Data Types

### Primitive Types

#### String
```python
from tyck import string

# Basic usage
name = string

# With constraints
username = string.min(3).max(20)
email_field = string.email()
url_field = string.url()
uuid_field = string.uuid()
datetime_field = string.datetime()
date_field = string.date()
time_field = string.time()
json_field = string.json()
code = string.pattern(r'^[A-Z]{3}$')
zip_code = string.length(5)
ip_address = string.ip()  # or string.ip(4) for IPv4, string.ip(6) for IPv6
```

**Available Methods:**
- `.min(length)` - Minimum string length
- `.max(length)` - Maximum string length
- `.length(exact)` - Exact string length
- `.pattern(regex)` - Regex pattern validation
- `.email()` - Email format validation
- `.url()` - URL format validation
- `.uuid()` - UUID format validation
- `.datetime()` - ISO datetime format
- `.date()` - ISO date format
- `.time()` - ISO time format
- `.ip(version=None)` - IP address validation
- `.json()` - JSON string validation
- `.strip()` - Strip whitespace
- `.lower()` - Convert to lowercase
- `.upper()` - Convert to uppercase
- `.default(value)` - Set default value
- `.alias(name)` - Set field alias
- `.description(text)` - Set field description
- `.title(text)` - Set field title
- `.examples(*values)` - Set example values
- `.deprecated(bool)` - Mark as deprecated

#### Number (Float)
```python
from tyck import number

# Basic usage
price = number

# With constraints
positive_num = number.positive()
negative_num = number.negative()
percentage = number.gte(0).lte(100)
range_num = number.gt(10).lt(100)
finite_num = number.finite()
multiple = number.multiple_of(0.5)
```

**Available Methods:**
- `.gt(value)` - Greater than
- `.gte(value)` - Greater than or equal
- `.lt(value)` - Less than
- `.lte(value)` - Less than or equal
- `.positive()` - Greater than 0
- `.negative()` - Less than 0
- `.non_positive()` - Less than or equal to 0
- `.non_negative()` - Greater than or equal to 0
- `.finite()` - Not infinite/NaN
- `.multiple_of(value)` - Divisible by value
- `.range(min, max)` - Inclusive range (gte + lte)
- `.integer()` - Require integer values
- `.default(value)` - Set default value

#### Integer
```python
from tyck import integer

# Basic usage
id_field = integer

# With constraints
positive_int = integer.positive()
age = integer.range(0, 150)
```

**Available Methods:** (same as Number)
- `.gt(value)`, `.gte(value)`, `.lt(value)`, `.lte(value)`
- `.positive()`, `.negative()`, `.non_positive()`, `.non_negative()`
- `.multiple_of(value)`, `.range(min, max)`
- `.default(value)`

#### Boolean
```python
from tyck import boolean

# Basic usage
is_active = boolean

# With strict validation
strict_bool = boolean.strict()
```

**Available Methods:**
- `.strict()` - Strict boolean validation
- `.default(value)` - Set default value

#### DateTime
```python
from tyck import datetime, date, time

# DateTime
created_at = datetime

# Date
birth_date = date

# Time
opening_time = time
```

#### UUID
```python
from tyck import uuid

# Any UUID version
user_id = uuid
```

#### Bytes
```python
from tyck import bytes_type

# Basic usage
data = bytes_type

# With constraints
limited_data = bytes_type.min(1).max(1024)
```

**Available Methods:**
- `.min(length)` - Minimum bytes length
- `.max(length)` - Maximum bytes length
- `.default(value)` - Set default value

#### Decimal
```python
from tyck import decimal

# Basic usage
price = decimal

# With constraints
precise = decimal.max_digits(10).decimal_places(2)
positive_decimal = decimal.gt(0)
```

**Available Methods:**
- `.max_digits(n)` - Maximum total digits
- `.decimal_places(n)` - Maximum decimal places
- `.gt(value)`, `.gte(value)`, `.lt(value)`, `.lte(value)`
- `.default(value)` - Set default value

#### Any
```python
from tyck import any_type

# Accept any value
metadata = any_type
```

#### None
```python
from tyck import none_type

# None value
null_field = none_type
```

---

### Complex Types

#### Array / List
```python
from tyck import array, string, number

# Basic array
tags = array(string)

# With constraints
members = array(string).min(1).max(10)
scores = array(number).unique()  # Unique items only
exact_count = array(string).length(5)
```

**Available Methods:**
- `.min(length)` - Minimum items
- `.max(length)` - Maximum items
- `.length(exact)` - Exact item count
- `.unique()` - Require unique items
- `.default(value)` - Set default value

#### Optional
```python
from tyck import optional, string

# Optional field
bio = optional(string.max(500))
age = optional(number)
```

#### Literal
```python
from tyck import literal

# Enum-like validation
role = literal('admin', 'user', 'guest')
status = literal('active', 'inactive', 'pending')
```

#### Dictionary
```python
from tyck import dict_type, string, any_type, integer

# Dict[str, Any]
metadata = dict_type(string, any_type)

# Dict[str, int]
counts = dict_type(string, integer)
```

**Available Methods:**
- `.min(length)` - Minimum key-value pairs
- `.max(length)` - Maximum key-value pairs
- `.default(value)` - Set default value

#### Set
```python
from tyck import set_type, string

# Set of unique strings
tags = set_type(string)
```

**Available Methods:**
- `.min(length)` - Minimum items
- `.max(length)` - Maximum items
- `.default(value)` - Set default value

#### Tuple
```python
from tyck import tuple_type, number, string

# Fixed-size tuple
point = tuple_type(number, number)  # (x, y)
person = tuple_type(string, number)  # (name, age)
```

#### Union
```python
from tyck import union, string, number

# Multiple allowed types
id_or_name = union(string, number)
```

#### Enum
```python
from enum import Enum
from tyck import enum_type

class Color(Enum):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'

color_field = enum_type(Color)
```

---

## APIs

### Functional API

Create models using the `interface()` function with a dictionary of fields.

```python
from tyck import interface, string, number, integer, array, optional, config

# Basic interface
User = interface({
    'id': integer.positive(),
    'name': string.min(1).max(100),
    'email': string.email(),
    'age': optional(number.gt(0).lt(150)),
    'tags': array(string).max(10),
})

# With configuration
StrictUser = interface({
    'name': string,
    'email': string.email(),
}, config=config(
    strict=True,           # Strict type checking
    frozen=True,           # Immutable models
    extra='forbid',        # Forbid extra fields
))

# Create instance
user = User(id=1, name="John", email="john@example.com")

# Access fields
print(user.id)        # 1
print(user.name)      # "John"

# Serialization
user_dict = user.model_dump()       # Dict
user_json = user.model_dump_json()  # JSON string
```

**interface() Parameters:**
- `fields` (dict) - Field definitions mapping names to type builders
- `config` (ConfigDict, optional) - Pydantic configuration
- `validators` (dict, optional) - Custom validator functions
- `name` (str, optional) - Custom class name
- `base` (BaseModel, optional) - Base class to inherit from
- `doc` (str, optional) - Docstring for the model

### Class-Based API

Define models using Python classes with the `@model` decorator.

```python
from tyck import model, string, number, integer, array, optional

@model()
class User:
    id: integer.positive()
    name: string.min(1).max(100)
    email: string.email()
    age: optional(number.gt(0).lt(150))
    tags: array(string).max(10)
    
    def greet(self) -> str:
        return f"Hello, {self.name}!"

# Create instance
user = User(id=1, name="John", email="john@example.com")

# Call methods
print(user.greet())  # "Hello, John!"
```

**@model() Parameters:**
- `config` (ConfigDict, optional) - Pydantic configuration
- `frozen` (bool) - Make model immutable
- `strict` (bool) - Enable strict type checking
- `extra` (str) - How to handle extra fields ('ignore', 'allow', 'forbid')
- `validate_assignment` (bool) - Validate on assignment
- `populate_by_name` (bool) - Allow population by field name
- `use_enum_values` (bool) - Use enum values instead of instances

#### Inheritance

```python
from tyck import model, string, integer, array

@model()
class BaseUser:
    id: integer.positive()
    name: string

@model()
class Admin(BaseUser):
    role: string.default("admin")
    permissions: array(string)

# Admin has id, name, role, and permissions
admin = Admin(id=1, name="Super Admin", permissions=["read", "write"])
```

#### Field Helper

```python
from tyck import model, field, string

@model()
class User:
    name: field(
        string.min(1).max(100),
        alias="fullName",
        description="The user's full name",
        examples=["John Doe", "Jane Smith"]
    )
```

---

## Utility Functions

### pick()
Create a new model with only the specified fields.

```python
from tyck import interface, integer, string, pick

User = interface({
    'id': integer,
    'name': string,
    'email': string,
    'password': string,
})

# Pick only public fields
PublicUser = pick(User, 'id', 'name', 'email')
# PublicUser has: id, name, email
```

### omit()
Create a new model without the specified fields.

```python
from tyck import omit

# Omit sensitive fields
SafeUser = omit(User, 'password')
# SafeUser has: id, name, email
```

### partial()
Make all fields optional (useful for PATCH requests).

```python
from tyck import partial

# All fields are now optional
UserUpdate = partial(User)

# Update only specific fields
update = UserUpdate(name="New Name")
```

### required()
Make all fields required (remove defaults).

```python
from tyck import required

# All fields must be provided
StrictUser = required(User)
```

### extend()
Extend a model with new fields.

```python
from tyck import interface, integer, string, array, extend

User = interface({
    'id': integer,
    'name': string,
})

Admin = extend(User, {
    'role': string.default('admin'),
    'permissions': array(string),
})
# Admin has: id, name, role, permissions
```

### merge()
Merge multiple models into one.

```python
from tyck import interface, integer, string, merge

User = interface({'id': integer, 'name': string})
Profile = interface({'bio': string, 'avatar': string})

UserWithProfile = merge(User, Profile)
# Has: id, name, bio, avatar
```

---

## Configuration

### config() Helper

```python
from tyck import config

# Create configuration
cfg = config(
    strict=True,              # Strict type checking
    frozen=True,              # Immutable models
    extra='forbid',           # Forbid extra fields
    populate_by_name=True,    # Allow population by field name
    validate_assignment=True, # Validate on assignment
    str_to_lower=False,       # Convert strings to lowercase
    str_to_upper=False,       # Convert strings to uppercase
    str_strip_whitespace=True,# Strip whitespace from strings
    use_enum_values=True,     # Use enum values instead of instances
    validate_default=True,    # Validate default values
)
```

**Configuration Options:**
___________________________________________________________________________________
| Option                 | Type | Description                                     |
|------------------------|------|-------------------------------------------------|
| `strict`               | bool | Enable strict type checking                     |
| `frozen`               | bool | Make models immutable                           | 
| `extra`                | str  | Handle extra fields: 'ignore', 'allow', 'forbid'|
| `populate_by_name`     | bool | Allow population by field name                  |
| `validate_assignment`  | bool | Validate on field assignment                    |
| `str_to_lower`         | bool | Convert strings to lowercase                    |
| `str_to_upper`         | bool | Convert strings to uppercase                    |
| `str_strip_whitespace` | bool | Strip whitespace from strings                   |
| `use_enum_values`      | bool | Use enum values instead of instances            |
| `validate_default`     | bool | Validate default values                         |
___________________________________________________________________________________
---

## Validation & Serialization

### Validation

```python
from pydantic import ValidationError
from tyck import interface, string, number

User = interface({
    'email': string.email(),
    'age': number.gt(0).lt(150),
})

# Valid data
user = User(email="test@example.com", age=25)

# Invalid data raises ValidationError
try:
    invalid_user = User(email="invalid", age=-5)
except ValidationError as e:
    print(e.error_count())  # Number of errors
    for error in e.errors():
        print(f"{error['loc']}: {error['msg']}")
```

### Serialization

```python
user = User(email="test@example.com", age=25)

# To dictionary
data = user.model_dump()
# {'email': 'test@example.com', 'age': 25}

# To JSON
json_str = user.model_dump_json()
# '{"email":"test@example.com","age":25}'

# Exclude fields
data = user.model_dump(exclude={'age'})
# {'email': 'test@example.com'}

# Include only specific fields
json_str = user.model_dump_json(include={'email'})
# '{"email":"test@example.com"}'
```

---

## JSON Schema

```python
from tyck import interface, integer, string

User = interface({
    'id': integer.positive(),
    'name': string.min(1).max(100),
    'email': string.email(),
})

# Generate JSON Schema
schema = User.model_json_schema()

print(schema)
# {
#   'title': 'Interface_...',
#   'type': 'object',
#   'properties': {
#     'id': {'type': 'integer', 'exclusiveMinimum': 0},
#     'name': {'type': 'string', 'minLength': 1, 'maxLength': 100},
#     'email': {'type': 'string', 'format': 'email'}
#   },
#   'required': ['id', 'name', 'email']
# }
```

---

## Examples

### API Request/Response Models

```python
from tyck import interface, string, number, integer, optional, array, pick, omit, partial

# Request models
CreateUserRequest = interface({
    'name': string.min(1).max(100),
    'email': string.email(),
    'age': optional(number.gt(0).lt(150))
})

UpdateUserRequest = partial(CreateUserRequest)

# Response models
UserResponse = interface({
    'id': integer.positive(),
    'name': string,
    'email': string.email(),
    'created_at': string.datetime()
})

PublicUserResponse = omit(UserResponse, 'email')
```

### Configuration Models

```python
from tyck import interface, string, number, boolean, literal

DatabaseConfig = interface({
    'host': string.default('localhost'),
    'port': number.integer().range(1, 65535).default(5432),
    'username': string,
    'password': string,
    'ssl': boolean.default(False)
})

AppConfig = interface({
    'name': string,
    'debug': boolean.default(False),
    'database': DatabaseConfig,
    'log_level': literal('debug', 'info', 'warning', 'error').default('info')
})
```

### Nested Models

```python
from tyck import interface, string, number, array, optional

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
    'phone': optional(string.pattern(r'^\+?1?\d{9,15}$'))
})

# Create nested instance
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
```

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

Built on top of [Pydantic](https://docs.pydantic.dev/) - the most widely used data validation library for Python.

Inspired by TypeScript's type system and [Zod](https://zod.dev/)'s API design.
