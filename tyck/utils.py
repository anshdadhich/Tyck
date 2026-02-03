"""Utility functions for schema manipulation.

These utilities are inspired by TypeScript utility types like
Pick, Omit, Partial, and Record.
"""

from typing import Type, Dict, Any, Set, get_type_hints
from pydantic import BaseModel, create_model
from .interface import interface


def pick_fields(model: Type[BaseModel], *field_names: str) -> Type[BaseModel]:
    """
    Create a new model with only the specified fields.
    
    Similar to TypeScript's Pick<T, K>.
    
    Args:
        model: Source Pydantic model
        field_names: Field names to include
        
    Returns:
        New model with only picked fields
        
    Example:
        >>> User = interface({'id': int, 'name': str, 'email': str})
        >>> PublicUser = pick_fields(User, 'id', 'name')
    """
    # Get model fields
    model_fields = model.model_fields
    
    # Filter to only picked fields and convert to (type, FieldInfo) tuples
    picked = {}
    for name in field_names:
        if name in model_fields:
            field_info = model_fields[name]
            # Convert FieldInfo to (type, FieldInfo) tuple for Pydantic v2
            picked[name] = (field_info.annotation, field_info)
    
    # Create new model
    return create_model(
        f'{model.__name__}Pick',
        **picked,
        __base__=BaseModel,
    )


def omit_fields(model: Type[BaseModel], *field_names: str) -> Type[BaseModel]:
    """
    Create a new model excluding the specified fields.
    
    Similar to TypeScript's Omit<T, K>.
    
    Args:
        model: Source Pydantic model
        field_names: Field names to exclude
        
    Returns:
        New model without omitted fields
        
    Example:
        >>> User = interface({'id': int, 'name': str, 'password': str})
        >>> SafeUser = omit_fields(User, 'password')
    """
    # Get model fields
    model_fields = model.model_fields
    
    # Filter out omitted fields and convert to (type, FieldInfo) tuples
    omitted = {}
    for name, field_info in model_fields.items():
        if name not in field_names:
            # Convert FieldInfo to (type, FieldInfo) tuple for Pydantic v2
            omitted[name] = (field_info.annotation, field_info)
    
    # Create new model
    return create_model(
        f'{model.__name__}Omit',
        **omitted,
        __base__=BaseModel,
    )


def extend_fields(model: Type[BaseModel], fields: Dict[str, Any]) -> Type[BaseModel]:
    """
    Create a new model by adding/replacing fields.
    
    Args:
        model: Source Pydantic model
        fields: New fields to add
        
    Returns:
        New model with extended fields
        
    Example:
        >>> User = interface({'id': int, 'name': str})
        >>> Admin = extend_fields(User, {'role': str, 'permissions': list})
    """
    # Get existing fields
    existing = dict(model.model_fields)
    
    # Merge with new fields
    merged = {**existing, **fields}
    
    # Create new model using interface
    return interface(merged)


def make_optional(model: Type[BaseModel]) -> Type[BaseModel]:
    """
    Make all fields in a model optional.
    
    Similar to TypeScript's Partial<T>.
    
    Args:
        model: Source Pydantic model
        
    Returns:
        New model with all fields optional
        
    Example:
        >>> CreateUser = interface({'name': str, 'email': str, 'age': int})
        >>> UpdateUser = make_optional(CreateUser)  # All fields optional
    """
    from typing import Optional
    
    model_fields = model.model_fields
    
    # Make all fields optional with default=None
    optional_fields = {}
    for name, field_info in model_fields.items():
        annotation = field_info.annotation
        optional_fields[name] = (Optional[annotation], None)
    
    return create_model(
        f'{model.__name__}Partial',
        **optional_fields,
        __base__=BaseModel,
    )


def merge(*models: Type[BaseModel]) -> Type[BaseModel]:
    """
    Merge multiple models into one.
    
    Later models override fields from earlier ones.
    
    Args:
        models: Models to merge
        
    Returns:
        New merged model
        
    Example:
        >>> Timestamps = interface({'created_at': str, 'updated_at': str})
        >>> User = interface({'id': int, 'name': str})
        >>> UserWithTimestamps = merge(User, Timestamps)
    """
    merged_fields = {}
    
    for model in models:
        merged_fields.update(model.model_fields)
    
    return interface(merged_fields)
