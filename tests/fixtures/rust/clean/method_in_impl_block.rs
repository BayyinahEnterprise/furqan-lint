// Idiom: function_item nested inside impl_item (a method).
// Verdict: PASS. R3.4-load-bearing per prompt: function discovery
// must walk impl_item bodies recursively to find methods.
// CST nodes: impl_item, struct_item, function_item (inside impl).

struct Counter {
    value: i32,
}

impl Counter {
    fn current(&self) -> i32 {
        self.value
    }
}
