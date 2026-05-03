// Idiom: match where every arm body returns.
// Verdict: PASS (D24 satisfied via per-arm return).
// CST nodes: function_item, match_expression, match_arm, return_expression.

fn classify(x: i32) -> i32 {
    match x {
        0 => return 0,
        n if n > 0 => return 1,
        _ => return -1,
    }
}
