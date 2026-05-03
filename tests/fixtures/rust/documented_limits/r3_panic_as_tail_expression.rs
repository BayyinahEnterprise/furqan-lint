// Documented limitation: panic!() (or any diverging macro) used
// as a tail expression with no trailing ';' is NOT flagged by
// R3 in v0.7.1, even though the function structurally produces
// no value.
// Verdict: PASS (silent false negative).
//
// Why R3 does not fire: the tree-sitter-rust grammar treats a
// macro invocation without ';' at block end as a tail
// expression. The translator (per the v0.7.0 R1 rule for
// implicit-return tail expressions) synthesizes a
// ReturnStmt(opaque) for any tail expression. So
// `fn f() -> i32 { panic!() }` produces statements=1 with a
// ReturnStmt, and check_ring_close does not fire R3 (zero-return
// is the firing condition).
//
// Why we don't flag it anyway: doing so would require either
// (a) a hardcoded PANIC_MACROS = {"panic", "todo",
// "unimplemented", "unreachable"} allowlist, which is
// brittle (third-party diverging macros like never_return!()
// would not be caught), or (b) cross-file type inference of
// the macro's expansion type to detect divergence (this needs
// a Rust type checker, out of scope).
//
// Phase 3 may revisit if the Rust ecosystem standardizes a
// #[diverging] attribute on macros, or if a user-reported false
// negative makes the cost worth it.
//
// Compare with failing/r3_panic_only_body.rs: same `panic!()`
// invocation but WITH trailing ';' fires R3. The semicolon is
// load-bearing because it determines whether tree-sitter-rust
// parses the macro as a statement (translator drops it) or as
// a tail expression (translator synthesizes a ReturnStmt).
// CST nodes: function_item, primitive_type, block,
// macro_invocation (no enclosing expression_statement).

fn f() -> i32 {
    panic!("never returns, but R3 misses it because no ';'")
}
