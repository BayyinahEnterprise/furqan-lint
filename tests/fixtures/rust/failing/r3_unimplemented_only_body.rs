// Idiom: function body is a single unimplemented!() macro with
// semicolon. Same pattern as panic!(); and todo!();.
// Verdict: MARAD zero_return_path (R3, ring-close) on `f`.
// The Option<T> return type translates to
// UnionType(T, TypePath("None")).
// CST nodes: function_item, generic_type (Option),
// expression_statement, macro_invocation.

fn f() -> Option<i32> {
    unimplemented!();
}
