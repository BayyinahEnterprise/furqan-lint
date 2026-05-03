// Idiom: async fn with Result return type.
// Verdict: PASS. async-ness is irrelevant to D24/D11; the translator
// treats async fn identically to fn for these checkers.
// CST nodes: function_item with `async` modifier, generic_type (Result),
// call_expression, scoped_identifier (Ok).

async fn fetch(id: u64) -> Result<String, std::io::Error> {
    Ok(format!("id={}", id))
}
