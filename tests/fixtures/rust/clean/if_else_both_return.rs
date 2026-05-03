// Idiom: if/else where both arms terminate in return.
// Verdict: PASS (D24 satisfied: every control-flow path reaches a return).
// CST nodes: function_item, if_expression, block, return_expression.

fn classify(x: i32) -> i32 {
    if x > 0 {
        return 1;
    } else {
        return -1;
    }
}
