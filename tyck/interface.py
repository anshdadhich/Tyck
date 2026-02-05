"""Interface function to create Pydantic models from dictionaries."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Type

from pydantic import BaseModel, ConfigDict, create_model, Field
from pydantic.fields import FieldInfo

from .types_ import TyckType


def interface(
    fields: Dict[str, Any],
    *,
    config: Optional[ConfigDict] = None,
    validators: Optional[Dict[str, Callable]] = None,
    name: Optional[str] = None,
    base: Optional[Type[BaseModel]] = None,
    doc: Optional[str] = None,
) -> Type[BaseModel]:
    """
    Create a Pydantic model from a dictionary of fields.
    
    This is the core function of Tyck that converts dictionary-based
    schema definitions into fully functional Pydantic models.
    
    Args:
        fields: Dictionary mapping field names to type validators or type annotations
        config: Optional Pydantic configuration dictionary
        validators: Optional dictionary of custom validator functions
        name: Optional custom class name
        base: Optional base class to inherit from
        doc: Optional docstring for the model
        
    Returns:
        A Pydantic BaseModel subclass
        
    Example:
        >>> from tyck import interface, string, integer
        >>> 
        >>> User = interface({
        ...     'id': integer.positive(),
        ...     'name': string.min(1).max(100),
        ... })
        >>> 
        >>> user = User(id=1, name="John")
        >>> print(user.model_dump())
        {'id': 1, 'name': 'John'}
    """
    pydantic_fields = {}
    
    for field_name, field_def in fields.items():
        if isinstance(field_def, TyckType):
            # Handle Tyck type validators
            result = field_def.build()
            if isinstance(result, tuple):
                pydantic_fields[field_name] = result
            else:
                pydantic_fields[field_name] = result
        elif isinstance(field_def, FieldInfo):
            # Handle direct Pydantic Field instances
            annotation = field_def.annotation if hasattr(field_def, 'annotation') else Any
            pydantic_fields[field_name] = (annotation, field_def)
        elif isinstance(field_def, tuple) and len(field_def) == 2:
            # Handle (type, FieldInfo) tuples directly
            pydantic_fields[field_name] = field_def
        elif isinstance(field_def, type) and issubclass(field_def, BaseModel):
            # Handle nested Pydantic models
            pydantic_fields[field_name] = (field_def, ...)
        else:
            # Handle raw types (int, str, etc.) or default values
            if isinstance(field_def, type):
                pydantic_fields[field_name] = (field_def, ...)
            else:
                # It's a default value
                pydantic_fields[field_name] = field_def
    
    # Generate class name if not provided
    if name is None:
        import hashlib
        field_names = '_'.join(sorted(fields.keys()))
        hash_suffix = hashlib.md5(field_names.encode()).hexdigest()[:8]
        name = f"Interface_{hash_suffix}"
    
    # Prepare model kwargs
    model_kwargs: Dict[str, Any] = {}
    
    if base:
        model_kwargs['__base__'] = base
    
    if config:
        # For Pydantic v2, we need to pass config differently
        pass  # Will be handled after model creation
    
    # Create the model using Pydantic's create_model
    model = create_model(
        name,
        **pydantic_fields,
    )
    
    # Apply config if provided
    if config:
        model.model_config.update(config)
    
    # Add docstring if provided
    if doc:
        model.__doc__ = doc
    
    return model


def config(
    *,
    strict: Optional[bool] = None,
    frozen: Optional[bool] = None,
    extra: Optional[str] = None,
    populate_by_name: Optional[bool] = None,
    validate_assignment: Optional[bool] = None,
    str_to_lower: Optional[bool] = None,
    str_to_upper: Optional[bool] = None,
    str_strip_whitespace: Optional[bool] = None,
    use_enum_values: Optional[bool] = None,
    validate_default: Optional[bool] = None,
    **kwargs: Any,
) -> ConfigDict:
    """
    Create a Pydantic configuration dictionary.
    
    Args:
        strict: Whether to use strict type checking
        frozen: Whether models are immutable
        extra: How to handle extra fields ('ignore', 'allow', 'forbid')
        populate_by_name: Whether to allow population by field name
        validate_assignment: Whether to validate on assignment
        str_to_lower: Convert strings to lowercase
        str_to_upper: Convert strings to uppercase
        str_strip_whitespace: Strip whitespace from strings
        use_enum_values: Use enum values instead of enum instances
        validate_default: Validate default values
        **kwargs: Additional configuration options
        
    Returns:
        Configuration dictionary (ConfigDict)
        
    Example:
        >>> from tyck import interface, string, config
        >>> User = interface({
        ...     'name': string
        ... }, config=config(strict=True, frozen=True))
    """
    cfg: Dict[str, Any] = {}
    
    if strict is not None:
        cfg['strict'] = strict
    if frozen is not None:
        cfg['frozen'] = frozen
    if extra is not None:
        cfg['extra'] = extra
    if populate_by_name is not None:
        cfg['populate_by_name'] = populate_by_name
    if validate_assignment is not None:
        cfg['validate_assignment'] = validate_assignment
    if str_to_lower is not None:
        cfg['str_to_lower'] = str_to_lower
    if str_to_upper is not None:
        cfg['str_to_upper'] = str_to_upper
    if str_strip_whitespace is not None:
        cfg['str_strip_whitespace'] = str_strip_whitespace
    if use_enum_values is not None:
        cfg['use_enum_values'] = use_enum_values
    if validate_default is not None:
        cfg['validate_default'] = validate_default
    
    cfg.update(kwargs)
    
    return cfg  # type: ignore
