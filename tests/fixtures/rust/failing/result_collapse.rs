// Idiom: a function declares -> i32 (a concrete type) but its body
// calls a Result<T, E>-returning helper and silently unwraps the
// error arm via panic. The caller's signature lies about what the
// function actually does (it might panic, but the caller has no
// indication from the type).
// Verdict: MARAD status_coverage (D11) on `parse_age` (Case S1:
// caller silently narrows the union the producer declared).
// CST nodes: function_item, generic_type (Result), call_expression,
// match_expression, macro_invocation (panic).
//
// Phase 2 D11 (v0.7.1) only fired on Option-returning helpers
// (UnionType with a None arm). v0.7.2 widens the producer
// predicate to include Result<T, E> (UnionType where neither arm
// is None). Without the widening, this fixture passes silently;
// with it, D11 fires.

fn parse_helper(s: &str) -> Result<i32, String> {
    if s.is_empty() {
        return Err(String::from("empty input"));
    }
    Ok(42)
}

fn parse_age(s: &str) -> i32 {
    // Calls a Result-returning helper but declares -> i32.
    // The Err arm is collapsed via panic; D11 fires.
    match parse_helper(s) {
        Ok(n) => n,
        Err(_) => panic!("bad input"),
    }
}
