"""Core type validators for Tyck.

This module provides TypeScript-inspired type validators that can be chained
to create complex validation schemas with minimal boilerplate.
"""

from __future__ import annotations

import copy
import json
import re
from abc import ABC, abstractmethod
from datetime import date as _date, datetime as _datetime, time as _time
from decimal import Decimal as _Decimal
from enum import Enum as _Enum
from typing import Annotated, Any, Callable, Dict as TypingDict, List, Optional as TypingOptional, Set as TypingSet, Tuple as TypingTuple, Type, Union as TypingUnion
from uuid import UUID as _UUID

from pydantic import Field, BaseModel, field_validator, BeforeValidator, AfterValidator
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
import math


class TyckType(ABC):
    """Base class for all Tyck type validators."""
    
    def __init__(self):
        self._constraints: Dict[str, Any] = {}
        self._default: Any = PydanticUndefined
        self._has_default: bool = False
        self._alias: TypingOptional[str] = None
        self._description: TypingOptional[str] = None
        self._title: TypingOptional[str] = None
        self._examples: TypingOptional[List[Any]] = None
        self._deprecated: bool = False
    
    def _copy(self) -> "TyckType":
        """Create a copy of this validator with the same constraints."""
        new = copy.copy(self)
        new._constraints = self._constraints.copy()
        if hasattr(self, '_examples') and self._examples:
            new._examples = self._examples.copy()
        return new
    
    def default(self, value: Any) -> "TyckType":
        """Set a default value for this field."""
        new = self._copy()
        new._default = value
        new._has_default = True
        return new
    
    def optional(self) -> "TyckType":
        """Make this field optional (equivalent to default(None))."""
        return self.default(None)
    
    def alias(self, name: str) -> "TyckType":
        """Set an alias for this field."""
        new = self._copy()
        new._alias = name
        return new
    
    def description(self, text: str) -> "TyckType":
        """Set a description for this field."""
        new = self._copy()
        new._description = text
        return new
    
    def title(self, text: str) -> "TyckType":
        """Set a title for this field."""
        new = self._copy()
        new._title = text
        return new
    
    def examples(self, *values: Any) -> "TyckType":
        """Set example values for this field."""
        new = self._copy()
        new._examples = list(values)
        return new
    
    def deprecated(self, is_deprecated: bool = True) -> "TyckType":
        """Mark this field as deprecated."""
        new = self._copy()
        new._deprecated = is_deprecated
        return new
    
    def _build_field_kwargs(self) -> TypingDict[str, Any]:
        """Build common field kwargs."""
        kwargs: TypingDict[str, Any] = {}
        
        if self._has_default:
            kwargs['default'] = self._default
        
        if self._alias:
            kwargs['alias'] = self._alias
        if self._description:
            kwargs['description'] = self._description
        if self._title:
            kwargs['title'] = self._title
        if self._examples:
            kwargs['examples'] = self._examples
        if self._deprecated:
            kwargs['deprecated'] = self._deprecated
            
        return kwargs
    
    @abstractmethod
    def build(self) -> Tuple[Type, FieldInfo]:
        """Build and return a type annotation and FieldInfo tuple."""
        pass


