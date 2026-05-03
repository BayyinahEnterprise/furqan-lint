// Idiom: while-let with a return after the loop. The loop is opaque
// (may run zero or N times); the post-loop return covers the falls-
// through path.
// Verdict: PASS (D24 satisfied: the unconditional final return).
// CST nodes: function_item, while_let_expression, return_expression.

fn count_until_zero(mut n: i32) -> i32 {
    let mut count = 0;
    while let Some(_) = (n > 0).then_some(()) {
        count += 1;
        n -= 1;
    }
    return count;
}
