// Documented limit (v0.8.3): impl-block methods are NOT
// collected by the Rust adapter's extract_public_names. The
// extractor walks only top-level CST root children; methods
// inside `impl Type { ... }` blocks live one level deeper and
// are intentionally skipped.
//
// Asymmetry with Go (intentional): the Go adapter (as of v0.8.2)
// emits qualified method names like `Counter.increment` from
// goast. The Rust adapter does not yet do the equivalent walk
// into impl bodies. Reasoning: the public-name diff use case
// is dominated by top-level item additions and removals;
// per-method receivers require additional CST surface
// (impl_item -> declaration_list -> function_item children)
// that v0.8.3 does not implement. Rust impl-method collection
// is registered as a v0.8.4 candidate.
//
// Verdict: extract_public_names returns frozenset({"Counter"})
// only. The two impl methods (`increment`, `get`) are silently
// omitted. The pinning test lives in
// `tests/test_rust_correctness.py::test_rust_extract_omits_impl_methods`.

pub struct Counter {
    value: u32,
}

impl Counter {
    pub fn increment(&mut self) {
        self.value += 1;
    }

    pub fn get(&self) -> u32 {
        self.value
    }
}
