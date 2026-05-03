// Idiom: tail-expression implicit return (no semicolon, no `return` keyword).
// Verdict: PASS. R1-load-bearing per validator finding: missing this
// detection produces silent false negatives on the most common Rust
// shape `fn f() -> T { expr }`.
// CST nodes: function_item, block, integer_literal (as block tail
// expression, not as statement).

fn answer() -> i32 {
    42
}
