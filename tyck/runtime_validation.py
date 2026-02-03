"""Runtime validation for Tyck - ValidatedField and validate_call.

This module provides runtime type validation for Python variables and function calls.
"""

from __future__ import annotations

import functools
import inspect
from typing import Any, Callable, Dict, get_type_hints, Type, TypeVar, Union

from pydantic import BaseModel, ValidationError
from pydantic_core import PydanticUndefined

from tyck.core.builders import TypeBuilder


def _format_value(value: Any) -> str:
    """Format a value for display in error messages."""
    value_str = repr(value)
    if len(value_str) > 50:
        value_str = value_str[:47] + "..."
    return value_str


def _get_friendly_type_name(builder: TypeBuilder) -> str:
    """Get a user-friendly name for a type builder."""
    builder_type = type(builder).__name__
    # Map internal names to friendly names
    type_names = {
        'StringBuilder': 'text (string)',
        'IntegerBuilder': 'whole number (integer)',
        'FloatBuilder': 'decimal number (float)',
        'BooleanBuilder': 'true/false value (boolean)',
        'ListBuilder': 'list',
        'DictBuilder': 'dictionary',
        'OptionalBuilder': 'optional value',
    }
    return type_names.get(builder_type, builder_type.replace('Builder', '').lower())


def _create_field_error_message(
    field_name: str,
    builder: TypeBuilder,
    value: Any,
    original_error: str = ""
) -> str:
    """Create a user-friendly error message for field validation failures."""
    expected_type = _get_friendly_type_name(builder)
    actual_value = _format_value(value)
    actual_type = type(value).__name__
    
    message = f"Validation error for field '{field_name}':\n"
    message += f"  Expected: {expected_type}\n"
    message += f"  Received: {actual_type} with value {actual_value}\n"
    
    # Add helpful suggestions based on the type
    if 'StringBuilder' in str(type(builder)):
        message += "  Tip: Please provide a text value (e.g., 'hello' or \"world\")"
    elif 'IntegerBuilder' in str(type(builder)):
        message += "  Tip: Please provide a whole number (e.g., 42, -10, or 0)"
    elif 'FloatBuilder' in str(type(builder)):
        message += "  Tip: Please provide a number (e.g., 3.14, 42, or -0.5)"
    elif 'BooleanBuilder' in str(type(builder)):
        message += "  Tip: Please provide True or False"
    elif 'ListBuilder' in str(type(builder)):
        message += "  Tip: Please provide a list (e.g., [1, 2, 3])"
    elif 'DictBuilder' in str(type(builder)):
        message += "  Tip: Please provide a dictionary (e.g., {'key': 'value'})"
    
    if original_error and original_error not in message:
        message += f"\n  Details: {original_error}"
    
    return message


def _create_argument_error_message(
    param_name: str,
    builder: TypeBuilder,
    value: Any,
    original_error: str = ""
) -> str:
    """Create a user-friendly error message for argument validation failures."""
    expected_type = _get_friendly_type_name(builder)
    actual_value = _format_value(value)
    actual_type = type(value).__name__
    
    message = f"Validation error for argument '{param_name}':\n"
    message += f"  Expected: {expected_type}\n"
    message += f"  Received: {actual_type} with value {actual_value}\n"
    
    # Add helpful suggestions based on the type
    if 'StringBuilder' in str(type(builder)):
        message += "  Tip: Please provide a text value (e.g., 'hello' or \"world\")"
    elif 'IntegerBuilder' in str(type(builder)):
        message += "  Tip: Please provide a whole number (e.g., 42, -10, or 0)"
    elif 'FloatBuilder' in str(type(builder)):
        message += "  Tip: Please provide a number (e.g., 3.14, 42, or -0.5)"
    elif 'BooleanBuilder' in str(type(builder)):
        message += "  Tip: Please provide True or False"
    elif 'ListBuilder' in str(type(builder)):
        message += "  Tip: Please provide a list (e.g., [1, 2, 3])"
    elif 'DictBuilder' in str(type(builder)):
        message += "  Tip: Please provide a dictionary (e.g., {'key': 'value'})"
    
    if original_error and original_error not in message:
        message += f"\n  Details: {original_error}"
    
    return message