class StringValidator(TyckType):
    """String type validator with chainable constraints."""
    
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    URL_PATTERN = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.\-~%])*(?:\?(?:[\w&=%.\-])*)?(?:#(?:[\w.\-])*)?)?$'
    UUID_PATTERN = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    DATETIME_PATTERN = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$'
    DATE_PATTERN = r'^\d{4}-\d{2}-\d{2}$'
    TIME_PATTERN = r'^\d{2}:\d{2}:\d{2}(?:\.\d+)?$'
    IPV4_PATTERN = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    IPV6_PATTERN = r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    
    def __init__(self):
        super().__init__()
        self._min_length: TypingOptional[int] = None
        self._max_length: TypingOptional[int] = None
        self._pattern: TypingOptional[str] = None
        self._strip_whitespace: bool = False
        self._to_lower: bool = False
        self._to_upper: bool = False
    
    def _copy(self) -> "StringValidator":
        new = super()._copy()
        new._min_length = self._min_length
        new._max_length = self._max_length
        new._pattern = self._pattern
        new._strip_whitespace = self._strip_whitespace
        new._to_lower = self._to_lower
        new._to_upper = self._to_upper
        return new
    
    def min(self, length: int) -> "StringValidator":
        """Set minimum string length."""
        new = self._copy()
        new._min_length = length
        return new
    
    def max(self, length: int) -> "StringValidator":
        """Set maximum string length."""
        new = self._copy()
        new._max_length = length
        return new
    
    def length(self, length: int) -> "StringValidator":
        """Set exact string length."""
        new = self._copy()
        new._min_length = length
        new._max_length = length
        return new
    
    def email(self) -> "StringValidator":
        """Validate as email address."""
        new = self._copy()
        new._pattern = self.EMAIL_PATTERN
        return new
    
    def url(self) -> "StringValidator":
        """Validate as URL."""
        new = self._copy()
        new._pattern = self.URL_PATTERN
        return new
    
    def uuid(self) -> "StringValidator":
        """Validate as UUID."""
        new = self._copy()
        new._pattern = self.UUID_PATTERN
        return new
    
    def pattern(self, regex: str) -> "StringValidator":
        """Validate against regex pattern."""
        new = self._copy()
        new._pattern = regex
        return new
    
    def datetime(self) -> "StringValidator":
        """Validate as ISO datetime string."""
        new = self._copy()
        new._pattern = self.DATETIME_PATTERN
        return new
    
    def date(self) -> "StringValidator":
        """Validate as ISO date string."""
        new = self._copy()
        new._pattern = self.DATE_PATTERN
        return new
    
    def time(self) -> "StringValidator":
        """Validate as ISO time string."""
        new = self._copy()
        new._pattern = self.TIME_PATTERN
        return new
    
    def ip(self, version: TypingOptional[int] = None) -> "StringValidator":
        """Validate as IP address."""
        new = self._copy()
        if version == 4:
            new._pattern = self.IPV4_PATTERN
        elif version == 6:
            new._pattern = self.IPV6_PATTERN
        else:
            new._pattern = f'({self.IPV4_PATTERN})|({self.IPV6_PATTERN})'
        return new
    
    def json(self) -> "StringValidator":
        """Validate as JSON string."""
        new = self._copy()
        new._constraints['json_validate'] = True
        return new
    
    def strip(self) -> "StringValidator":
        """Strip whitespace from string."""
        new = self._copy()
        new._strip_whitespace = True
        return new
    
    def lower(self) -> "StringValidator":
        """Convert string to lowercase."""
        new = self._copy()
        new._to_lower = True
        return new
    
    def upper(self) -> "StringValidator":
        """Convert string to uppercase."""
        new = self._copy()
        new._to_upper = True
        return new
    
    def build(self) -> TypingTuple[Type, FieldInfo]:
        """Build and return a type annotation and FieldInfo tuple."""
        kwargs = self._build_field_kwargs()
        
        if self._min_length is not None:
            kwargs['min_length'] = self._min_length
        if self._max_length is not None:
            kwargs['max_length'] = self._max_length
        if self._pattern is not None:
            kwargs['pattern'] = self._pattern
        
        # Build the base type
        base_type: Type = str
        
        # Apply transformations using Annotated with validators
        validators_to_apply = []
        
        # String transformations (before validation)
        if self._strip_whitespace or self._to_lower or self._to_upper:
            strip_ws = self._strip_whitespace
            to_lower = self._to_lower
            to_upper = self._to_upper
            
            def string_transform(v: Any) -> Any:
                if isinstance(v, str):
                    if strip_ws:
                        v = v.strip()
                    if to_lower:
                        v = v.lower()
                    if to_upper:
                        v = v.upper()
                return v
            
            validators_to_apply.append(BeforeValidator(string_transform))
        
        # JSON validation (after other validations)
        if self._constraints.get('json_validate'):
            def validate_json(v: str) -> str:
                try:
                    json.loads(v)
                except json.JSONDecodeError as e:
                    raise ValueError(f'Invalid JSON string: {e}')
                return v
            
            validators_to_apply.append(AfterValidator(validate_json))
        
        # If we have validators, wrap with Annotated
        if validators_to_apply:
            base_type = Annotated[str, *validators_to_apply]
        
        return (base_type, Field(**kwargs))


class NumberValidator(TyckType):
    """Float/Number type validator with chainable constraints."""
    
    def __init__(self, is_integer: bool = False):
        super().__init__()
        self._is_integer = is_integer
        self._gt: TypingOptional[float] = None
        self._ge: TypingOptional[float] = None
        self._lt: TypingOptional[float] = None
        self._le: TypingOptional[float] = None
        self._multiple_of: TypingOptional[float] = None
        self._allow_inf_nan: bool = True
    
    def _copy(self) -> "NumberValidator":
        new = super()._copy()
        new._is_integer = self._is_integer
        new._gt = self._gt
        new._ge = self._ge
        new._lt = self._lt
        new._le = self._le
        new._multiple_of = self._multiple_of
        new._allow_inf_nan = self._allow_inf_nan
        return new
    
    def integer(self) -> "NumberValidator":
        """Require integer values."""
        new = self._copy()
        new._is_integer = True
        return new
    
    def gt(self, value: float) -> "NumberValidator":
        """Greater than."""
        new = self._copy()
        new._gt = value
        return new
    
    def gte(self, value: float) -> "NumberValidator":
        """Greater than or equal."""
        new = self._copy()
        new._ge = value
        return new
    
    def lt(self, value: float) -> "NumberValidator":
        """Less than."""
        new = self._copy()
        new._lt = value
        return new
    
    def lte(self, value: float) -> "NumberValidator":
        """Less than or equal."""
        new = self._copy()
        new._le = value
        return new
    
    def range(self, min_val: float, max_val: float) -> "NumberValidator":
        """Set inclusive range (gte + lte)."""
        new = self._copy()
        new._ge = min_val
        new._le = max_val
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
    
    def finite(self) -> "NumberValidator":
        """Must be finite (not inf/NaN)."""
        new = self._copy()
        new._allow_inf_nan = False
        return new
    
    def multiple_of(self, value: float) -> "NumberValidator":
        """Must be multiple of value."""
        new = self._copy()
        new._multiple_of = value
        return new
    
    def build(self) -> TypingTuple[Type, FieldInfo]:
        """Build and return a type annotation and FieldInfo tuple."""
        kwargs = self._build_field_kwargs()
        
        if self._gt is not None:
            kwargs['gt'] = self._gt
        if self._ge is not None:
            kwargs['ge'] = self._ge
        if self._lt is not None:
            kwargs['lt'] = self._lt
        if self._le is not None:
            kwargs['le'] = self._le
        if self._multiple_of is not None:
            kwargs['multiple_of'] = self._multiple_of
        
        base_type = int if self._is_integer else float
        
        # Handle finite constraint (reject inf/NaN)
        if not self._allow_inf_nan:
            def check_finite(v: Any) -> Any:
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    if math.isinf(v) or math.isnan(v):
                        raise ValueError('Value must be finite (not infinity or NaN)')
                return v
            
            base_type = Annotated[base_type, AfterValidator(check_finite)]
        
        return (base_type, Field(**kwargs))


class BooleanValidator(TyckType):
    """Boolean type validator."""
    
    def __init__(self):
        super().__init__()
        self._strict: bool = False
    
    def _copy(self) -> "BooleanValidator":
        new = super()._copy()
        new._strict = self._strict
        return new
    
    def strict(self) -> "BooleanValidator":
        """Strict validation (no type coercion)."""
        new = self._copy()
        new._strict = True
        return new
    
    def build(self) -> Tuple[Type, FieldInfo]:
        """Build and return a type annotation and FieldInfo tuple."""
        kwargs = self._build_field_kwargs()
        if self._strict:
            kwargs['strict'] = True
        return (bool, Field(**kwargs))


class DateTimeValidator(TyckType):
    """DateTime type validator."""
    
    def __init__(self, type_: str = 'datetime'):
        super().__init__()
        self._type = type_
    
    def _copy(self) -> "DateTimeValidator":
        new = super()._copy()
        new._type = self._type
        return new
    
    def build(self) -> Tuple[Type, FieldInfo]:
        """Build and return a type annotation and FieldInfo tuple."""
        kwargs = self._build_field_kwargs()
        
        if self._type == 'datetime':
            return (_datetime, Field(**kwargs))
        elif self._type == 'date':
            return (_date, Field(**kwargs))
        elif self._type == 'time':
            return (_time, Field(**kwargs))
        return (_datetime, Field(**kwargs))


class UUIDValidator(TyckType):
    """UUID type validator."""
    
    def build(self) -> Tuple[Type, FieldInfo]:
        """Build and return a type annotation and FieldInfo tuple."""
        kwargs = self._build_field_kwargs()
        return (_UUID, Field(**kwargs))


class BytesValidator(TyckType):
    """Bytes type validator."""
    
    def __init__(self):
        super().__init__()
        self._min_length: TypingOptional[int] = None
        self._max_length: TypingOptional[int] = None
    
    def _copy(self) -> "BytesValidator":
        new = super()._copy()
        new._min_length = self._min_length
        new._max_length = self._max_length
        return new
    
    def min(self, length: int) -> "BytesValidator":
        """Set minimum bytes length."""
        new = self._copy()
        new._min_length = length
        return new
    
    def max(self, length: int) -> "BytesValidator":
        """Set maximum bytes length."""
        new = self._copy()
        new._max_length = length
        return new
    
    def build(self) -> Tuple[Type, FieldInfo]:
        """Build and return a type annotation and FieldInfo tuple."""
        kwargs = self._build_field_kwargs()
        if self._min_length is not None:
            kwargs['min_length'] = self._min_length
        if self._max_length is not None:
            kwargs['max_length'] = self._max_length
        return (bytes, Field(**kwargs))


class DecimalValidator(TyckType):
    """Decimal type validator."""
    
    def __init__(self):
        super().__init__()
        self._max_digits: TypingOptional[int] = None
        self._decimal_places: TypingOptional[int] = None
        self._gt: TypingOptional[_Decimal] = None
        self._ge: TypingOptional[_Decimal] = None
        self._lt: TypingOptional[_Decimal] = None
        self._le: TypingOptional[_Decimal] = None
    
    def _copy(self) -> "DecimalValidator":
        new = super()._copy()
        new._max_digits = self._max_digits
        new._decimal_places = self._decimal_places
        new._gt = self._gt
        new._ge = self._ge
        new._lt = self._lt
        new._le = self._le
        return new
    
    def max_digits(self, value: int) -> "DecimalValidator":
        """Set maximum total digits."""
        new = self._copy()
        new._max_digits = value
        return new
    
    def decimal_places(self, value: int) -> "DecimalValidator":
        """Set maximum decimal places."""
        new = self._copy()
        new._decimal_places = value
        return new
    
    def gt(self, value: Any) -> "DecimalValidator":
        """Greater than."""
        new = self._copy()
        new._gt = _Decimal(str(value))
        return new
    
    def gte(self, value: Any) -> "DecimalValidator":
        """Greater than or equal."""
        new = self._copy()
        new._ge = _Decimal(str(value))
        return new
    
    def lt(self, value: Any) -> "DecimalValidator":
        """Less than."""
        new = self._copy()
        new._lt = _Decimal(str(value))
        return new
    
    def lte(self, value: Any) -> "DecimalValidator":
        """Less than or equal."""
        new = self._copy()
        new._le = _Decimal(str(value))
        return new
    
    def build(self) -> Tuple[Type, FieldInfo]:
        """Build and return a type annotation and FieldInfo tuple."""
        kwargs = self._build_field_kwargs()
        if self._max_digits is not None:
            kwargs['max_digits'] = self._max_digits
        if self._decimal_places is not None:
            kwargs['decimal_places'] = self._decimal_places
        if self._gt is not None:
            kwargs['gt'] = self._gt
        if self._ge is not None:
            kwargs['ge'] = self._ge
        if self._lt is not None:
            kwargs['lt'] = self._lt
        if self._le is not None:
            kwargs['le'] = self._le
        return (_Decimal, Field(**kwargs))


class AnyValidator(TyckType):
    """Any type validator - accepts any value."""
    
    def build(self) -> Tuple[Type, FieldInfo]:
        """Build and return a type annotation and FieldInfo tuple."""
        kwargs = self._build_field_kwargs()
        return (Any, Field(**kwargs))


class NoneValidator(TyckType):
    """None type validator."""
    
    def build(self) -> Tuple[Type, FieldInfo]:
        """Build and return a type annotation and FieldInfo tuple."""
        kwargs = self._build_field_kwargs()
        kwargs['default'] = None
        return (type(None), Field(**kwargs))


class ArrayValidator(TyckType):
    """Array/List type validator with chainable constraints."""
    
    def __init__(self, item_type: Any = Any):
        super().__init__()
        self._item_type = item_type
        self._min_length: TypingOptional[int] = None
        self._max_length: TypingOptional[int] = None
        self._unique: bool = False
    
    def _copy(self) -> "ArrayValidator":
        new = super()._copy()
        new._item_type = self._item_type
        new._min_length = self._min_length
        new._max_length = self._max_length
        new._unique = self._unique
        return new
    
    def min(self, length: int) -> "ArrayValidator":
        """Set minimum array length."""
        new = self._copy()
        new._min_length = length
        return new
    
    def max(self, length: int) -> "ArrayValidator":
        """Set maximum array length."""
        new = self._copy()
        new._max_length = length
        return new
    
    def length(self, length: int) -> "ArrayValidator":
        """Set exact array length."""
        new = self._copy()
        new._min_length = length
        new._max_length = length
        return new
    
    def unique(self) -> "ArrayValidator":
        """Require unique items."""
        new = self._copy()
        new._unique = True
        return new
    
    def build(self) -> TypingTuple[Type, FieldInfo]:
        """Build and return a type annotation and FieldInfo tuple."""
        kwargs = self._build_field_kwargs()
        
        if self._min_length is not None:
            kwargs['min_length'] = self._min_length
        if self._max_length is not None:
            kwargs['max_length'] = self._max_length
        
        item_type = self._resolve_type(self._item_type)
        base_type = List[item_type]
        
        # Handle unique constraint
        if self._unique:
            def check_unique(v: Any) -> Any:
                if isinstance(v, list):
                    # Try to check for duplicates (works for hashable items)
                    try:
                        if len(v) != len(set(v)):
                            raise ValueError('Array items must be unique')
                    except TypeError:
                        # Items not hashable, do O(n^2) comparison
                        for i, item in enumerate(v):
                            for j, other in enumerate(v):
                                if i < j and item == other:
                                    raise ValueError('Array items must be unique')
                return v
            
            base_type = Annotated[List[item_type], AfterValidator(check_unique)]
        
        return (base_type, Field(**kwargs))
    
    def _resolve_type(self, t: Any) -> Any:
        """Resolve a TyckType to its Python type annotation."""
        if isinstance(t, TyckType):
            result = t.build()
            return result[0]
        elif isinstance(t, type) and issubclass(t, BaseModel):
            return t
        return t


class OptionalValidator(TyckType):
    """Optional/Nullable type wrapper."""
    
    def __init__(self, wrapped_type: Any = Any):
        super().__init__()
        self._wrapped = wrapped_type
        self._default = None
        self._has_default = True
    
    def _copy(self) -> "OptionalValidator":
        new = super()._copy()
        new._wrapped = self._wrapped
        return new
    
    def build(self) -> Tuple[Type, FieldInfo]:
        """Build and return a type annotation and FieldInfo tuple."""
        kwargs = self._build_field_kwargs()
        
        inner_type = self._resolve_type(self._wrapped)
        return (TypingOptional[inner_type], Field(**kwargs))
    
    def _resolve_type(self, t: Any) -> Any:
        """Resolve a TyckType to its Python type annotation."""
        if isinstance(t, TyckType):
            result = t.build()
            return result[0]
        elif isinstance(t, type) and issubclass(t, BaseModel):
            return t
        return t


class LiteralValidator(TyckType):
    """Literal/Enum type validator."""
    
    def __init__(self, *values: Any):
        super().__init__()
        self._values = values
    
    def _copy(self) -> "LiteralValidator":
        new = super()._copy()
        new._values = self._values
        return new
    
    def build(self) -> Tuple[Type, FieldInfo]:
        """Build and return a type annotation and FieldInfo tuple."""
        from typing import Literal as TypingLiteral
        kwargs = self._build_field_kwargs()
        
        if len(self._values) == 1:
            literal_type = TypingLiteral[self._values[0]]
        else:
            literal_type = TypingLiteral[self._values]
        return (literal_type, Field(**kwargs))


class RecordValidator(TyckType):
    """Record/Dict type validator."""
    
    def __init__(self, key_type: Any = str, value_type: Any = Any):
        super().__init__()
        self._key_type = key_type
        self._value_type = value_type
        self._min_length: TypingOptional[int] = None
        self._max_length: TypingOptional[int] = None
    
    def _copy(self) -> "RecordValidator":
        new = super()._copy()
        new._key_type = self._key_type
        new._value_type = self._value_type
        new._min_length = self._min_length
        new._max_length = self._max_length
        return new
    
    def min(self, length: int) -> "RecordValidator":
        """Set minimum key-value pairs."""
        new = self._copy()
        new._min_length = length
        return new
    
    def max(self, length: int) -> "RecordValidator":
        """Set maximum key-value pairs."""
        new = self._copy()
        new._max_length = length
        return new
    
    def build(self) -> Tuple[Type, FieldInfo]:
        """Build and return a type annotation and FieldInfo tuple."""
        kwargs = self._build_field_kwargs()
        if self._min_length is not None:
            kwargs['min_length'] = self._min_length
        if self._max_length is not None:
            kwargs['max_length'] = self._max_length
        
        key_type = self._resolve_type(self._key_type)
        value_type = self._resolve_type(self._value_type)
        return (TypingDict[key_type, value_type], Field(**kwargs))
    
    def _resolve_type(self, t: Any) -> Any:
        if isinstance(t, TyckType):
            result = t.build()
            return result[0]
        return t


class SetValidator(TyckType):
    """Set type validator."""
    
    def __init__(self, item_type: Any = Any):
        super().__init__()
        self._item_type = item_type
        self._min_length: TypingOptional[int] = None
        self._max_length: TypingOptional[int] = None
    
    def _copy(self) -> "SetValidator":
        new = super()._copy()
        new._item_type = self._item_type
        new._min_length = self._min_length
        new._max_length = self._max_length
        return new
    
    def min(self, length: int) -> "SetValidator":
        """Set minimum set size."""
        new = self._copy()
        new._min_length = length
        return new
    
    def max(self, length: int) -> "SetValidator":
        """Set maximum set size."""
        new = self._copy()
        new._max_length = length
        return new
    
    def build(self) -> Tuple[Type, FieldInfo]:
        """Build and return a type annotation and FieldInfo tuple."""
        kwargs = self._build_field_kwargs()
        if self._min_length is not None:
            kwargs['min_length'] = self._min_length
        if self._max_length is not None:
            kwargs['max_length'] = self._max_length
        
        item_type = self._resolve_type(self._item_type)
        return (TypingSet[item_type], Field(**kwargs))
    
    def _resolve_type(self, t: Any) -> Any:
        if isinstance(t, TyckType):
            result = t.build()
            return result[0]
        return t


class TupleValidator(TyckType):
    """Tuple type validator."""
    
    def __init__(self, *item_types: Any):
        super().__init__()
        self._item_types = item_types
    
    def _copy(self) -> "TupleValidator":
        new = super()._copy()
        new._item_types = self._item_types
        return new
    
    def build(self) -> Tuple[Type, FieldInfo]:
        """Build and return a type annotation and FieldInfo tuple."""
        kwargs = self._build_field_kwargs()
        
        resolved_types = tuple(self._resolve_type(t) for t in self._item_types)
        if resolved_types:
            tuple_type = TypingTuple[resolved_types]
        else:
            tuple_type = TypingTuple
        return (tuple_type, Field(**kwargs))
    
    def _resolve_type(self, t: Any) -> Any:
        if isinstance(t, TyckType):
            result = t.build()
            return result[0]
        return t


class UnionValidator(TyckType):
    """Union type validator."""
    
    def __init__(self, *types: Any):
        super().__init__()
        self._types = types
    
    def _copy(self) -> "UnionValidator":
        new = super()._copy()
        new._types = self._types
        return new
    
    def build(self) -> Tuple[Type, FieldInfo]:
        """Build and return a type annotation and FieldInfo tuple."""
        kwargs = self._build_field_kwargs()
        
        resolved_types = tuple(self._resolve_type(t) for t in self._types)
        union_type = TypingUnion[resolved_types]
        return (union_type, Field(**kwargs))
    
    def _resolve_type(self, t: Any) -> Any:
        if isinstance(t, TyckType):
            result = t.build()
            return result[0]
        return t


class EnumValidator(TyckType):
    """Enum type validator."""
    
    def __init__(self, enum_class: Type[_Enum]):
        super().__init__()
        self._enum_class = enum_class
    
    def _copy(self) -> "EnumValidator":
        new = super()._copy()
        new._enum_class = self._enum_class
        return new
    
    def build(self) -> Tuple[Type, FieldInfo]:
        """Build and return a type annotation and FieldInfo tuple."""
        kwargs = self._build_field_kwargs()
        return (self._enum_class, Field(**kwargs))


# Singleton instances for direct import
string = StringValidator()
number = NumberValidator(is_integer=False)
integer = NumberValidator(is_integer=True)
boolean = BooleanValidator()
datetime = DateTimeValidator('datetime')
date = DateTimeValidator('date')
time = DateTimeValidator('time')
uuid = UUIDValidator()
bytes_type = BytesValidator()
decimal = DecimalValidator()
any_type = AnyValidator()
none_type = NoneValidator()

# Also export as PascalCase for backwards compatibility
String = string
Number = number
Integer = integer
Boolean = boolean
DateTime = datetime
Date = date
Time = time
Uuid = uuid
Bytes = bytes_type
Decimal = decimal
AnyType = any_type
NoneType = none_type


# Factory functions for parameterized types
def array(item_type: Any) -> ArrayValidator:
    """Create an array/list type validator."""
    return ArrayValidator(item_type)


def optional(wrapped_type: Any) -> OptionalValidator:
    """Create an optional type validator."""
    return OptionalValidator(wrapped_type)


def literal(*values: Any) -> LiteralValidator:
    """Create a literal type validator."""
    return LiteralValidator(*values)


def dict_type(key_type: Any = str, value_type: Any = Any) -> RecordValidator:
    """Create a dictionary type validator."""
    return RecordValidator(key_type, value_type)


def record(key_type: Any = str, value_type: Any = Any) -> RecordValidator:
    """Create a record/dict type validator (alias for dict_type)."""
    return RecordValidator(key_type, value_type)


def set_type(item_type: Any) -> SetValidator:
    """Create a set type validator."""
    return SetValidator(item_type)


def tuple_type(*item_types: Any) -> TupleValidator:
    """Create a tuple type validator."""
    return TupleValidator(*item_types)


def union(*types: Any) -> UnionValidator:
    """Create a union type validator."""
    return UnionValidator(*types)


def enum_type(enum_class: Type[_Enum]) -> EnumValidator:
    """Create an enum type validator."""
    return EnumValidator(enum_class)


# PascalCase factory aliases
Array = array
Optional = optional
Literal = literal
Dict = dict_type
Record = record
Set = set_type
Tuple = tuple_type
Union = union
Enum = enum_type
