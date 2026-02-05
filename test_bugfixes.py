"""Test bug fixes"""
from tyck import interface, string, number, array
import math

print('=== Testing Bug Fixes ===')
print()

# Test 1: string.strip().lower()
print('1. string.strip().lower():')
Schema = interface({'name': string.strip().lower()})
obj = Schema(name='  HELLO WORLD  ')
print(f'   Input: "  HELLO WORLD  "')
print(f'   Output: "{obj.name}"')
print(f'   PASS' if obj.name == 'hello world' else '   FAIL')
print()

# Test 2: string.json()
print('2. string.json():')
Schema = interface({'data': string.json()})
try:
    obj = Schema(data='not valid json')
    print('   FAIL: Invalid JSON accepted')
except Exception as e:
    print(f'   PASS: Invalid JSON rejected')
print()

# Test 3: array().unique()
print('3. array().unique():')
Schema = interface({'tags': array(string).unique()})
try:
    obj = Schema(tags=['a', 'a', 'b'])
    print('   FAIL: Duplicates accepted')
except Exception as e:
    print(f'   PASS: Duplicates rejected')
print()

# Test 4: number.finite()
print('4. number.finite():')
Schema = interface({'value': number.finite()})
try:
    obj = Schema(value=math.inf)
    print('   FAIL: Infinity accepted')
except Exception as e:
    print(f'   PASS: Infinity rejected')
print()

# Test 5: string.upper()
print('5. string.upper():')
Schema = interface({'code': string.upper()})
obj = Schema(code='hello')
print(f'   Input: "hello"')
print(f'   Output: "{obj.code}"')
print(f'   PASS' if obj.code == 'HELLO' else '   FAIL')
