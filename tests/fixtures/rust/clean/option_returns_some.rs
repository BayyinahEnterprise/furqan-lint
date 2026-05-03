// Idiom: Option<T> return with explicit Some(_) tail expression.
// Verdict: PASS. D11 must treat Option<T> as a UnionType-with-None-arm
// (mirroring Python Optional[T] -> UnionType(T, None)) so an
// Option-returning helper called by an Option-returning caller does
// NOT fire D11 status_collapse.
// CST nodes: function_item, generic_type (Option), call_expression,
// scoped_identifier (Some).

fn maybe(n: i32) -> Option<i32> {
    Some(n + 1)
}
