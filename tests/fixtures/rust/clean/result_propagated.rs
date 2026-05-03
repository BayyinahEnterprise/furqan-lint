// Idiom: a function calls a Result<T, E>-returning helper and
// honestly propagates the may-fail union by declaring -> Result<T, E>
// itself. The caller's signature reflects that the operation may
// fail; consumers further up the stack must handle the Err arm.
// Verdict: PASS. D11 does not fire because the union is propagated,
// not narrowed.
// CST nodes: function_item, generic_type (Result), call_expression,
// try_expression (?-operator).

fn parse_helper(s: &str) -> Result<i32, String> {
    if s.is_empty() {
        return Err(String::from("empty input"));
    }
    Ok(42)
}

fn parse_age(s: &str) -> Result<i32, String> {
    // Honest propagation via ?-operator.
    let n = parse_helper(s)?;
    Ok(n)
}
