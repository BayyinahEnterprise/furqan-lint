// Idiom: function whose body is a macro invocation. Phase 1 cannot
// see through macro expansion; the body looks empty/opaque.
// Verdict: PASS (silent false negative). Rust analogue of R3
// (zero-return) is deferred to v0.7.1; until then this case is a
// documented limit.
// CST nodes: function_item, macro_invocation.

fn unimplemented_endpoint() -> i32 {
    todo!("wire this up before v1.0")
}
