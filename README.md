# furqan-lint

Structural-honesty checks for Python, powered by [Furqan](https://tryfurqan.com).

`furqan-lint` translates Python source into the Furqan AST and runs the
subset of Furqan checkers whose semantics carry across language boundaries
into idiomatic Python. Phase 1 ships two checks:

- **D24 (all-paths-return)** every control-flow path through a typed
  function reaches a return statement.
- **D11 (status-coverage)** when a function returns `Optional[X]`, every
  caller either propagates the optionality or explicitly handles `None`.
  A caller that silently collapses `Optional[X]` into a non-optional return
  type is the structural equivalent of dropping the `Incomplete` arm of
  Furqan's `Integrity | Incomplete` union.

## Install

```bash
pip install furqan-lint
```

Requires Python 3.10+ and `furqan>=0.10.1`.

## Usage

```bash
furqan-lint check path/to/file.py
furqan-lint check path/to/directory/
furqan-lint version
```

## Example

```python
# example.py
from typing import Optional

def find_record(id: int) -> Optional[dict]:
    if id <= 0:
        return None
    return {"id": id}

def get_name(id: int) -> str:
    record = find_record(id)
    if record is not None:
        return record["name"]
    # Missing else: falls through with no return
```

```
$ furqan-lint check example.py

MARAD  example.py
  2 violation(s):
    [all_paths_return] Function 'get_name' at line 8 declares
    -> str but not every control-flow path reaches a return
    statement.
      fix: Add a return statement to the else branch or after
      the if block.

    [status_coverage] Function 'get_name' at line 8 calls
    'find_record' (returns Optional[dict]) but declares -> str.
    The Optional is silently collapsed.
      fix: Change return type to Optional[str].
```

## Phase 1 scope and known gaps

Phase 1 wires two of Furqan's ten checkers to Python. The remaining eight
require Python-specific conventions (scope declarations, layer annotations,
calibration bounds, dependency mapping) that do not exist in standard
Python. Documented gaps in `Section 8` of the implementation prompt:

1. `return None` with a non-Optional declared return type is treated as a
   satisfied path by D24. Phase 2 adds D22 (return-type match) which closes
   this gap.
2. The D11 producer detection uses a scoped monkey-patch on
   `status_coverage._is_integrity_incomplete_union`. Phase 2 adds a
   `producer_predicate` parameter to `check_status_coverage` upstream.
3. Class methods are extracted as top-level functions; calls written as
   `self.validate()` are matched on the attribute name `validate` only.
4. Only D24 and D11 run. The other eight checkers require language-level
   constructs Python does not have.
5. Calls inside nested functions are attributed to the enclosing function.

## License

Apache-2.0.
