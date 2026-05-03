// Fixture for the v0.8.3 Rust diff parse-error gate (round-21
// HIGH finding). Contains a syntactically broken function
// signature that tree-sitter recovers from but flags via
// has_error. The pinning tests assert that
// extract_public_names raises RustParseError on this input
// (rather than silently returning an empty frozenset and
// producing a false MARAD on the diff).

pub fn ){ broken
