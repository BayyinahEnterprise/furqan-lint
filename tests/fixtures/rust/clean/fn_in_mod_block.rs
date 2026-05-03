// Idiom: function_item nested inside mod_item.
// Verdict: PASS. R3.4-load-bearing: function discovery must walk
// mod_item bodies to find module-scoped functions.
// CST nodes: mod_item, function_item (inside mod).

mod inner {
    pub fn double(x: i32) -> i32 {
        x * 2
    }
}

fn outer() -> i32 {
    inner::double(7)
}
