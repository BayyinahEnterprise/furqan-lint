// Idiom: only one branch of an if/else returns; the other
// produces no value. Distinct from missing_return_path.rs because
// here the else branch IS present, just not return-terminating.
// Verdict: MARAD all_paths_return on `pick` (Case P1: the else
// arm runs a side-effect call without yielding an i32).
// CST nodes: function_item, if_expression with else clause,
// return_expression, expression_statement.

fn pick(x: i32) -> i32 {
    if x > 0 {
        return x;
    } else {
        println!("non-positive");
        // Else branch falls through with no value.
    }
}
