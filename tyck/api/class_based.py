"""Class-based API for Tyck - @model()/@schema() decorator."""

from __future__ import annotations

import inspect
from typing import Any, Callable, cast, Dict, Literal, Optional, Tuple, Type, TypeVar, get_type_hints

from pydantic import BaseModel, ConfigDict, create_model
from pydantic.fields import FieldInfo

from tyck.core.builders import TypeBuilder

T = TypeVar('T')


def model(
    config: Optional[ConfigDict] = None,
    validators: Optional[Dict[str, Callable]] = None,
    base: Optional[Type[BaseModel]] = None,
    frozen: bool = False,
    strict: bool = False,
    extra: Optional[Literal['allow', 'ignore', 'forbid']] = None,
) -> Callable[[Type[T]], Type[BaseModel]]:
    """Decorator to convert a class to a Pydantic model.
    
    This is the class-based API for creating Tyck models. It allows you to
    define models using Python class syntax with Tyck builders.
    
    Note: @schema() is an alias for @model() - they are identical.
    
    Args:
        config: Optional Pydantic configuration dictionary
        validators: Optional dictionary of custom validator functions
        base: Optional base class to inherit from
        frozen: Whether the model is immutable (shorthand for config)
        strict: Whether to use strict type checking (shorthand for config)
        extra: How to handle extra fields (shorthand for config)
        
    Returns:
        Decorator function that converts a class to a Pydantic model
        
    Examples:
        Basic usage:
        >>> from Tyck import model, String, Integer
        >>> @model()  # You can also use @schema()
        ... class User:
        ...     id: Integer.positive()
        ...     name: String.min(1).max(100)
        ...     email: String.email()
        >>> user = User(id=1, name="John", email="john@example.com")
        
        With configuration:
        >>> @model(frozen=True, strict=True)  # You can also use @schema()
        ... class User:
        ...     name: String
        
        With methods:
        >>> @model()  # You can also use @schema()
        ... class User:
        ...     name: String
        ...     
        ...     def greet(self) -> str:
        ...         return f"Hello, {self.name}!"
        >>> user = User(name="John")
        >>> user.greet()  # "Hello, John!"
        
        With inheritance:
        >>> @model()  # You can also use @schema()
        ... class BaseUser:
        ...     id: Integer.positive()
        ...     name: String
        >>> @model()  # You can also use @schema()
        ... class Admin(BaseUser):
        ...     role: String.default("admin")
    """
    def decorator(cls: Type[T]) -> Type[BaseModel]:
        # Get the class name and module
        class_name = cls.__name__
        class_module = cls.__module__
        
        # Check if this class inherits from a Pydantic model
        # If so, we need to handle inheritance specially
        parent_pydantic_model = None
        for parent in cls.__bases__:
            if isinstance(parent, type) and issubclass(parent, BaseModel) and parent is not BaseModel:
                parent_pydantic_model = parent
                break
        
        # Get annotations defined directly on this class (not inherited)
        # We need to filter out annotations from parent classes to avoid
        # re-processing inherited fields when a child class inherits from
        # a Pydantic model created by the @model decorator
        # Use __dict__ to get only this class's annotations, not inherited ones
        hints = cls.__dict__.get('__annotations__', {})
        
        # Convert type builders to Pydantic fields
        fields: Dict[str, Any] = {}
        for attr_name, annotation in hints.items():
            if isinstance(annotation, TypeBuilder):
                # Convert TypeBuilder to FieldInfo
                fields[attr_name] = annotation.to_field_info()
            elif isinstance(annotation, type) and issubclass(annotation, BaseModel):
                # Nested model
                fields[attr_name] = (annotation, ...)
            elif isinstance(annotation, FieldInfo):
                # Already a FieldInfo
                fields[attr_name] = annotation
            elif hasattr(annotation, '__origin__'):
                # Generic type (List, Dict, Optional, etc.)
                fields[attr_name] = (annotation, ...)
            else:
                # Regular type annotation
                fields[attr_name] = (annotation, ...)
        
        # Build configuration
        model_config = config or {}
        if frozen:
            model_config['frozen'] = True
        if strict:
            model_config['strict'] = True
        if extra:
            model_config['extra'] = extra
        
        # Prepare base classes
        # Check if any of the class's bases are Pydantic models
        # If so, use them as the base to enable proper inheritance
        bases: Tuple[Type[Any], ...]
        if base:
            bases = (base,)
        elif parent_pydantic_model:
            # Inherit from the parent Pydantic model
            bases = (parent_pydantic_model,)
        else:
            bases = (BaseModel,)
        
        # Create the model
        model_class = create_model(
            class_name,
            __base__=bases,
            __module__=class_module,
            __config__=model_config if model_config else None,
            __validators__=validators or {},
            **fields
        )
        
        # Add to_json_schema method as an alias for model_json_schema
        def to_json_schema(cls, **kwargs):
            """Generate a JSON Schema for the model.
            
            This is an alias for model_json_schema() for convenience.
            
            Args:
                **kwargs: Additional arguments to pass to model_json_schema()
                
            Returns:
                Dict containing the JSON Schema
            """
            return cls.model_json_schema(**kwargs)
        
        # Bind the method to the class
        model_class.to_json_schema = classmethod(to_json_schema)
        
        # Copy over methods and attributes from original class
        for attr_name in dir(cls):
            if not attr_name.startswith('_') and attr_name not in fields:
                attr_value = getattr(cls, attr_name)
                if callable(attr_value) and not isinstance(attr_value, type):
                    # It's a method
                    setattr(model_class, attr_name, attr_value)
                elif not inspect.ismethod(attr_value) and not inspect.isfunction(attr_value):
                    # It's a class attribute
                    setattr(model_class, attr_name, attr_value)
        
        # Copy docstring
        if cls.__doc__:
            model_class.__doc__ = cls.__doc__
        
        return model_class
    
    return decorator


# Alias: schema is the same as model
schema = model


def field(
    builder: TypeBuilder,
    alias: Optional[str] = None,
    description: Optional[str] = None,
    title: Optional[str] = None,
    examples: Optional[list] = None,
    deprecated: bool = False,
    **kwargs: Any
) -> Tuple[type, FieldInfo]:
    """Create a field with additional metadata.
    
    This is a helper function to create fields with extra metadata
    beyond what the type builder provides.
    
    Args:
        builder: Type builder for this field
        alias: Alternative name for this field
        description: Field description
        title: Field title
        examples: Example values
        deprecated: Whether this field is deprecated
        **kwargs: Additional field kwargs
        
    Returns:
        Pydantic FieldInfo
        
    Example:
        >>> from Tyck import model, field, String
        >>> @model()  # You can also use @schema()
        ... class User:
        ...     name: field(String, alias="fullName", description="The user's full name")
    """
    field_type, field_info = builder.to_field_info()
    
    # Update with additional metadata
    if alias:
        field_info.alias = alias
    if description:
        field_info.description = description
    if title:
        field_info.title = title
    if examples:
        field_info.examples = examples
    if deprecated:
        field_info.deprecated = deprecated
    
    # Update with any additional kwargs
    for key, value in kwargs.items():
        setattr(field_info, key, value)
    
    return (field_type, field_info)
