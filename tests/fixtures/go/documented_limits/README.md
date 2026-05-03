# Go documented limits (v0.8.1)

Each Go limit here has a fixture in this directory and a
pinning test in `tests/test_go_documented_limits.py` (or
`tests/test_go_translator.py` for the older limits).

The contract these tests enforce is identical to the Rust and
Python documented_limits dirs: any change in fixture-vs-checker
behavior, in either direction, must be intentional and must
reflect in the test.

## Inventory

| Fixture | Limit | Introduced | Resolution path |
|---|---|---|---|
| `multi_return_three_or_more.go` | 3+-element returns translate to opaque `TypePath("<multi-return>")` | v0.8.0 | A future phase may add n-ary IR support |
| `two_element_non_error_tuple.go` | 2-element non-error tuples (e.g. `(int, string)`) translate to opaque `TypePath("(int, string)")` | v0.8.0 | Out of scope; locked decision 4 |
| `for_statement_opaque.go` | `for` / `range` bodies wrap as may-runs-0-or-N opaque IfStmt | v0.8.0 | A future phase may extend |
| `switch_statement_opaque.go` | `switch` bodies wrap as may-runs-0-or-N opaque IfStmt | v0.8.0 | A future phase may extend |
| `select_statement_opaque.go` | `select` bodies wrap as may-runs-0-or-N opaque IfStmt | v0.8.0 | A future phase may extend |
| `defer_statement_opaque.go` | `defer` statements wrap as opaque (deferred call ordering not modeled) | v0.8.0 | A future phase may extend |
| `interface_method_dispatch.go` | Calls through interface receivers are not specially modeled (the receiver type is opaque) | v0.8.0 | A future phase may add type-aware dispatch via `go/types` |
| `generic_type_parameters.go` | Generic type parameters in function signatures are syntactically allowed; their constraints are ignored | v0.8.0 | A future phase may add type-parameter awareness |
| `r3_compile_rejected.go` | R3 (zero-return) is documented not-applicable to Go: the compiler rejects all firing shapes | v0.8.1 | Predetermined; not a phase deferral |
| `method_conflation_v1.go`, `method_conflation_v2.go` | Same-named methods on distinct receivers collapse in `public_names`; diff false-negative on partial removal | v0.8.0 (pre-existing in goast) | v0.8.2 fixes via qualified method-name emission in goast |
| `diff_not_implemented_rust.rs` | Rust additive-only diff is not implemented in v0.8.1; see `tests/fixtures/rust/documented_limits/` for the mirror | v0.8.1 | v0.8.2 implements |

The Go adapter (current as of v0.8.1) ships D24, D11, and an
additive-only diff. R3 is documented not-applicable. The 8
v0.8.0 limits above remain unchanged in v0.8.1.
