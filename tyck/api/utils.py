"""Utility functions for Tyck - pick_fields, omit_fields, make_optional, extend_fields, merge_schemas, etc."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Type, TypeVar, get_type_hints

from pydantic import BaseModel, ConfigDict, Field, create_model
from pydantic.fields import FieldInfo

from tyck.api.functional import interface
from tyck.core.builders import TypeBuilder
from tyck.core.complex_types import Optional as OptionalBuilder

T = TypeVar('T', bound=BaseModel)


def _field_info_to_tuple(field_info: FieldInfo) -> tuple[type, FieldInfo]:
    """Convert a FieldInfo to a (type, FieldInfo) tuple."""
    annotation = field_info.annotation
    if annotation is None:
        annotation = Any
    return (annotation, field_info)


def pick_fields(
    model_class: Type[T],
    *field_names: str,
    name: Optional[str] = None,
    config: Optional[ConfigDict] = None
) -> Type[BaseModel]:
    """Create a new model with only the specified fields.
    
    Similar to TypeScript's Pick<T, K>.
    
    Args:
        model_class: Source model class
        *field_names: Names of fields to pick
        name: Optional custom class name
        config: Optional configuration for the new model
        
    Returns:
        New model class with only the picked fields
        
    Example:
        >>> from Tyck import interface, string, number, pick_fields
        >>> User = interface({
        ...     'id': number.integer(),
        ...     'name': string,
        ...     'email': string.email(),
        ...     'password': string
        ... })
        >>> PublicUser = pick_fields(User, 'id', 'name', 'email')
        >>> user = PublicUser(id=1, name="John", email="john@example.com")
    """
    # Get the fields from the source model
    source_fields = model_class.__pydantic_fields__
    
    # Create new field dictionary with only picked fields
    new_fields: Dict[str, Any] = {}
    for field_name in field_names:
        if field_name in source_fields:
            field_info = source_fields[field_name]
            new_fields[field_name] = _field_info_to_tuple(field_info)
        else:
            raise ValueError(f"Field '{field_name}' not found in model '{model_class.__name__}'")
    
    # Generate name if not provided
    if name is None:
        picked = '_'.join(field_names)
        name = f"Pick{model_class.__name__}_{picked}"
    
    # Create the new model (don't inherit from base to avoid including all parent fields)
    return interface(
        new_fields,
        name=name,
        config=config
    )


def omit_fields(
    model_class: Type[T],
    *field_names: str,
    name: Optional[str] = None,
    config: Optional[ConfigDict] = None
) -> Type[BaseModel]:
    """Create a new model without the specified fields.
    
    Similar to TypeScript's Omit<T, K>.
    
    Args:
        model_class: Source model class
        *field_names: Names of fields to omit
        name: Optional custom class name
        config: Optional configuration for the new model
        
    Returns:
        New model class without the omitted fields
        
    Example:
        >>> from Tyck import interface, string, number, omit_fields
        >>> User = interface({
        ...     'id': number.integer(),
        ...     'name': string,
        ...     'password': string
        ... })
        >>> PublicUser = omit_fields(User, 'password')
        >>> user = PublicUser(id=1, name="John")
    """
    # Get the fields from the source model
    source_fields = model_class.__pydantic_fields__
    
    # Create new field dictionary without omitted fields
    new_fields: Dict[str, Any] = {}
    omitted_set = set(field_names)
    
    for field_name, field_info in source_fields.items():
        if field_name not in omitted_set:
            new_fields[field_name] = _field_info_to_tuple(field_info)
    
    # Generate name if not provided
    if name is None:
        omitted = '_'.join(field_names)
        name = f"Omit{model_class.__name__}_{omitted}"
    
    # Create the new model (don't inherit from base to avoid including all parent fields)
    return interface(
        new_fields,
        name=name,
        config=config
    )


def make_optional(
    model_class: Type[T],
    name: Optional[str] = None,
    config: Optional[ConfigDict] = None
) -> Type[BaseModel]:
    """Make all fields optional.
    
    Similar to TypeScript's Partial<T>.
    
    Args:
        model_class: Source model class
        name: Optional custom class name
        config: Optional configuration for the new model
        
    Returns:
        New model class with all fields optional
        
    Example:
        >>> from Tyck import interface, string, number, make_optional
        >>> User = interface({
        ...     'id': number.integer(),
        ...     'name': string,
        ...     'email': string.email()
        ... })
        >>> UserUpdate = make_optional(User)
        >>> update = UserUpdate(name="New Name")  # Only update name
    """
    # Get the fields from the source model
    source_fields = model_class.__pydantic_fields__
    
    # Create new field dictionary with all fields optional
    new_fields: Dict[str, Any] = {}
    
    for field_name, field_info in source_fields.items():
        # Make the field optional by setting default to None
        annotation = field_info.annotation
        if annotation is None:
            annotation = Any
        
        # Create a new FieldInfo with default=None
        new_field_info = Field(
            default=None,
            alias=field_info.alias,
            title=field_info.title,
            description=field_info.description,
            examples=field_info.examples if hasattr(field_info, 'examples') else None,
            deprecated=field_info.deprecated if hasattr(field_info, 'deprecated') else False,
        )
        new_fields[field_name] = (Optional[annotation], new_field_info)
    
    # Generate name if not provided
    if name is None:
        name = f"Partial{model_class.__name__}"
    
    # Create the new model (don't inherit from base to avoid including all parent fields)
    return interface(
        new_fields,
        name=name,
        config=config
    )


def make_required(
    model_class: Type[T],
    name: Optional[str] = None,
    config: Optional[ConfigDict] = None
) -> Type[BaseModel]:
    """Make all fields required (remove defaults).
    
    Opposite of make_optional().
    
    Args:
        model_class: Source model class
        name: Optional custom class name
        config: Optional configuration for the new model
        
    Returns:
        New model class with all fields required
        
    Example:
        >>> from Tyck import interface, string, number, make_required
        >>> User = interface({
        ...     'id': number.integer(),
        ...     'name': string,
        ...     'bio': string.default("")
        ... })
        >>> StrictUser = make_required(User)
        >>> user = StrictUser(id=1, name="John", bio="")  # bio is now required
    """
    # Get the fields from the source model
    source_fields = model_class.__pydantic_fields__
    
    # Create new field dictionary with all fields required
    new_fields: Dict[str, Any] = {}
    
    for field_name, field_info in source_fields.items():
        annotation = field_info.annotation
        if annotation is None:
            annotation = Any
        
        # Create a new FieldInfo without default
        new_field_info = Field(
            alias=field_info.alias,
            title=field_info.title,
            description=field_info.description,
            examples=field_info.examples if hasattr(field_info, 'examples') else None,
            deprecated=field_info.deprecated if hasattr(field_info, 'deprecated') else False,
        )
        new_fields[field_name] = (annotation, new_field_info)
    
    # Generate name if not provided
    if name is None:
        name = f"Required{model_class.__name__}"
    
    # Create the new model (don't inherit from base to avoid including all parent fields)
    return interface(
        new_fields,
        name=name,
        config=config
    )


def extend_fields(
    base_model: Type[T],
    new_fields: Dict[str, Any],
    name: Optional[str] = None,
    config: Optional[ConfigDict] = None
) -> Type[BaseModel]:
    """Extend a model with new fields.
    
    Similar to TypeScript's interface extension.
    
    Args:
        base_model: Base model class to extend
        new_fields: Dictionary of new fields to add
        name: Optional custom class name
        config: Optional configuration for the new model
        
    Returns:
        New model class with extended fields
        
    Example:
        >>> from Tyck import interface, string, number, extend_fields
        >>> User = interface({
        ...     'id': number.integer(),
        ...     'name': string
        ... })
        >>> Admin = extend_fields(User, {
        ...     'role': string.default('admin'),
        ...     'permissions': list
        ... })
        >>> admin = Admin(id=1, name="John", role="admin", permissions=['read', 'write'])
    """
    # Get the fields from the base model
    base_fields = dict(base_model.__pydantic_fields__)
    
    # Convert existing fields to tuples
    merged_fields: Dict[str, Any] = {}
    for field_name, field_info in base_fields.items():
        merged_fields[field_name] = _field_info_to_tuple(field_info)
    
    # Convert new fields if they are TypeBuilders
    for field_name, field_def in new_fields.items():
        if isinstance(field_def, TypeBuilder):
            merged_fields[field_name] = field_def.to_field_info()
        elif isinstance(field_def, type) and issubclass(field_def, BaseModel):
            merged_fields[field_name] = (field_def, ...)
        else:
            merged_fields[field_name] = field_def
    
    # Generate name if not provided
    if name is None:
        name = f"Extended{base_model.__name__}"
    
    # Create the new model
    return interface(
        merged_fields,
        name=name,
        config=config,
        base=base_model
    )


def merge_schemas(
    *model_classes: Type[BaseModel],
    name: Optional[str] = None,
    config: Optional[ConfigDict] = None
) -> Type[BaseModel]:
    """Merge multiple models into one.
    
    Args:
        *model_classes: Model classes to merge
        name: Optional custom class name
        config: Optional configuration for the new model
        
    Returns:
        New model class with merged fields
        
    Example:
        >>> from Tyck import interface, string, number, merge_schemas
        >>> User = interface({'id': number.integer(), 'name': string})
        >>> Profile = interface({'bio': string, 'avatar': string})
        >>> UserWithProfile = merge_schemas(User, Profile)
    """
    # Collect all fields from all models
    merged_fields: Dict[str, Any] = {}
    
    for model_class in model_classes:
        fields = model_class.__pydantic_fields__
        for field_name, field_info in fields.items():
            if field_name in merged_fields:
                # Field already exists, skip or override (last one wins)
                pass
            merged_fields[field_name] = _field_info_to_tuple(field_info)
    
    # Generate name if not provided
    if name is None:
        names = '_'.join([cls.__name__ for cls in model_classes])
        name = f"Merge_{names}"
    
    # Create the new model
    return interface(
        merged_fields,
        name=name,
        config=config,
        base=model_classes[0] if model_classes else None
    )


# Alias for extend_fields
add_fields = extend_fields
