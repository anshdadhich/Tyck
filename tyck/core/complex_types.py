"""Complex type builders and helper functions for Tyck."""

from __future__ import annotations

from typing import Any, Dict as _Dict, List, Literal as _Literal, Optional as _Optional, Set as _Set, Type, Union as _Union, get_args, get_origin
from enum import Enum as _Enum

from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from tyck.core.builders import TypeBuilder


class ArrayBuilder(TypeBuilder):
    """Builder for array/list types."""
    
    def __init__(self, item_builder: TypeBuilder):
        super().__init__()
        self._item_builder = item_builder
        self._min_length: _Optional[int] = None
        self._max_length: _Optional[int] = None
        self._unique: bool = False
    
    @property
    def _annotation_type(self) -> type:
        return list
    
    def min(self, length: int) -> 'ArrayBuilder':
        """Set minimum array length."""
        clone = self._clone()
        clone._min_length = length
        return clone
    
    def max(self, length: int) -> 'ArrayBuilder':
        """Set maximum array length."""
        clone = self._clone()
        clone._max_length = length
        return clone
    
    def length(self, exact: int) -> 'ArrayBuilder':
        """Set exact array length."""
        clone = self._clone()
        clone._min_length = exact
        clone._max_length = exact
        return clone
    
    def unique(self) -> 'ArrayBuilder':
        """Require unique items."""
        clone = self._clone()
        clone._unique = True
        return clone
    
    def to_field_info(self) -> tuple[type, FieldInfo]:
        """Convert to tuple of (type, FieldInfo)."""
        kwargs = self._build_field_kwargs()
        
        if self._default is PydanticUndefined:
            kwargs['default_factory'] = list
        
        if self._min_length is not None:
            kwargs['min_length'] = self._min_length
        if self._max_length is not None:
            kwargs['max_length'] = self._max_length
        if self._unique:
            kwargs['unique_items'] = True
            
        return (list, Field(**kwargs))


class DictBuilder(TypeBuilder):
    """Builder for dictionary types."""
    
    def __init__(self, key_builder: TypeBuilder, value_builder: TypeBuilder):
        super().__init__()
        self._key_builder = key_builder
        self._value_builder = value_builder
        self._min_length: _Optional[int] = None
        self._max_length: _Optional[int] = None
    
    @property
    def _annotation_type(self) -> type:
        return dict
    
    def min(self, length: int) -> 'DictBuilder':
        """Set minimum dictionary size."""
        clone = self._clone()
        clone._min_length = length
        return clone
    
    def max(self, length: int) -> 'DictBuilder':
        """Set maximum dictionary size."""
        clone = self._clone()
        clone._max_length = length
        return clone
    
    def to_field_info(self) -> tuple[type, FieldInfo]:
        """Convert to tuple of (type, FieldInfo)."""
        kwargs = self._build_field_kwargs()
        
        if self._default is PydanticUndefined:
            kwargs['default_factory'] = dict
        
        if self._min_length is not None:
            kwargs['min_length'] = self._min_length
        if self._max_length is not None:
            kwargs['max_length'] = self._max_length
            
        return (dict, Field(**kwargs))


class SetBuilder(TypeBuilder):
    """Builder for set types."""
    
    def __init__(self, item_builder: TypeBuilder):
        super().__init__()
        self._item_builder = item_builder
        self._min_length: _Optional[int] = None
        self._max_length: _Optional[int] = None
    
    @property
    def _annotation_type(self) -> type:
        return set
    
    def min(self, length: int) -> 'SetBuilder':
        """Set minimum set size."""
        clone = self._clone()
        clone._min_length = length
        return clone
    
    def max(self, length: int) -> 'SetBuilder':
        """Set maximum set size."""
        clone = self._clone()
        clone._max_length = length
        return clone
    
    def to_field_info(self) -> tuple[type, FieldInfo]:
        """Convert to tuple of (type, FieldInfo)."""
        kwargs = self._build_field_kwargs()
        
        if self._default is PydanticUndefined:
            kwargs['default_factory'] = set
        
        if self._min_length is not None:
            kwargs['min_length'] = self._min_length
        if self._max_length is not None:
            kwargs['max_length'] = self._max_length
            
        return (set, Field(**kwargs))


class TupleBuilder(TypeBuilder):
    """Builder for tuple types."""
    
    def __init__(self, *item_builders: TypeBuilder):
        super().__init__()
        self._item_builders = item_builders
    
    @property
    def _annotation_type(self) -> type:
        return tuple
    
    def to_field_info(self) -> tuple[type, FieldInfo]:
        """Convert to tuple of (type, FieldInfo)."""
        kwargs = self._build_field_kwargs()
        return (tuple, Field(**kwargs))


