// Idiom: function body is a single unreachable!() macro with
// semicolon. Same pattern as panic!(); todo!(); unimplemented!();.
// Verdict: MARAD zero_return_path (R3, ring-close) on `f`.
// CST nodes: function_item, primitive_type,
// expression_statement, macro_invocation.

fn f() -> i32 {
    unreachable!();
}
