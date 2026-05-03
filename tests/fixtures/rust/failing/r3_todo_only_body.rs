// Idiom: function body is a single todo!() macro invocation
// with semicolon. Same structural pattern as panic!(); ;.
// Verdict: MARAD zero_return_path (R3, ring-close) on `f`.
// The Result<T, E> return type translates to UnionType(T, E).
// CST nodes: function_item, generic_type (Result),
// expression_statement, macro_invocation.

fn f() -> Result<i32, String> {
    todo!();
}
