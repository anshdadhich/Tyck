"""Model decorator for class-based schema definitions."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Type, get_type_hints

from pydantic import BaseModel, ConfigDict

from .types_ import TyckType


def model(
    *,
    config: Optional[ConfigDict] = None,
    frozen: bool = False,
    strict: bool = False,
    extra: Optional[str] = None,
    validate_assignment: bool = False,
    populate_by_name: bool = False,
    use_enum_values: bool = False,
) -> Callable[[Type], Type[BaseModel]]:
    """
    Decorator to convert a class into a Pydantic model with Tyck support.
    
    This allows using Tyck's fluent API within class definitions while
    maintaining full Pydantic functionality.
    
    Args:
        config: Optional Pydantic ConfigDict to apply
        frozen: Whether the model is immutable
        strict: Whether to use strict validation
        extra: How to handle extra fields ('ignore', 'allow', 'forbid')
        validate_assignment: Whether to validate on assignment
        populate_by_name: Whether to allow population by field name
        use_enum_values: Whether to use enum values instead of instances
        
    Returns:
        A decorator that converts the class to a Pydantic model
        
    Example:
        >>> from tyck import model, string, integer
        >>> 
        >>> @model()
        ... class User:
        ...     id: integer.positive()
        ...     name: string.min(1).max(100)
        ...     email: string.email()
        ...     
        ...     def greet(self) -> str:
        ...         return f"Hello, {self.name}!"
        >>> 
        >>> user = User(id=1, name="John", email="john@example.com")
        >>> user.greet()
        'Hello, John!'
    """
    def decorator(cls: Type) -> Type[BaseModel]:
        # Build model config
        model_config: Dict[str, Any] = {}
        
        if config:
            model_config.update(config)
        if frozen:
            model_config['frozen'] = True
        if strict:
            model_config['strict'] = True
        if extra:
            model_config['extra'] = extra
        if validate_assignment:
            model_config['validate_assignment'] = True
        if populate_by_name:
            model_config['populate_by_name'] = True
        if use_enum_values:
            model_config['use_enum_values'] = True
        
        # Get annotations from the class
        annotations = {}
        if hasattr(cls, '__annotations__'):
            annotations = cls.__annotations__.copy()
        
        # Process annotations - convert TyckType to proper annotations
        field_definitions = {}
        processed_annotations = {}
        
        for attr_name, hint in annotations.items():
            if isinstance(hint, TyckType):
                # Convert TyckType to (type, Field) tuple
                type_annotation, field_info = hint.build()
                processed_annotations[attr_name] = type_annotation
                field_definitions[attr_name] = field_info
            else:
                processed_annotations[attr_name] = hint
                # Check if there's a class attribute with default value
                if hasattr(cls, attr_name):
                    field_definitions[attr_name] = getattr(cls, attr_name)
        
        # Collect methods and other class attributes
        class_attrs: Dict[str, Any] = {
            '__annotations__': processed_annotations,
            '__module__': cls.__module__,
            '__qualname__': cls.__qualname__,
        }
        
        if cls.__doc__:
            class_attrs['__doc__'] = cls.__doc__
        
        if model_config:
            class_attrs['model_config'] = ConfigDict(**model_config)
        
        # Copy methods and non-annotation attributes
        for key, value in cls.__dict__.items():
            if key.startswith('_'):
                continue
            if key in processed_annotations:
                # This is a field with a default value
                if key not in field_definitions:
                    field_definitions[key] = value
            elif callable(value):
                # This is a method
                class_attrs[key] = value
            elif not key.startswith('__'):
                # Other class attributes
                class_attrs[key] = value
        
        # Add field definitions
        class_attrs.update(field_definitions)
        
        # Create the Pydantic model class
        model_class = type(cls.__name__, (BaseModel,), class_attrs)
        
        return model_class
    
    return decorator


def field(
    type_def: TyckType,
    *,
    alias: Optional[str] = None,
    description: Optional[str] = None,
    title: Optional[str] = None,
    examples: Optional[list] = None,
    deprecated: bool = False,
) -> TyckType:
    """
    Helper to add metadata to a field in class-based definitions.
    
    Args:
        type_def: The TyckType defining the field's type and constraints
        alias: Optional alias for the field
        description: Optional description for the field
        title: Optional title for the field
        examples: Optional list of example values
        deprecated: Whether the field is deprecated
        
    Returns:
        Modified TyckType with the metadata
        
    Example:
        >>> from tyck import model, field, string
        >>> 
        >>> @model()
        ... class User:
        ...     name: field(
        ...         string.min(1).max(100),
        ...         alias="fullName",
        ...         description="The user's full name",
        ...         examples=["John Doe", "Jane Smith"]
        ...     )
    """
    result = type_def
    
    if alias:
        result = result.alias(alias)
    if description:
        result = result.description(description)
    if title:
        result = result.title(title)
    if examples:
        result = result.examples(*examples)
    if deprecated:
        result = result.deprecated(True)
    
    return result