def _create_simple_type_error(
    name: str,
    expected: str,
    value: Any,
    is_return: bool = False
) -> str:
    """Create a user-friendly error message for simple type validation failures."""
    actual_value = _format_value(value)
    actual_type = type(value).__name__
    
    type_descriptions = {
        'str': 'text (string)',
        'int': 'whole number (integer)',
        'float': 'decimal number (float)',
        'bool': 'true/false value (boolean)',
        'bytes': 'bytes',
    }
    
    expected_friendly = type_descriptions.get(expected, expected)
    
    if is_return:
        message = f"Validation error for return value:\n"
    else:
        message = f"Validation error for argument '{name}':\n"
    
    message += f"  Expected: {expected_friendly}\n"
    message += f"  Received: {actual_type} with value {actual_value}\n"
    
    # Add helpful suggestions
    if expected == 'str':
        message += "  Tip: Please provide a text value in quotes (e.g., 'hello')"
    elif expected == 'int':
        message += "  Tip: Please provide a whole number without decimals (e.g., 42)"
    elif expected == 'float':
        message += "  Tip: Please provide a number (e.g., 3.14 or 42.0)"
    elif expected == 'bool':
        message += "  Tip: Please provide True or False (without quotes)"
    
    return message

F = TypeVar('F', bound=Callable[..., Any])


class ValidatedField:
    """A descriptor that validates values on assignment.
    
    Use this to add runtime type validation to class attributes.
    
    Example:
        >>> from Tyck import String, Integer
        >>> 
        >>> class User:
        ...     name = ValidatedField(String)
        ...     age = ValidatedField(Integer)
        >>> 
        >>> user = User()
        >>> user.name = "John"  # Works
        >>> user.name = 123     # Raises ValidationError!
    
    Args:
        builder: Tyck type builder (e.g., String, Integer)
        default: Optional default value
    """
    
    def __init__(self, builder: TypeBuilder, default: Any = PydanticUndefined):
        self.builder = builder
        self.default = default
        self.name = None  # Will be set by __set_name__
    
    def __set_name__(self, owner: Type[Any], name: str):
        """Called when the descriptor is assigned to a class attribute."""
        self.name = name
    
    def __get__(self, instance: Any, owner: Type[Any]) -> Any:
        """Get the value from the instance's dictionary."""
        if instance is None:
            return self
        
        # Return default if no value set
        if self.name not in instance.__dict__:
            if self.default is not PydanticUndefined:
                return self.default
            raise AttributeError(f"'{owner.__name__}' object has no attribute '{self.name}'")
        
        return instance.__dict__[self.name]
    
    def __set__(self, instance: Any, value: Any):
        """Validate and set the value."""
        # Validate using the type builder
        annotation, field_info = self.builder.to_field_info()
        
        # Create a temporary model to validate dynamically
        _TempValidator = type(
            "_TempValidator",
            (BaseModel,),
            {"__annotations__": {"value": annotation}, "value": field_info}
        )
        
        try:
            validated = _TempValidator(value=value)
            instance.__dict__[self.name] = validated.value
        except ValidationError as e:
            # Re-raise with user-friendly error message
            errors = e.errors()
            if errors:
                error_msg = errors[0].get('msg', '')
                field_name = self.name or 'unknown'
                friendly_msg = _create_field_error_message(
                    field_name, self.builder, value, error_msg
                )
                raise ValidationError(friendly_msg)
            raise


