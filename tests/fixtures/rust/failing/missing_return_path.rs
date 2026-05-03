// Idiom: if-without-else; the `if` body returns but the trailing
// statement is a side-effect with no return; D24 fires.
// Verdict: MARAD all_paths_return on `classify` (Case P1: the
// fall-through path runs the trailing statement and reaches the
// end of the block without a value).
// CST nodes: function_item, if_expression (no else clause),
// return_expression, expression_statement, call_expression.

fn classify(x: i32) -> i32 {
    if x > 0 {
        return 1;
    }
    println!("negative or zero");
    // Falls through to end of block without producing an i32.
}
