"""Type exports for Tyck."""

from tyck.core.builders import (
    AnyBuilder,
    BooleanBuilder,
    BytesBuilder,
    DateTimeBuilder,
    DecimalBuilder,
    NoneBuilder,
    NumberBuilder,
    StringBuilder,
    UUIDBuilder,
)

# Create singleton instances that will be cloned when methods are called
String = StringBuilder()
Number = NumberBuilder(is_integer=False)
Integer = NumberBuilder(is_integer=True)
Boolean = BooleanBuilder()
DateTime = DateTimeBuilder(type_='datetime')
Date = DateTimeBuilder(type_='date')
Time = DateTimeBuilder(type_='time')
Uuid = UUIDBuilder()
Bytes = BytesBuilder()
Decimal = DecimalBuilder()
AnyType = AnyBuilder()
NoneType = NoneBuilder()

__all__ = [
    # Builder classes
    'StringBuilder',
    'NumberBuilder',
    'BooleanBuilder',
    'DateTimeBuilder',
    'UUIDBuilder',
    'BytesBuilder',
    'DecimalBuilder',
    'AnyBuilder',
    'NoneBuilder',
    # Singletons (will be cloned on use)
    'String',
    'Number',
    'Integer',
    'Boolean',
    'DateTime',
    'Date',
    'Time',
    'Uuid',
    'Bytes',
    'Decimal',
    'AnyType',
    'NoneType',
]