class UnionBuilder(TypeBuilder):
    """Builder for union types."""
    
    def __init__(self, *builders: TypeBuilder):
        super().__init__()
        self._builders = builders
    
    @property
    def _annotation_type(self) -> type:
        return _Union  # type: ignore
    
    def to_field_info(self) -> tuple[type, FieldInfo]:
        """Convert to tuple of (type, FieldInfo)."""
        kwargs = self._build_field_kwargs()
        return (_Union, Field(**kwargs))  # type: ignore


class LiteralBuilder(TypeBuilder):
    """Builder for literal types."""
    
    def __init__(self, *values: Any):
        super().__init__()
        self._values = values
    
    @property
    def _annotation_type(self) -> type:
        # Create a Literal type with the values
        if len(self._values) == 1:
            return _Literal[self._values[0]]
        else:
            return _Literal[self._values]  # type: ignore
    
    def to_field_info(self) -> tuple[type, FieldInfo]:
        """Convert to tuple of (type, FieldInfo)."""
        kwargs = self._build_field_kwargs()
        # Create the Literal type annotation
        if len(self._values) == 1:
            literal_type = _Literal[self._values[0]]
        else:
            # For multiple values, we need to build Union[Literal[v1], Literal[v2], ...]
            literal_type = _Union[tuple(_Literal[v] for v in self._values)]  # type: ignore
        return (literal_type, Field(**kwargs))


class EnumBuilder(TypeBuilder):
    """Builder for enum types."""
    
    def __init__(self, enum_class: Type[_Enum]):
        super().__init__()
        self._enum_class = enum_class
    
    @property
    def _annotation_type(self) -> type:
        return self._enum_class
    
    def to_field_info(self) -> tuple[type, FieldInfo]:
        """Convert to tuple of (type, FieldInfo)."""
        kwargs = self._build_field_kwargs()
        return (self._enum_class, Field(**kwargs))


# Helper functions

def Array(item_builder: TypeBuilder) -> ArrayBuilder:
    """Create an array/list type builder.
    
    Args:
        item_builder: Type builder for array items
        
    Returns:
        ArrayBuilder instance
        
    Example:
        >>> from Tyck import Array, string
        >>> tags = Array(string).min(1).max(10)
    """
    return ArrayBuilder(item_builder)


def Dict(key_builder: TypeBuilder, value_builder: TypeBuilder) -> DictBuilder:
    """Create a dictionary type builder.
    
    Args:
        key_builder: Type builder for dictionary keys
        value_builder: Type builder for dictionary values
        
    Returns:
        DictBuilder instance
        
    Example:
        >>> from Tyck import Dict, string, any_type
        >>> metadata = Dict(string, any_type)
    """
    return DictBuilder(key_builder, value_builder)


def Set(item_builder: TypeBuilder) -> SetBuilder:
    """Create a set type builder.
    
    Args:
        item_builder: Type builder for set items
        
    Returns:
        SetBuilder instance
        
    Example:
        >>> from Tyck import Set, string
        >>> tags = Set(string)
    """
    return SetBuilder(item_builder)


def Tuple(*item_builders: TypeBuilder) -> TupleBuilder:
    """Create a tuple type builder.
    
    Args:
        *item_builders: Type builders for tuple items
        
    Returns:
        TupleBuilder instance
        
    Example:
        >>> from Tyck import Tuple, string, number
        >>> point = Tuple(number, number)
    """
    return TupleBuilder(*item_builders)


def Union(*builders: TypeBuilder) -> UnionBuilder:
    """Create a union type builder.
    
    Args:
        *builders: Type builders to union
        
    Returns:
        UnionBuilder instance
        
    Example:
        >>> from Tyck import Union, string, number
        >>> id_or_name = Union(string, number)
    """
    return UnionBuilder(*builders)


def Literal(*values: Any) -> LiteralBuilder:
    """Create a literal type builder.
    
    Args:
        *values: Literal values
        
    Returns:
        LiteralBuilder instance
        
    Example:
        >>> from Tyck import Literal
        >>> role = Literal('admin', 'user', 'guest')
    """
    return LiteralBuilder(*values)


def Enum(enum_class: Type[_Enum]) -> EnumBuilder:
    """Create an enum type builder.
    
    Args:
        enum_class: Enum class to use
        
    Returns:
        EnumBuilder instance
        
    Example:
        >>> from enum import Enum as _Enum
        >>> from Tyck import Enum
        >>> class Color(_Enum):
        ...     RED = 'red'
        ...     GREEN = 'green'
        >>> color = Enum(Color)
    """
    return EnumBuilder(enum_class)


def Optional(builder: TypeBuilder) -> TypeBuilder:
    """Make a field optional (Union[T, None]).
    
    Args:
        builder: Type builder to make optional
        
    Returns:
        Modified builder with None as default
        
    Example:
        >>> from Tyck import string, Optional
        >>> bio = Optional(string.max(500))
    """
    builder._default = None
    return builder
