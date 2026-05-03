// Idiom: function with explicit lifetime parameter on the return
// type. Phase 1 strips lifetime annotations during translation;
// `fn f<'a>(...) -> &'a str` is treated as `-> str`.
// Verdict: PASS. Limit: D11 cannot reason about lifetimes; the
// translation is lossy in a way that does not affect D24's
// path-coverage logic but would affect a future borrow-pattern
// checker.
// CST nodes: function_item, type_parameters (with lifetime),
// reference_type, lifetime.

fn first_word<'a>(s: &'a str) -> &'a str {
    s.split_whitespace().next().unwrap_or("")
}
