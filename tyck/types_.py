"""Core type validators for Tyck.

This module provides TypeScript-inspired type validators that can be chained
to create complex validation schemas with minimal boilerplate.
"""

from typing import Any, Dict, List, Optional as TypingOptional, Set, Type, Union as TypingUnion, get_type_hints
from pydantic import Field, BaseModel
from pydantic.fields import FieldInfo
import re


class TyckType:
    """Base class for all Tyck type validators."""
    
    def __init__(self, constraints: Dict[str, Any] = None, default: Any = None, has_default: bool = False):
        self._constraints: Dict[str, Any] = constraints.copy() if constraints else {}
        self._default: Any = default
        self._has_default: bool = has_default
    
    def default(self, value: Any) -> "TyckType":
        """Set a default value for this field."""
        new = self._copy()
        new._default = value
        new._has_default = True
        return new
    
    def optional(self) -> "TyckType":
        """Make this field optional (equivalent to default(None))."""
        return self.default(None)
    
    def _copy(self) -> "TyckType":
        """Create a copy of this validator with the same constraints."""
        new = self.__class__.__new__(self.__class__)
        new._constraints = self._constraints.copy()
        new._default = self._default
        new._has_default = self._has_default
        return new
    
    def build(self):
        """Build and return a type annotation and FieldInfo tuple."""
        field_kwargs = self._constraints.copy()
        if self._has_default:
            field_kwargs['default'] = self._default
        return Field(**field_kwargs)


class StringValidator(TyckType):
    """String type validator with chainable constraints."""
    
    def __init__(self, constraints: Dict[str, Any] = None, default: Any = None, has_default: bool = False):
        super().__init__(constraints, default, has_default)
    
    def _copy(self) -> "StringValidator":
        """Create a copy of this validator with the same constraints."""
        new = StringValidator.__new__(StringValidator)
        new._constraints = self._constraints.copy()
        new._default = self._default
        new._has_default = self._has_default
        return new
    
    def build(self):
        """Build and return a type annotation and FieldInfo tuple."""
        field_kwargs = self._constraints.copy()
        if self._has_default:
            field_kwargs['default'] = self._default
        return (str, Field(**field_kwargs))
    
    def min(self, length: int) -> "StringValidator":
        """Set minimum string length."""
        new = self._copy()
        new._constraints['min_length'] = length
        return new
    
    def max(self, length: int) -> "StringValidator":
        """Set maximum string length."""
        new = self._copy()
        new._constraints['max_length'] = length
        return new
    
    def length(self, length: int) -> "StringValidator":
        """Set exact string length."""
        new = self._copy()
        new._constraints['min_length'] = length
        new._constraints['max_length'] = length
        return new
    
    def email(self) -> "StringValidator":
        """Validate as email address."""
        new = self._copy()
        new._constraints['pattern'] = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return new
    
    def url(self) -> "StringValidator":
        """Validate as URL."""
        new = self._copy()
        new._constraints['pattern'] = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
        return new
    
    def uuid(self) -> "StringValidator":
        """Validate as UUID."""
        new = self._copy()
        new._constraints['pattern'] = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
        return new
    
    def pattern(self, regex: str) -> "StringValidator":
        """Validate against regex pattern."""
        new = self._copy()
        new._constraints['pattern'] = regex
        return new
    
    def upper(self) -> "StringValidator":
        """Transform to uppercase."""
        new = self._copy()
        new._constraints['transform'] = 'upper'
        return new
    
    def lower(self) -> "StringValidator":
        """Transform to lowercase."""
        new = self._copy()
        new._constraints['transform'] = 'lower'
        return new
    
    def strip(self) -> "StringValidator":
        """Strip whitespace."""
        new = self._copy()
        new._constraints['strip_whitespace'] = True
        return new
    
    def datetime(self) -> "StringValidator":
        """Validate as ISO datetime string."""
        new = self._copy()
        new._constraints['pattern'] = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$'
        return new


