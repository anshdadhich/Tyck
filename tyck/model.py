"""Model decorator for class-based schema definitions."""

from typing import Type, Any, Callable, get_type_hints
from pydantic import BaseModel
from .types_ import TyckType


def model(*, frozen: bool = False, strict: bool = False) -> Callable[[Type], Type[BaseModel]]:
    """
    Decorator to convert a class into a Pydantic model with Tyck support.
    
    This allows using Tyck's fluent API within class definitions while
    maintaining full Pydantic functionality.
    
    Args:
        frozen: Whether the model is immutable
        strict: Whether to use strict validation
        
    Returns:
        A decorator that converts the class to a Pydantic model
        
    Example:
        >>> from tyck import model, String
        >>> 
        >>> @model()
        ... class User:
        ...     name: String.min(1)
        ...     email: String.email()
        ...     
        ...     def greet(self) -> str:
        ...         return f"Hello, {self.name}!"
        >>> 
        >>> user = User(name="John", email="john@example.com")
        >>> user.greet()
        'Hello, John!'
    """
    def decorator(cls: Type) -> Type[BaseModel]:
        # Get type hints from the class
        hints = get_type_hints(cls, include_extras=True)
        
        # Build field definitions
        fields = {}
        for attr_name, hint in hints.items():
            if isinstance(hint, TyckType):
                fields[attr_name] = hint.build()
            else:
                fields[attr_name] = hint
        
        # Create config dict
        config = {}
        if frozen:
            config['frozen'] = True
        if strict:
            config['strict'] = True
        
        # Create the Pydantic model
        model_class = type(
            cls.__name__,
            (BaseModel,),
            {
                '__annotations__': fields,
                '__module__': cls.__module__,
                '__doc__': cls.__doc__,
                '__qualname__': cls.__qualname__,
                'model_config': config,
                **{k: v for k, v in cls.__dict__.items() if not k.startswith('_')},
            }
        )
        
        return model_class
    
    return decorator
