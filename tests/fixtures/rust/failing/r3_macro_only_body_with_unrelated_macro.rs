// Idiom: function body is a single eprintln!() macro invocation
// with semicolon. The macro name has nothing to do with
// divergence (eprintln just writes to stderr); R3 fires anyway
// because the structural pattern is "annotated return type +
// zero ReturnStmt", not "panic-like macro name".
// Verdict: MARAD zero_return_path (R3, ring-close) on `f`.
//
// This fixture is the load-bearing locking pin for the design
// decision in §3.2: R3 is grammar-and-macro-agnostic. Without
// this fixture, a future contributor might add a
// PANIC_MACROS = {"panic", "todo", ...} allowlist, which would
// narrow the checker incorrectly. The structural rule (zero
// ReturnStmt + non-None return type) catches this case
// correctly even though eprintln!() is not "diverging".
//
// Contrast with documented_limits/r3_panic_as_tail_expression.rs:
// that one PASSes because the missing ; turns the macro into a
// tail expression and the translator synthesizes a ReturnStmt.
// Same rule, different IR shape, different verdict. The rule
// is the rule; we don't pattern-match on macro identity.
// CST nodes: function_item, primitive_type,
// expression_statement, macro_invocation.

fn f() -> i32 {
    eprintln!("side effect only; nothing returned");
}