class NumberValidator(TyckType):
    """Float/Number type validator with chainable constraints."""
    
    def __init__(self, constraints: Dict[str, Any] = None, default: Any = None, has_default: bool = False):
        super().__init__(constraints, default, has_default)
    
    def _copy(self) -> "NumberValidator":
        """Create a copy of this validator with the same constraints."""
        new = NumberValidator.__new__(NumberValidator)
        new._constraints = self._constraints.copy()
        new._default = self._default
        new._has_default = self._has_default
        return new
    
    def gt(self, value: float) -> "NumberValidator":
        """Greater than."""
        new = self._copy()
        new._constraints['gt'] = value
        return new
    
    def gte(self, value: float) -> "NumberValidator":
        """Greater than or equal."""
        new = self._copy()
        new._constraints['ge'] = value
        return new
    
    def lt(self, value: float) -> "NumberValidator":
        """Less than."""
        new = self._copy()
        new._constraints['lt'] = value
        return new
    
    def lte(self, value: float) -> "NumberValidator":
        """Less than or equal."""
        new = self._copy()
        new._constraints['le'] = value
        return new
    
    def range(self, min: float, max: float) -> "NumberValidator":
        """Set inclusive range."""
        new = self._copy()
        new._constraints['ge'] = min
        new._constraints['le'] = max
        return new
    
    def positive(self) -> "NumberValidator":
        """Must be positive (> 0)."""
        return self.gt(0)
    
    def non_negative(self) -> "NumberValidator":
        """Must be non-negative (>= 0)."""
        return self.gte(0)
    
    def negative(self) -> "NumberValidator":
        """Must be negative (< 0)."""
        return self.lt(0)
    
    def non_positive(self) -> "NumberValidator":
        """Must be non-positive (<= 0)."""
        return self.lte(0)
    
    def multiple_of(self, value: float) -> "NumberValidator":
        """Must be multiple of value."""
        new = self._copy()
        new._constraints['multiple_of'] = value
        return new
    
    def build(self):
        """Build and return a type annotation and FieldInfo tuple."""
        field_kwargs = self._constraints.copy()
        if self._has_default:
            field_kwargs['default'] = self._default
        return (float, Field(**field_kwargs))


class IntegerValidator(TyckType):
    """Integer type validator with chainable constraints."""
    
    def __init__(self, constraints: Dict[str, Any] = None, default: Any = None, has_default: bool = False):
        if constraints is None:
            constraints = {'strict': True}
        super().__init__(constraints, default, has_default)
    
    def _copy(self) -> "IntegerValidator":
        """Create a copy of this validator with the same constraints."""
        new = IntegerValidator.__new__(IntegerValidator)
        new._constraints = self._constraints.copy()
        new._default = self._default
        new._has_default = self._has_default
        return new
    
    def gt(self, value: int) -> "IntegerValidator":
        """Greater than."""
        new = self._copy()
        new._constraints['gt'] = value
        return new
    
    def gte(self, value: int) -> "IntegerValidator":
        """Greater than or equal."""
        new = self._copy()
        new._constraints['ge'] = value
        return new
    
    def lt(self, value: int) -> "IntegerValidator":
        """Less than."""
        new = self._copy()
        new._constraints['lt'] = value
        return new
    
    def lte(self, value: int) -> "IntegerValidator":
        """Less than or equal."""
        new = self._copy()
        new._constraints['le'] = value
        return new
    
    def range(self, min: int, max: int) -> "IntegerValidator":
        """Set inclusive range."""
        new = self._copy()
        new._constraints['ge'] = min
        new._constraints['le'] = max
        return new
    
    def positive(self) -> "IntegerValidator":
        """Must be positive (> 0)."""
        return self.gt(0)
    
    def non_negative(self) -> "IntegerValidator":
        """Must be non-negative (>= 0)."""
        return self.gte(0)
    
    def negative(self) -> "IntegerValidator":
        """Must be negative (< 0)."""
        return self.lt(0)
    
    def non_positive(self) -> "IntegerValidator":
        """Must be non-positive (<= 0)."""
        return self.lte(0)
    
    def multiple_of(self, value: int) -> "IntegerValidator":
        """Must be multiple of value."""
        new = self._copy()
        new._constraints['multiple_of'] = value
        return new
    
    def build(self):
        """Build and return a type annotation and FieldInfo tuple."""
        field_kwargs = self._constraints.copy()
        if self._has_default:
            field_kwargs['default'] = self._default
        return (int, Field(**field_kwargs))


