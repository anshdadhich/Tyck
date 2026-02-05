"""Tyck - TypeScript-inspired fluent API for Pydantic validation

A clean, chainable API for defining Pydantic validation schemas.
Write less boilerplate, get better type safety.

Example:
    >>> from tyck import interface, string, number, integer
    >>> 
    >>> User = interface({
    ...     'id': integer.positive(),
    ...     'name': string.min(1).max(100),
    ...     'email': string.email(),
    ...     'age': number.gt(0).lt(150).default(None)
    ... })
    >>> 
    >>> user = User(id=1, name="John", email="john@example.com")
"""

from .types_ import (
    # Singleton instances (lowercase - preferred)
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
    # PascalCase aliases (for backwards compatibility)
    String,
    Number,
    Integer,
    Boolean,
    DateTime,
    Date,
    Time,
    Uuid,
    Bytes,
    Decimal,
    AnyType,
    NoneType,
    # Factory functions (lowercase - preferred)
    array,
    optional,
    literal,
    dict_type,
    record,
    set_type,
    tuple_type,
    union,
    enum_type,
    # PascalCase factory aliases
    Array,
    Optional,
    Literal,
    Dict,
    Record,
    Set,
    Tuple,
    Union,
    Enum,
    # Validator classes (for type hints and advanced usage)
    TyckType,
    StringValidator,
    NumberValidator,
    BooleanValidator,
    DateTimeValidator,
    UUIDValidator,
    BytesValidator,
    DecimalValidator,
    AnyValidator,
    NoneValidator,
    ArrayValidator,
    OptionalValidator,
    LiteralValidator,
    RecordValidator,
    SetValidator,
    TupleValidator,
    UnionValidator,
    EnumValidator,
)

from .interface import interface, config
from .model import model, field

from .utils import (
    # Preferred function names (matching README)
    pick,
    omit,
    partial,
    required,
    extend,
    merge,
    # Legacy aliases
    pick_fields,
    omit_fields,
    make_optional,
    extend_fields,
    merge_fields,
)

__version__ = "0.1.0"
__author__ = "Ansh Dadhich"
__email__ = "anshdadhichmm@gmail.com"

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    
    # Core functions
    "interface",
    "config",
    "model",
    "field",
    
    # Primitive types (lowercase - preferred)
    "string",
    "number",
    "integer",
    "boolean",
    "datetime",
    "date",
    "time",
    "uuid",
    "bytes_type",
    "decimal",
    "any_type",
    "none_type",
    
    # PascalCase aliases
    "String",
    "Number",
    "Integer",
    "Boolean",
    "DateTime",
    "Date",
    "Time",
    "Uuid",
    "Bytes",
    "Decimal",
    "AnyType",
    "NoneType",
    
    # Complex type factories (lowercase - preferred)
    "array",
    "optional",
    "literal",
    "dict_type",
    "record",
    "set_type",
    "tuple_type",
    "union",
    "enum_type",
    
    # PascalCase factory aliases
    "Array",
    "Optional",
    "Literal",
    "Dict",
    "Record",
    "Set",
    "Tuple",
    "Union",
    "Enum",
    
    # Utility functions
    "pick",
    "omit",
    "partial",
    "required",
    "extend",
    "merge",
    
    # Legacy utility aliases
    "pick_fields",
    "omit_fields",
    "make_optional",
    "extend_fields",
    "merge_fields",
    
    # Validator classes (for advanced usage)
    "TyckType",
    "StringValidator",
    "NumberValidator",
    "BooleanValidator",
    "DateTimeValidator",
    "UUIDValidator",
    "BytesValidator",
    "DecimalValidator",
    "AnyValidator",
    "NoneValidator",
    "ArrayValidator",
    "OptionalValidator",
    "LiteralValidator",
    "RecordValidator",
    "SetValidator",
    "TupleValidator",
    "UnionValidator",
    "EnumValidator",
]