def validate_call(func: F) -> F:
    """Decorator to validate function arguments based on type hints.
    
    Validates all arguments against their type hints before executing the function.
    Works with Tyck types (String, Integer, etc.) and standard Python types.
    
    Example:
        >>> from Tyck import String, Integer
        >>> 
        >>> @validate_call
        ... def greet(name: String, age: Integer):
        ...     return f"Hello {name}, you are {age} years old"
        >>> 
        >>> greet("John", 25)     # Works
        >>> greet(123, "twenty")  # Raises ValidationError!
    
    Args:
        func: The function to validate
        
    Returns:
        Wrapped function with validation
    """
    
    # Get type hints from the function
    type_hints = get_type_hints(func)
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get function signature
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        
        # Validate each argument
        for param_name, value in bound_args.arguments.items():
            if param_name in type_hints:
                hint = type_hints[param_name]
                
                # Check if it's a Tyck builder
                if isinstance(hint, TypeBuilder):
                    # Validate using the builder
                    annotation, field_info = hint.to_field_info()
                    
                    _TempValidator = type(
                        "_TempValidator",
                        (BaseModel,),
                        {"__annotations__": {"value": annotation}, "value": field_info}
                    )
                    
                    try:
                        _TempValidator(value=value)
                    except ValidationError as e:
                        errors = e.errors()
                        if errors:
                            error_msg = errors[0].get('msg', '')
                            friendly_msg = _create_argument_error_message(
                                param_name, hint, value, error_msg
                            )
                            raise ValidationError(friendly_msg)
                        raise
                
                # Check if it's a standard Python type
                elif hint in (str, int, float, bool, bytes):
                    if not isinstance(value, hint):
                        friendly_msg = _create_simple_type_error(
                            param_name, hint.__name__, value
                        )
                        raise ValidationError(friendly_msg)
        
        # Call the original function
        return func(*args, **kwargs)
    
    return wrapper


# Alternative: validate_call with support for return type validation
def validate_call_with_return(func: F) -> F:
    """Decorator to validate function arguments AND return value.
    
    Same as validate_call, but also validates the return value.
    
    Example:
        >>> from Tyck import String, Integer
        >>> 
        >>> @validate_call_with_return
        ... def get_user_name(user_id: Integer) -> String:
        ...     return str(user_id)  # Works
        ...     # return user_id     # Would raise ValidationError!
    """
    
    type_hints = get_type_hints(func)
    return_hint = type_hints.get('return', None)
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Validate arguments (same as validate_call)
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        
        for param_name, value in bound_args.arguments.items():
            if param_name in type_hints:
                hint = type_hints[param_name]
                
                if isinstance(hint, TypeBuilder):
                    annotation, field_info = hint.to_field_info()
                    
                    _TempValidator = type(
                        "_TempValidator",
                        (BaseModel,),
                        {"__annotations__": {"value": annotation}, "value": field_info}
                    )
                    
                    try:
                        _TempValidator(value=value)
                    except ValidationError as e:
                        errors = e.errors()
                        if errors:
                            error_msg = errors[0].get('msg', '')
                            friendly_msg = _create_argument_error_message(
                                param_name, hint, value, error_msg
                            )
                            raise ValidationError(friendly_msg)
                        raise
                
                elif hint in (str, int, float, bool, bytes):
                    if not isinstance(value, hint):
                        friendly_msg = _create_simple_type_error(
                            param_name, hint.__name__, value
                        )
                        raise ValidationError(friendly_msg)
        
        # Call the function
        result = func(*args, **kwargs)
        
        # Validate return value if return type hint exists
        if return_hint is not None and return_hint is not type(None):
            if isinstance(return_hint, TypeBuilder):
                annotation, field_info = return_hint.to_field_info()
                
                _TempValidator = type(
                    "_TempValidator",
                    (BaseModel,),
                    {"__annotations__": {"value": annotation}, "value": field_info}
                )
                
                try:
                    _TempValidator(value=result)
                except ValidationError as e:
                    errors = e.errors()
                    if errors:
                        error_msg = errors[0].get('msg', '')
                        expected_type = _get_friendly_type_name(return_hint)
                        actual_value = _format_value(result)
                        actual_type = type(result).__name__
                        friendly_msg = (
                            f"Validation error for return value:\n"
                            f"  Expected: {expected_type}\n"
                            f"  Received: {actual_type} with value {actual_value}\n"
                            f"  Details: {error_msg}\n"
                            f"  Tip: Check that your function returns the correct type"
                        )
                        raise ValidationError(friendly_msg)
                    raise
            
            elif return_hint in (str, int, float, bool, bytes):
                if not isinstance(result, return_hint):
                    friendly_msg = _create_simple_type_error(
                        "return value", return_hint.__name__, result, is_return=True
                    )
                    raise ValidationError(friendly_msg)
        
        return result
    
    return wrapper