class BooleanValidator(TyckType):
    """Boolean type validator."""
    
    def __init__(self, constraints: Dict[str, Any] = None, default: Any = None, has_default: bool = False):
        super().__init__(constraints, default, has_default)
    
    def _copy(self) -> "BooleanValidator":
        """Create a copy of this validator with the same constraints."""
        new = BooleanValidator.__new__(BooleanValidator)
        new._constraints = self._constraints.copy()
        new._default = self._default
        new._has_default = self._has_default
        return new
    
    def strict(self) -> "BooleanValidator":
        """Strict validation (no type coercion)."""
        new = self._copy()
        new._constraints['strict'] = True
        return new
    
    def build(self):
        """Build and return a type annotation and FieldInfo tuple."""
        field_kwargs = self._constraints.copy()
        if self._has_default:
            field_kwargs['default'] = self._default
        return (bool, Field(**field_kwargs))


class ArrayValidator(TyckType):
    """Array/List type validator with chainable constraints."""
    
    def __init__(self, item_type: Any = Any, constraints: Dict[str, Any] = None, default: Any = None, has_default: bool = False):
        super().__init__(constraints, default, has_default)
        self._item_type = item_type
    
    def _copy(self) -> "ArrayValidator":
        """Create a copy of this validator with the same constraints."""
        new = ArrayValidator.__new__(ArrayValidator)
        new._constraints = self._constraints.copy()
        new._default = self._default
        new._has_default = self._has_default
        new._item_type = self._item_type
        return new
    
    def min(self, length: int) -> "ArrayValidator":
        """Set minimum array length."""
        new = self._copy()
        new._constraints['min_length'] = length
        return new
    
    def max(self, length: int) -> "ArrayValidator":
        """Set maximum array length."""
        new = self._copy()
        new._constraints['max_length'] = length
        return new
    
    def length(self, length: int) -> "ArrayValidator":
        """Set exact array length."""
        new = self._copy()
        new._constraints['min_length'] = length
        new._constraints['max_length'] = length
        return new
    
    def unique(self) -> "ArrayValidator":
        """Require unique items."""
        new = self._copy()
        new._constraints['unique_items'] = True
        return new
    
    def build(self) -> FieldInfo:
        """Build and return a Pydantic FieldInfo with list type."""
        from typing import List
        field_kwargs = self._constraints.copy()
        if self._has_default:
            field_kwargs['default'] = self._default
        # Return a tuple of (type, Field) for use in interface()
        return (List[self._item_type], Field(**field_kwargs))


class OptionalValidator(TyckType):
    """Optional/Nullable type wrapper."""
    
    def __init__(self, wrapped_type: Any = Any, constraints: Dict[str, Any] = None, default: Any = None, has_default: bool = False):
        if constraints is None:
            constraints = {'default': None}
            has_default = True
        super().__init__(constraints, default, has_default)
        self._wrapped = wrapped_type
    
    def _copy(self) -> "OptionalValidator":
        """Create a copy of this validator with the same constraints."""
        new = OptionalValidator.__new__(OptionalValidator)
        new._constraints = self._constraints.copy()
        new._default = self._default
        new._has_default = self._has_default
        new._wrapped = self._wrapped
        return new
    
    def build(self) -> FieldInfo:
        """Build and return a Pydantic FieldInfo."""
        from typing import Optional as TypingOptional
        field_kwargs = self._constraints.copy()
        return (TypingOptional[self._wrapped], Field(**field_kwargs))


