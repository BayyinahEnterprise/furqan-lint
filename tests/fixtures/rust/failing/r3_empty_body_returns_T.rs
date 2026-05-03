// Idiom: function declares non-unit return type but the body is
// completely empty. Rust compiler would also flag this (E0308:
// mismatched types), but linters that only walk the AST may miss
// it.
// Verdict: MARAD zero_return_path (R3, ring-close) on `f`.
// Distinct from D24: D24 needs at least one return present to
// fire (Case P1 = partial coverage); R3 fires on the zero-return
// shape. Pinning test asserts EXACTLY ONE diagnostic (the R3
// suppression of D24 path is exercised here).
// CST nodes: function_item, primitive_type, block (empty).

fn f() -> i32 {}
