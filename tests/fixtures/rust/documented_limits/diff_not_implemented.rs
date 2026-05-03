// Documented limit (v0.8.1): Rust additive-only diff is not
// implemented. The Rust adapter does not yet extract public
// names: module.functions contains all functions regardless of
// `pub` visibility, and structs/enums/consts are not collected
// at all.
//
// Building the extractor requires ~50-100 lines of tree-sitter
// CST walking. Deferred to v0.8.2 per locked decision 2.
//
// Verdict: `furqan-lint diff foo.rs bar.rs` returns exit 2
// (PARSE ERROR) with the message "Rust diff not implemented in
// v0.8.1. See CHANGELOG for the v0.8.2 schedule."
//
// This fixture is documentation; the pinning test exercises
// the contract via tmp_path-generated trivial .rs files in
// `tests/test_rust_diff_not_implemented.py`.

pub fn example() -> i32 {
    0
}
