"""Tyck - TypeScript-inspired fluent API for Pydantic validation

A clean, chainable API for defining Pydantic validation schemas.
Write less boilerplate, get better type safety.

Example:
    >>> from tyck import interface, String, Number, Integer
    >>> 
    >>> User = interface({
    ...     'id': Integer.positive(),
    ...     'name': String.min(1).max(100),
    ...     'email': String.email(),
    ...     'age': Number.gt(0).lt(150).default(None)
    ... })
    >>> 
    >>> user = User(id=1, name="John", email="john@example.com")
"""

from .types_ import (
    String,
    Number,
    Integer,
    Boolean,
    Array,
    OptionalType,
    Literal,
    Record,
    Union,
    AnyType,
)
from .interface import interface
from .model import model
from .utils import pick_fields, omit_fields, extend_fields, make_optional, merge

__version__ = "0.1.0"
__author__ = "Ansh Dadhich"
__email__ = "anshdadhichmm@gmail.com"

__all__ = [
    # Version
    "__version__",
    # Types
    "String",
    "Number",
    "Integer",
    "Boolean",
    "Array",
    "OptionalType",
    "Literal",
    "Record",
    "Union",
    "AnyType",
    # Functions
    "interface",
    "model",
    # Utils
    "pick_fields",
    "omit_fields",
    "extend_fields",
    "make_optional",
    "merge",
]
