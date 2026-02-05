"""Utility functions for schema manipulation.

These utilities are inspired by TypeScript utility types like
Pick, Omit, Partial, Required, and Record.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, ConfigDict, create_model, Field
from pydantic.fields import FieldInfo

from .interface import interface
from .types_ import TyckType


def _field_info_to_tuple(field_info: FieldInfo) -> tuple:
    """Convert a FieldInfo to a (type, FieldInfo) tuple."""
    annotation = field_info.annotation
    if annotation is None:
        annotation = Any
    return (annotation, field_info)


def pick(
    model_class: Type[BaseModel],
    *field_names: str,
    name: Optional[str] = None,
    config: Optional[ConfigDict] = None,
) -> Type[BaseModel]:
    """
    Create a new model with only the specified fields.
    
    Similar to TypeScript's Pick<T, K>.
    
    Args:
        model_class: Source model class
        *field_names: Names of fields to pick
        name: Optional custom class name
        config: Optional configuration for the new model
        
    Returns:
        New model class with only the picked fields
        
    Example:
        >>> from tyck import interface, string, integer, pick
        >>> User = interface({
        ...     'id': integer,
        ...     'name': string,
        ...     'email': string,
        ...     'password': string,
        ... })
        >>> PublicUser = pick(User, 'id', 'name', 'email')
    """
    source_fields = model_class.model_fields
    
    new_fields: Dict[str, Any] = {}
    for field_name in field_names:
        if field_name in source_fields:
            field_info = source_fields[field_name]
            new_fields[field_name] = _field_info_to_tuple(field_info)
        else:
            raise ValueError(f"Field '{field_name}' not found in model '{model_class.__name__}'")
    
    if name is None:
        name = f"Pick_{model_class.__name__}"
    
    return interface(new_fields, name=name, config=config)


def omit(
    model_class: Type[BaseModel],
    *field_names: str,
    name: Optional[str] = None,
    config: Optional[ConfigDict] = None,
) -> Type[BaseModel]:
    """
    Create a new model without the specified fields.
    
    Similar to TypeScript's Omit<T, K>.
    
    Args:
        model_class: Source model class
        *field_names: Names of fields to omit
        name: Optional custom class name
        config: Optional configuration for the new model
        
    Returns:
        New model class without the omitted fields
        
    Example:
        >>> from tyck import interface, string, integer, omit
        >>> User = interface({
        ...     'id': integer,
        ...     'name': string,
        ...     'password': string,
        ... })
        >>> SafeUser = omit(User, 'password')
    """
    source_fields = model_class.model_fields
    omitted_set = set(field_names)
    
    new_fields: Dict[str, Any] = {}
    for field_name, field_info in source_fields.items():
        if field_name not in omitted_set:
            new_fields[field_name] = _field_info_to_tuple(field_info)
    
    if name is None:
        name = f"Omit_{model_class.__name__}"
    
    return interface(new_fields, name=name, config=config)


def partial(
    model_class: Type[BaseModel],
    name: Optional[str] = None,
    config: Optional[ConfigDict] = None,
) -> Type[BaseModel]:
    """
    Make all fields optional (useful for PATCH requests).
    
    Similar to TypeScript's Partial<T>.
    
    Args:
        model_class: Source model class
        name: Optional custom class name
        config: Optional configuration for the new model
        
    Returns:
        New model class with all fields optional
        
    Example:
        >>> from tyck import interface, string, integer, partial
        >>> User = interface({
        ...     'id': integer,
        ...     'name': string,
        ...     'email': string,
        ... })
        >>> UserUpdate = partial(User)
        >>> update = UserUpdate(name="New Name")  # Only update name
    """
    from typing import Optional as TypingOptional
    
    source_fields = model_class.model_fields
    
    new_fields: Dict[str, Any] = {}
    for field_name, field_info in source_fields.items():
        annotation = field_info.annotation
        if annotation is None:
            annotation = Any
        
        new_field_info = Field(
            default=None,
            alias=field_info.alias,
            title=field_info.title,
            description=field_info.description,
        )
        new_fields[field_name] = (TypingOptional[annotation], new_field_info)
    
    if name is None:
        name = f"Partial_{model_class.__name__}"
    
    return interface(new_fields, name=name, config=config)


def required(
    model_class: Type[BaseModel],
    name: Optional[str] = None,
    config: Optional[ConfigDict] = None,
) -> Type[BaseModel]:
    """
    Make all fields required (remove defaults).
    
    Opposite of partial().
    
    Args:
        model_class: Source model class
        name: Optional custom class name
        config: Optional configuration for the new model
        
    Returns:
        New model class with all fields required
        
    Example:
        >>> from tyck import interface, string, integer, required
        >>> User = interface({
        ...     'id': integer,
        ...     'name': string,
        ...     'bio': string.default("")
        ... })
        >>> StrictUser = required(User)
    """
    source_fields = model_class.model_fields
    
    new_fields: Dict[str, Any] = {}
    for field_name, field_info in source_fields.items():
        annotation = field_info.annotation
        if annotation is None:
            annotation = Any
        
        new_field_info = Field(
            alias=field_info.alias,
            title=field_info.title,
            description=field_info.description,
        )
        new_fields[field_name] = (annotation, new_field_info)
    
    if name is None:
        name = f"Required_{model_class.__name__}"
    
    return interface(new_fields, name=name, config=config)


def extend(
    base_model: Type[BaseModel],
    new_fields: Dict[str, Any],
    name: Optional[str] = None,
    config: Optional[ConfigDict] = None,
) -> Type[BaseModel]:
    """
    Extend a model with new fields.
    
    Similar to TypeScript's interface extension.
    
    Args:
        base_model: Base model class to extend
        new_fields: Dictionary of new fields to add
        name: Optional custom class name
        config: Optional configuration for the new model
        
    Returns:
        New model class with extended fields
        
    Example:
        >>> from tyck import interface, string, integer, array, extend
        >>> User = interface({
        ...     'id': integer,
        ...     'name': string
        ... })
        >>> Admin = extend(User, {
        ...     'role': string.default('admin'),
        ...     'permissions': array(string)
        ... })
    """
    base_fields = dict(base_model.model_fields)
    
    merged_fields: Dict[str, Any] = {}
    for field_name, field_info in base_fields.items():
        merged_fields[field_name] = _field_info_to_tuple(field_info)
    
    for field_name, field_def in new_fields.items():
        if isinstance(field_def, TyckType):
            merged_fields[field_name] = field_def.build()
        elif isinstance(field_def, type) and issubclass(field_def, BaseModel):
            merged_fields[field_name] = (field_def, ...)
        else:
            merged_fields[field_name] = field_def
    
    if name is None:
        name = f"Extended_{base_model.__name__}"
    
    return interface(merged_fields, name=name, config=config)


def merge(
    *model_classes: Type[BaseModel],
    name: Optional[str] = None,
    config: Optional[ConfigDict] = None,
) -> Type[BaseModel]:
    """
    Merge multiple models into one.
    
    Later models override fields from earlier ones.
    
    Args:
        *model_classes: Model classes to merge
        name: Optional custom class name
        config: Optional configuration for the new model
        
    Returns:
        New merged model class
        
    Example:
        >>> from tyck import interface, string, integer, merge
        >>> User = interface({'id': integer, 'name': string})
        >>> Profile = interface({'bio': string, 'avatar': string})
        >>> UserWithProfile = merge(User, Profile)
    """
    merged_fields: Dict[str, Any] = {}
    
    for model_class in model_classes:
        fields = model_class.model_fields
        for field_name, field_info in fields.items():
            merged_fields[field_name] = _field_info_to_tuple(field_info)
    
    if name is None:
        names = '_'.join([cls.__name__ for cls in model_classes])
        name = f"Merge_{names}"
    
    return interface(merged_fields, name=name, config=config)


# Legacy aliases for backward compatibility
pick_fields = pick
omit_fields = omit
make_optional = partial
extend_fields = extend
merge_fields = merge
