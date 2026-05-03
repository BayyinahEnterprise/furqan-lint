// Idiom: function body is a single panic!() macro invocation
// followed by a semicolon, making it an expression_statement that
// the translator drops (zero ReturnStmt in the IR).
// Verdict: MARAD zero_return_path (R3, ring-close) on `f`.
// The trailing ';' is load-bearing: panic!() WITHOUT ; would be
// a tail expression and would synthesize a ReturnStmt (see
// documented_limits/r3_panic_as_tail_expression.rs for the
// no-semi case).
// CST nodes: function_item, primitive_type, block,
// expression_statement, macro_invocation.

fn f() -> i32 {
    panic!("not implemented");
}
