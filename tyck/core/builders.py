"""Core type builder implementations for Tyck."""

from __future__ import annotations

import copy
import re
from abc import ABC, abstractmethod
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union, cast, get_args, get_origin
from uuid import UUID

from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined, core_schema


class TypeBuilder(ABC):
    """Base class for all type builders."""
    
    def __init__(self):
        self._default = PydanticUndefined
        self._alias: Optional[str] = None
        self._description: Optional[str] = None
        self._title: Optional[str] = None
        self._examples: Optional[list] = None
        self._deprecated: bool = False
    
    def _clone(self):
        """Create a copy of this builder with the same state."""
        return copy.copy(self)
    
    @abstractmethod
    def to_field_info(self) -> tuple[type, FieldInfo]:
        """Convert this builder to a tuple of (type_annotation, FieldInfo)."""
        pass
    
    @property
    @abstractmethod
    def _annotation_type(self) -> type:
        """Return the Python type annotation for this builder."""
        pass
    
    def __get_pydantic_core_schema__(
        self, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Allow Pydantic to understand TypeBuilder objects in annotations.
        
        This method is called when Pydantic encounters a TypeBuilder as a type annotation.
        It converts the TypeBuilder to a proper Pydantic schema.
        """
        # Get the field type and info from the builder
        field_type, field_info = self.to_field_info()
        
        # Generate schema for the underlying type
        return handler(field_type)
    
    def default(self, value: Any) -> 'TypeBuilder':
        """Set a default value for this field."""
        new_builder = self._clone()
        new_builder._default = value
        return new_builder
    
    def alias(self, name: str) -> 'TypeBuilder':
        """Set an alias for this field."""
        new_builder = self._clone()
        new_builder._alias = name
        return new_builder
    
    def description(self, text: str) -> 'TypeBuilder':
        """Set a description for this field."""
        new_builder = self._clone()
        new_builder._description = text
        return new_builder
    
    def title(self, text: str) -> 'TypeBuilder':
        """Set a title for this field."""
        new_builder = self._clone()
        new_builder._title = text
        return new_builder
    
    def examples(self, *examples: Any) -> 'TypeBuilder':
        """Set examples for this field."""
        new_builder = self._clone()
        new_builder._examples = list(examples)
        return new_builder
    
    def deprecated(self, is_deprecated: bool = True) -> 'TypeBuilder':
        """Mark this field as deprecated."""
        new_builder = self._clone()
        new_builder._deprecated = is_deprecated
        return new_builder
    
    def _build_field_kwargs(self) -> Dict[str, Any]:
        """Build common field kwargs."""
        kwargs: Dict[str, Any] = {'default': self._default}
        
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


class StringBuilder(TypeBuilder):
    """Builder for string types with constraints."""
    
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    URL_PATTERN = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    UUID_PATTERN = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    
    def __init__(self):
        super().__init__()
        self._min_length: Optional[int] = None
        self._max_length: Optional[int] = None
        self._pattern: Optional[str] = None
        self._format: Optional[str] = None
        self._strip_whitespace: bool = False
        self._to_lower: bool = False
        self._to_upper: bool = False
    
    @property
    def _annotation_type(self) -> type:
        return str
    
    def min(self, length: int) -> 'StringBuilder':
        """Set minimum string length."""
        new_builder = cast(StringBuilder, self._clone())
        new_builder._min_length = length
        return new_builder
    
    def max(self, length: int) -> 'StringBuilder':
        """Set maximum string length."""
        new_builder = cast(StringBuilder, self._clone())
        new_builder._max_length = length
        return new_builder
    
    def length(self, exact: int) -> 'StringBuilder':
        """Set exact string length."""
        new_builder = cast(StringBuilder, self._clone())
        new_builder._min_length = exact
        new_builder._max_length = exact
        return new_builder
    
    def pattern(self, regex: str) -> 'StringBuilder':
        """Set regex pattern constraint."""
        new_builder = cast(StringBuilder, self._clone())
        new_builder._pattern = regex
        return new_builder
    
    def email(self) -> 'StringBuilder':
        """Set email format constraint."""
        new_builder = cast(StringBuilder, self._clone())
        new_builder._pattern = self.EMAIL_PATTERN
        new_builder._format = 'email'
        return new_builder
    
    def url(self) -> 'StringBuilder':
        """Set URL format constraint."""
        new_builder = cast(StringBuilder, self._clone())
        new_builder._pattern = self.URL_PATTERN
        new_builder._format = 'uri'
        return new_builder
    
    def uuid(self) -> 'StringBuilder':
        """Set UUID format constraint."""
        new_builder = cast(StringBuilder, self._clone())
        new_builder._pattern = self.UUID_PATTERN
        return new_builder
    
    def datetime(self) -> 'StringBuilder':
        """Set ISO datetime format constraint."""
        new_builder = cast(StringBuilder, self._clone())
        new_builder._format = 'date-time'
        return new_builder
    
    def date(self) -> 'StringBuilder':
        """Set ISO date format constraint."""
        new_builder = cast(StringBuilder, self._clone())
        new_builder._format = 'date'
        return new_builder
    
    def time(self) -> 'StringBuilder':
        """Set ISO time format constraint."""
        new_builder = cast(StringBuilder, self._clone())
        new_builder._format = 'time'
        return new_builder
    
    def ip(self, version: Optional[int] = None) -> 'StringBuilder':
        """Set IP address format constraint."""
        new_builder = cast(StringBuilder, self._clone())
        if version == 4:
            new_builder._pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        elif version == 6:
            new_builder._pattern = r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
        new_builder._format = f'ipv{version}' if version else 'ip'
        return new_builder
    
    def json(self) -> 'StringBuilder':
        """Set JSON string constraint."""
        new_builder = cast(StringBuilder, self._clone())
        new_builder._format = 'json-string'
        return new_builder
    
    def strip(self) -> 'StringBuilder':
        """Strip whitespace from string."""
        new_builder = cast(StringBuilder, self._clone())
        new_builder._strip_whitespace = True
        return new_builder
    
    def lower(self) -> 'StringBuilder':
        """Convert string to lowercase."""
        new_builder = cast(StringBuilder, self._clone())
        new_builder._to_lower = True
        return new_builder
    
    def upper(self) -> 'StringBuilder':
        """Convert string to uppercase."""
        new_builder = cast(StringBuilder, self._clone())
        new_builder._to_upper = True
        return new_builder
    
    def to_field_info(self) -> tuple[type, FieldInfo]:
        """Convert to tuple of (type, FieldInfo)."""
        kwargs = self._build_field_kwargs()
        
        if self._min_length is not None:
            kwargs['min_length'] = self._min_length
        if self._max_length is not None:
            kwargs['max_length'] = self._max_length
        if self._pattern is not None:
            kwargs['pattern'] = self._pattern
            
        return (str, Field(**kwargs))


class NumberBuilder(TypeBuilder):
    """Builder for numeric types (int/float) with constraints."""
    
    def __init__(self, is_integer: bool = False):
        super().__init__()
        self._is_integer = is_integer
        self._gt: Optional[float] = None
        self._ge: Optional[float] = None
        self._lt: Optional[float] = None
        self._le: Optional[float] = None
        self._multiple_of: Optional[float] = None
        self._allow_inf_nan: bool = True
    
    @property
    def _annotation_type(self) -> type:
        return int if self._is_integer else float
    
    def gt(self, value: float) -> 'NumberBuilder':
        """Set greater than constraint."""
        new_builder = cast(NumberBuilder, self._clone())
        new_builder._gt = value
        return new_builder
    
    def gte(self, value: float) -> 'NumberBuilder':
        """Set greater than or equal constraint."""
        new_builder = cast(NumberBuilder, self._clone())
        new_builder._ge = value
        return new_builder
    
    def lt(self, value: float) -> 'NumberBuilder':
        """Set less than constraint."""
        new_builder = cast(NumberBuilder, self._clone())
        new_builder._lt = value
        return new_builder
    
    def lte(self, value: float) -> 'NumberBuilder':
        """Set less than or equal constraint."""
        new_builder = cast(NumberBuilder, self._clone())
        new_builder._le = value
        return new_builder
    
    def positive(self) -> 'NumberBuilder':
        """Set positive constraint (> 0)."""
        new_builder = cast(NumberBuilder, self._clone())
        new_builder._gt = 0
        return new_builder
    
    def negative(self) -> 'NumberBuilder':
        """Set negative constraint (< 0)."""
        new_builder = cast(NumberBuilder, self._clone())
        new_builder._lt = 0
        return new_builder
    
    def non_positive(self) -> 'NumberBuilder':
        """Set non-positive constraint (<= 0)."""
        new_builder = cast(NumberBuilder, self._clone())
        new_builder._le = 0
        return new_builder
    
    def non_negative(self) -> 'NumberBuilder':
        """Set non-negative constraint (>= 0)."""
        new_builder = cast(NumberBuilder, self._clone())
        new_builder._ge = 0
        return new_builder
    
    def finite(self) -> 'NumberBuilder':
        """Set finite constraint (no inf/NaN)."""
        new_builder = cast(NumberBuilder, self._clone())
        new_builder._allow_inf_nan = False
        return new_builder
    
    def multiple_of(self, value: float) -> 'NumberBuilder':
        """Set multiple of constraint."""
        new_builder = cast(NumberBuilder, self._clone())
        new_builder._multiple_of = value
        return new_builder
    
    def range(self, min: float, max: float) -> 'NumberBuilder':
        """Set range constraint (inclusive)."""
        new_builder = cast(NumberBuilder, self._clone())
        new_builder._ge = min
        new_builder._le = max
        return new_builder
    
    def to_field_info(self) -> tuple[type, FieldInfo]:
        """Convert to tuple of (type, FieldInfo)."""
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
        
        annotation = int if self._is_integer else float
        return (annotation, Field(**kwargs))


class BooleanBuilder(TypeBuilder):
    """Builder for boolean types."""
    
    def __init__(self):
        super().__init__()
        self._strict: bool = False
    
    @property
    def _annotation_type(self) -> type:
        return bool
    
    def strict(self) -> 'BooleanBuilder':
        """Set strict boolean constraint."""
        new_builder = cast(BooleanBuilder, self._clone())
        new_builder._strict = True
        return new_builder
    
    def to_field_info(self) -> tuple[type, FieldInfo]:
        """Convert to tuple of (type, FieldInfo)."""
        kwargs = self._build_field_kwargs()
        return (bool, Field(**kwargs))


class DateTimeBuilder(TypeBuilder):
    """Builder for datetime types."""
    
    def __init__(self, type_: str = 'datetime'):
        super().__init__()
        self._type = type_  # 'datetime', 'date', 'time'
    
    @property
    def _annotation_type(self) -> type:
        if self._type == 'datetime':
            return datetime
        elif self._type == 'date':
            return date
        elif self._type == 'time':
            return time
        return datetime
    
    def to_field_info(self) -> tuple[type, FieldInfo]:
        """Convert to tuple of (type, FieldInfo)."""
        kwargs = self._build_field_kwargs()
        return (self._annotation_type, Field(**kwargs))


class UUIDBuilder(TypeBuilder):
    """Builder for UUID types."""
    
    def __init__(self, version: Optional[int] = None):
        super().__init__()
        self._version = version
    
    @property
    def _annotation_type(self) -> type:
        return UUID
    
    def to_field_info(self) -> tuple[type, FieldInfo]:
        """Convert to tuple of (type, FieldInfo)."""
        kwargs = self._build_field_kwargs()
        return (UUID, Field(**kwargs))


class BytesBuilder(TypeBuilder):
    """Builder for bytes types."""
    
    def __init__(self):
        super().__init__()
        self._min_length: Optional[int] = None
        self._max_length: Optional[int] = None
    
    @property
    def _annotation_type(self) -> type:
        return bytes
    
    def min(self, length: int) -> 'BytesBuilder':
        """Set minimum bytes length."""
        new_builder = cast(BytesBuilder, self._clone())
        new_builder._min_length = length
        return new_builder
    
    def max(self, length: int) -> 'BytesBuilder':
        """Set maximum bytes length."""
        new_builder = cast(BytesBuilder, self._clone())
        new_builder._max_length = length
        return new_builder
    
    def to_field_info(self) -> tuple[type, FieldInfo]:
        """Convert to tuple of (type, FieldInfo)."""
        kwargs = self._build_field_kwargs()
        
        if self._min_length is not None:
            kwargs['min_length'] = self._min_length
        if self._max_length is not None:
            kwargs['max_length'] = self._max_length
            
        return (bytes, Field(**kwargs))


class DecimalBuilder(TypeBuilder):
    """Builder for decimal types."""
    
    def __init__(self):
        super().__init__()
        self._max_digits: Optional[int] = None
        self._decimal_places: Optional[int] = None
        self._gt: Optional[Decimal] = None
        self._ge: Optional[Decimal] = None
        self._lt: Optional[Decimal] = None
        self._le: Optional[Decimal] = None
    
    @property
    def _annotation_type(self) -> type:
        return Decimal
    
    def max_digits(self, value: int) -> 'DecimalBuilder':
        """Set maximum digits."""
        new_builder = cast(DecimalBuilder, self._clone())
        new_builder._max_digits = value
        return new_builder
    
    def decimal_places(self, value: int) -> 'DecimalBuilder':
        """Set decimal places."""
        new_builder = cast(DecimalBuilder, self._clone())
        new_builder._decimal_places = value
        return new_builder
    
    def gt(self, value: Decimal) -> 'DecimalBuilder':
        """Set greater than constraint."""
        new_builder = cast(DecimalBuilder, self._clone())
        new_builder._gt = value
        return new_builder
    
    def gte(self, value: Decimal) -> 'DecimalBuilder':
        """Set greater than or equal constraint."""
        new_builder = cast(DecimalBuilder, self._clone())
        new_builder._ge = value
        return new_builder
    
    def lt(self, value: Decimal) -> 'DecimalBuilder':
        """Set less than constraint."""
        new_builder = cast(DecimalBuilder, self._clone())
        new_builder._lt = value
        return new_builder
    
    def lte(self, value: Decimal) -> 'DecimalBuilder':
        """Set less than or equal constraint."""
        new_builder = cast(DecimalBuilder, self._clone())
        new_builder._le = value
        return new_builder
    
    def to_field_info(self) -> tuple[type, FieldInfo]:
        """Convert to tuple of (type, FieldInfo)."""
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
            
        return (Decimal, Field(**kwargs))


class AnyBuilder(TypeBuilder):
    """Builder for any type."""
    
    @property
    def _annotation_type(self) -> type:
        return Any
    
    def to_field_info(self) -> tuple[type, FieldInfo]:
        """Convert to tuple of (type, FieldInfo)."""
        kwargs = self._build_field_kwargs()
        return (Any, Field(**kwargs))


class NoneBuilder(TypeBuilder):
    """Builder for None type."""
    
    @property
    def _annotation_type(self) -> type:
        return type(None)
    
    def to_field_info(self) -> tuple[type, FieldInfo]:
        """Convert to tuple of (type, FieldInfo)."""
        kwargs = self._build_field_kwargs()
        kwargs['default'] = None
        return (type(None), Field(**kwargs))