class LiteralValidator(TyckType):
    """Literal/Enum type validator."""
    
    def __init__(self, values: tuple = (), constraints: Dict[str, Any] = None, default: Any = None, has_default: bool = False):
        super().__init__(constraints, default, has_default)
        self._values = values
    
    def _copy(self) -> "LiteralValidator":
        """Create a copy of this validator with the same constraints."""
        new = LiteralValidator.__new__(LiteralValidator)
        new._constraints = self._constraints.copy()
        new._default = self._default
        new._has_default = self._has_default
        new._values = self._values
        return new
    
    def build(self) -> FieldInfo:
        """Build and return a Pydantic FieldInfo."""
        from typing import Literal as TypingLiteral
        field_kwargs = self._constraints.copy()
        if self._has_default:
            field_kwargs['default'] = self._default
        literal_type = TypingLiteral[self._values]
        return (literal_type, Field(**field_kwargs))


class RecordValidator(TyckType):
    """Record/Dict type validator."""
    
    def __init__(self, key_type: Type = str, value_type: Any = Any, constraints: Dict[str, Any] = None, default: Any = None, has_default: bool = False):
        super().__init__(constraints, default, has_default)
        self._key_type = key_type
        self._value_type = value_type
    
    def _copy(self) -> "RecordValidator":
        """Create a copy of this validator with the same constraints."""
        new = RecordValidator.__new__(RecordValidator)
        new._constraints = self._constraints.copy()
        new._default = self._default
        new._has_default = self._has_default
        new._key_type = self._key_type
        new._value_type = self._value_type
        return new
    
    def build(self) -> FieldInfo:
        """Build and return a Pydantic FieldInfo."""
        from typing import Dict
        field_kwargs = self._constraints.copy()
        if self._has_default:
            field_kwargs['default'] = self._default
        dict_type = Dict[self._key_type, self._value_type]
        return (dict_type, Field(**field_kwargs))


class UnionValidator(TyckType):
    """Union type validator (accepts multiple types)."""
    
    def __init__(self, types: tuple = (), constraints: Dict[str, Any] = None, default: Any = None, has_default: bool = False):
        super().__init__(constraints, default, has_default)
        self._types = types
    
    def _copy(self) -> "UnionValidator":
        """Create a copy of this validator with the same constraints."""
        new = UnionValidator.__new__(UnionValidator)
        new._constraints = self._constraints.copy()
        new._default = self._default
        new._has_default = self._has_default
        new._types = self._types
        return new
    
    def build(self) -> FieldInfo:
        """Build and return a Pydantic FieldInfo."""
        from typing import Union as TypingUnion
        field_kwargs = self._constraints.copy()
        if self._has_default:
            field_kwargs['default'] = self._default
        union_type = TypingUnion[self._types]
        return (union_type, Field(**field_kwargs))


class AnyValidator(TyckType):
    """Any type - accepts any value."""
    
    def __init__(self, constraints: Dict[str, Any] = None, default: Any = None, has_default: bool = False):
        super().__init__(constraints, default, has_default)
    
    def _copy(self) -> "AnyValidator":
        """Create a copy of this validator with the same constraints."""
        new = AnyValidator.__new__(AnyValidator)
        new._constraints = self._constraints.copy()
        new._default = self._default
        new._has_default = self._has_default
        return new
    
    def build(self) -> FieldInfo:
        """Build and return a Pydantic FieldInfo."""
        from typing import Any as TypingAny
        field_kwargs = self._constraints.copy()
        if self._has_default:
            field_kwargs['default'] = self._default
        return (TypingAny, Field(**field_kwargs))


# Module-level singleton instances for direct import and use
String = StringValidator()
Number = NumberValidator()
Integer = IntegerValidator()
Boolean = BooleanValidator()
Array = ArrayValidator()
OptionalType = OptionalValidator()
AnyType = AnyValidator()

# Factory functions for parameterized types
def Literal(*values: Any) -> LiteralValidator:
    """Create a Literal type validator with the given values."""
    return LiteralValidator(values)

def Record(key_type: Type = str, value_type: Any = Any) -> RecordValidator:
    """Create a Record/Dict type validator with the given key and value types."""
    return RecordValidator(key_type, value_type)

def Union(*types: Any) -> UnionValidator:
    """Create a Union type validator with the given types."""
    return UnionValidator(types)
