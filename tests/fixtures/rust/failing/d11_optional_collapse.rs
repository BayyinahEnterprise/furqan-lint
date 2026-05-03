// Idiom: caller silently narrows an Option-returning helper.
// Verdict: MARAD status_coverage on `find_age` (Case S1: caller
// declares `i32` but the helper returns Option<i32>; the consumer-
// side honesty discipline requires propagation, not silent unwrap-
// or-default).
// CST nodes: function_item, generic_type (Option), call_expression,
// scoped_identifier (Some), match_expression with non-propagating
// arm.
//
// Phase 1 D11 fires on Option (translated to UnionType(T, None));
// Result-returning helpers are out of scope until v0.7.x adds a
// Rust-specific producer_predicate. The Python-adapter parity is
// the same: D11 fires on Optional[T], not on a generic two-arm
// Union.

fn lookup(id: u64) -> Option<i32> {
    if id == 0 {
        return None;
    }
    return Some(42);
}

fn find_age(id: u64) -> i32 {
    // Calls an Option-returning function but declares plain i32.
    // The None arm is collapsed via unwrap-or-default; the union
    // is silently narrowed away. D11 fires.
    match lookup(id) {
        Some(n) => n,
        None => 0,
    }
}
