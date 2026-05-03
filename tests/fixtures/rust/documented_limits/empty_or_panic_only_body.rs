// Idiom: function whose body is empty, or contains only a single
// `panic!()` / `todo!()` / `unimplemented!()` macro invocation.
// Verdict: PASS (silent false negative). Phase 1 does not flag
// zero-statement / panic-only bodies because the Rust analogue of
// R3 (ring-close) is deferred to v0.7.1. Python's R3 catches the
// equivalent case (`def f() -> int: pass`); Rust's does not yet.
// CST nodes: function_item, block (empty or single macro_invocation).

fn empty_body() -> i32 {
}

fn panic_body() -> i32 {
    panic!("not yet implemented")
}
