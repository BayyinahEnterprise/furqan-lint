// Idiom: ? operator for Result propagation; final tail expression
// is Ok(()).
// Verdict: PASS. The ? site is a call to a Result-producing function
// whose Err arm propagates; this is the canonical Rust honesty
// pattern, NOT a silent narrowing, so D11 must not fire on ?.
// CST nodes: function_item, generic_type (Result), try_expression,
// call_expression, scoped_identifier (Ok), unit_expression.

fn run() -> Result<(), std::io::Error> {
    inner()?;
    Ok(())
}

fn inner() -> Result<(), std::io::Error> {
    Ok(())
}
