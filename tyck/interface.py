"""Interface function to create Pydantic models from dictionaries."""

from typing import Dict, Any, Type, get_type_hints
from pydantic import BaseModel, create_model, Field
from pydantic.fields import FieldInfo
from .types_ import TyckType


def interface(fields: Dict[str, Any]) -> Type[BaseModel]:
    """
    Create a Pydantic model from a dictionary of fields.
    
    This is the core function of Tyck that converts dictionary-based
    schema definitions into fully functional Pydantic models.
    
    Args:
        fields: Dictionary mapping field names to type validators or type annotations
        
    Returns:
        A Pydantic BaseModel subclass
        
    Example:
        >>> from tyck import interface, String, Integer
        >>> 
        >>> User = interface({
        ...     'id': Integer.positive(),
        ...     'name': String.min(1).max(100),
        ... })
        >>> 
        >>> user = User(id=1, name="John")
        >>> print(user.model_dump())
        {'id': 1, 'name': 'John'}
    """
    pydantic_fields = {}
    
    for name, field_def in fields.items():
        if isinstance(field_def, TyckType):
            # Handle Tyck type validators
            result = field_def.build()
            if isinstance(result, tuple):
                # Some validators return (type, FieldInfo) tuples
                pydantic_fields[name] = result
            else:
                # Others return just FieldInfo
                pydantic_fields[name] = result
        elif isinstance(field_def, FieldInfo):
            # Handle direct Pydantic Field instances
            pydantic_fields[name] = field_def
        elif isinstance(field_def, tuple) and len(field_def) == 2:
            # Handle (type, FieldInfo) tuples directly
            pydantic_fields[name] = field_def
        else:
            # Handle raw types (int, str, etc.)
            pydantic_fields[name] = field_def
    
    # Create the model using Pydantic's create_model
    model = create_model(
        'TyckModel',
        **pydantic_fields,
        __base__=BaseModel,
        __module__=__name__,
    )
    
    return model
