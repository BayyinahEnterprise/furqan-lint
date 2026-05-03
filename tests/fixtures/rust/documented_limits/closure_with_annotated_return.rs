// Idiom: closure with an explicit return-type annotation. Phase 1
// skips closure_expression nodes entirely (per prompt §3.4); the
// structural-honesty argument that motivates D24 is weaker for
// inline closures than for top-level functions. Phase 2 may revisit.
// Verdict: PASS (silent false negative on the closure body; the
// outer function `make_adder` itself is well-formed and PASSes).
// CST nodes: function_item (outer), closure_expression with explicit
// `->` return type, closure_parameters.

fn make_adder() -> i32 {
    let f = |x: i32| -> i32 {
        // Phase 1 skips this closure body even though it has an
        // explicit return type. v0.7.0 treats it as opaque.
    };
    let _ = f;  // silence unused
    7
}
