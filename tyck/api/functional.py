"""Functional API for Tyck - interface() function."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel, create_model, ConfigDict, Field
from pydantic.fields import FieldInfo

from tyck.core.builders import TypeBuilder

T = TypeVar('T', bound=BaseModel)


def interface(
    fields: Dict[str, Any],
    config: Optional[ConfigDict] = None,
    validators: Optional[Dict[str, Callable]] = None,
    name: Optional[str] = None,
    base: Optional[Type[BaseModel]] = None,
    doc: Optional[str] = None,
) -> Type[BaseModel]:
    """Create a Pydantic model from a field definition dictionary.
    
    This is the functional API for creating Tyck models, similar to
    TypeScript's interface or Zod's object().
    
    Args:
        fields: Dictionary mapping field names to type builders or types
        config: Optional Pydantic configuration dictionary
        validators: Optional dictionary of custom validator functions
        name: Optional custom class name (auto-generated if not provided)
        base: Optional base class to inherit from
        doc: Optional docstring for the generated class
        
    Returns:
        A Pydantic BaseModel subclass
        
    Examples:
        Basic usage:
        >>> from Tyck import interface, string, number
        >>> User = interface({
        ...     'id': number.integer().positive(),
        ...     'name': string.min(1).max(100),
        ...     'email': string.email(),
        ... })
        >>> user = User(id=1, name="John", email="john@example.com")
        
        With optional fields:
        >>> from Tyck import optional
        >>> User = interface({
        ...     'id': number.integer(),
        ...     'bio': optional(string.max(500))
        ... })
        >>> user = User(id=1)  # bio is optional
        
        With configuration:
        >>> User = interface({
        ...     'name': string
        ... }, config={'strict': True, 'frozen': True})
    """
    # Convert builders to Pydantic field definitions
    pydantic_fields: Dict[str, Any] = {}
    
    for field_name, field_def in fields.items():
        if isinstance(field_def, TypeBuilder):
            # Convert TypeBuilder to (type, FieldInfo) tuple
            annotation, field_info = field_def.to_field_info()
            pydantic_fields[field_name] = (annotation, field_info)
        elif isinstance(field_def, type) and issubclass(field_def, BaseModel):
            # Nested model - use as type annotation
            pydantic_fields[field_name] = (field_def, ...)
        elif isinstance(field_def, FieldInfo):
            # Already a FieldInfo
            pydantic_fields[field_name] = field_def
        elif isinstance(field_def, tuple):
            # Tuple of (type, default) or (type, FieldInfo)
            pydantic_fields[field_name] = field_def
        else:
            # Default value
            pydantic_fields[field_name] = Field(default=field_def)
    
    # Generate class name if not provided
    if name is None:
        import hashlib
        # Create a deterministic name based on field names
        field_names = '_'.join(sorted(fields.keys()))
        hash_suffix = hashlib.md5(field_names.encode()).hexdigest()[:8]
        name = f"Interface_{hash_suffix}"
    
    # Prepare model kwargs
    model_kwargs: Dict[str, Any] = {}
    
    if base:
        model_kwargs['__base__'] = base
    
    if config:
        model_kwargs['__config__'] = config
    
    if validators:
        model_kwargs['__validators__'] = validators
    
    # Create the model
    model = create_model(name, **model_kwargs, **pydantic_fields)
    
    # Add docstring if provided
    if doc:
        model.__doc__ = doc
    
    return model


def config(
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
    ser_json_timedelta: Optional[str] = None,
    ser_json_bytes: Optional[str] = None,
    **kwargs: Any
) -> ConfigDict:
    """Create a Pydantic configuration dictionary.
    
    This is a helper function to create configuration dictionaries with
    a more convenient API.
    
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
        ser_json_timedelta: JSON serialization format for timedelta
        ser_json_bytes: JSON serialization format for bytes
        **kwargs: Additional configuration options
        
    Returns:
        Configuration dictionary
        
    Example:
        >>> from Tyck import interface, string, config
        >>> User = interface({
        ...     'name': string
        ... }, config=config(strict=True, frozen=True))
    """
    cfg: ConfigDict = {}
    
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
    if ser_json_timedelta is not None:
        cfg['ser_json_timedelta'] = ser_json_timedelta
    if ser_json_bytes is not None:
        cfg['ser_json_bytes'] = ser_json_bytes
    
    cfg.update(kwargs)
    
    return cfg


def validator(
    field_name: str,
    check: Callable[[Any], bool],
    error_message: Optional[str] = None
) -> Callable:
    """Create a field validator.
    
    Args:
        field_name: Name of the field to validate
        check: Function that returns True if valid
        error_message: Custom error message if validation fails (optional)
        
    Returns:
        Validator function
        
    Example:
        >>> from Tyck import interface, string, number, validator
        >>> User = interface({
        ...     'age': number
        ... }, validators={'check_age': validator('age', lambda x: x >= 0, "Age must be non-negative")})
    """
    def validate(cls, v):
        if not check(v):
            if error_message:
                raise ValueError(error_message)
            else:
                # Generate a user-friendly error message
                value_str = repr(v)
                if len(value_str) > 50:
                    value_str = value_str[:47] + "..."
                raise ValueError(
                    f"Validation failed for field '{field_name}'.\n"
                    f"  Received value: {value_str}\n"
                    f"  Tip: The value does not meet the custom validation requirements.\n"
                    f"  You can provide a custom error message using the error_message parameter."
                )
        return v
    
    validate.__name__ = f"validate_{field_name}"
    return validate


def multi_field_validator(
    *field_names: str,
    check: Callable[..., bool],
    error_message: Optional[str] = None
) -> Callable:
    """Create a validator that checks multiple fields.
    
    Args:
        *field_names: Names of fields to validate
        check: Function that receives field values and returns True if valid
        error_message: Custom error message if validation fails (optional)
        
    Returns:
        Validator function
        
    Example:
        >>> from Tyck import interface, string, multi_field_validator
        >>> User = interface({
        ...     'password': string,
        ...     'confirm_password': string
        ... }, validators={'passwords_match': multi_field_validator('password', 'confirm_password', check=lambda p, c: p == c, error_message="Passwords must match")})
    """
    def validate(cls, **kwargs):
        values = [kwargs.get(name) for name in field_names]
        if not check(*values):
            if error_message:
                raise ValueError(error_message)
            else:
                # Generate a user-friendly error message
                fields_str = ", ".join([f"'{name}'" for name in field_names])
                values_str = ", ".join([repr(v) for v in values])
                raise ValueError(
                    f"Validation failed for fields {fields_str}.\n"
                    f"  Received values: {values_str}\n"
                    f"  Tip: These fields do not meet the validation requirements together.\n"
                    f"  You can provide a custom error message using the error_message parameter."
                )
        return kwargs
    
    validate.__name__ = f"validate_{'_'.join(field_names)}"
    return validate
