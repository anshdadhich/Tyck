# Building and Publishing Tyck to PyPI

## Quick Start

```bash
# 1. Build the package
python -m build

# 2. Upload to PyPI
python -m twine upload dist/*
```

## Detailed Steps

### 1. Install Build Tools

```bash
pip install build twine
```

### 2. Build the Package

```bash
# From the tyck/ directory (where pyproject.toml is)
cd tyck
python -m build
```

This creates:
- `dist/tyck-0.1.0-py3-none-any.whl` (wheel file)
- `dist/tyck-0.1.0.tar.gz` (source distribution)

### 3. Test the Build

```bash
# Check the package
twine check dist/*

# Test install locally
pip install dist/tyck-0.1.0-py3-none-any.whl

# Test it works
python -c "from tyck import interface, String; print('✓ Tyck installed successfully')"
```

### 4. Upload to TestPyPI (Recommended First)

```bash
# Upload to test.pypi.org first
twine upload --repository testpypi dist/*

# Test install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ tyck
```

### 5. Upload to Real PyPI

```bash
# Create API token at https://pypi.org/manage/account/token/
# Then upload
twine upload dist/*
```

### 6. Verify Installation

```bash
# Install from PyPI
pip install tyck

# Test it
python -c "
from tyck import interface, String, Integer

User = interface({
    'id': Integer.positive(),
    'name': String.min(1).max(100),
})

user = User(id=1, name='John')
print(user.model_dump())
"
```

## Version Updates

When releasing a new version:

1. Update version in `tyck/__init__.py`
2. Update CHANGELOG.md
3. Create git tag: `git tag v0.2.0`
4. Push tag: `git push origin v0.2.0`
5. Rebuild: `python -m build`
6. Upload: `twine upload dist/*`

## Files Created

- `pyproject.toml` - Package metadata and dependencies
- `tyck/__init__.py` - Package exports
- `tyck/types.py` - String, Number, Integer, Boolean, Array, etc.
- `tyck/interface.py` - interface() function
- `tyck/model.py` - @model decorator
- `tyck/utils.py` - pick_fields, omit_fields, etc.
- `README.md` - Package documentation
- `LICENSE` - MIT License
- `.gitignore` - Git ignore patterns
- `tests/` - Test suite

## Package Info

- **Name**: tyck
- **Version**: 0.1.0
- **Author**: Ansh Dadhich (anshdadhichmm@gmail.com)
- **License**: MIT
- **Python**: 3.8+
- **Dependencies**: pydantic>=2.0.0

## Next Steps

1. Create a GitHub repo: https://github.com/new
2. Push the code
3. Build and upload to PyPI
4. Install with: `pip install tyck`
