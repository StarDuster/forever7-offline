"""Test package bootstrap for both script and ``python -m unittest`` entrypoints."""
import sys

from . import _paths as _paths_module

# Existing test modules import the shared bootstrap as a top-level module.
# Register the same module object when tests are loaded through the package.
sys.modules.setdefault('_paths', _paths_module)
