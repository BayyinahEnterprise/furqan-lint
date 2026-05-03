// Idiom: match where some arms return but at least one falls
// through with a side-effect-only body.
// Verdict: MARAD all_paths_return on `route` (Case P1: the wildcard
// arm runs a print but does not return).
// CST nodes: function_item, match_expression, match_arm,
// return_expression, macro_invocation.

fn route(code: i32) -> i32 {
    match code {
        0 => return 100,
        1 => return 200,
        _ => {
            println!("unknown route");
            // No return; falls through.
        }
    }
}
