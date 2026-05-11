// Phase G11.2 (al-Mursalat / v0.12.0) Go smoke-test fixture.
//
// Minimal Go module with a single public function that has the
// canonical may-fail (T, error) signature -- the smoke test
// signs this file via Sigstore (ambient OIDC under GitHub
// Actions) and verifies the resulting bundle dispatches
// through verification.verify -> _verify_go.
//
// Per F22 closure across all three substrates at v0.12.0:
// gate11-go-smoke-test runs the sign-then-verify round-trip
// the same way gate11-rust-smoke-test does for Rust and
// gate11-smoke-test does for Python. CASM-V-001 fail-closed
// is the prior failure shape; post-v0.12.0 the dispatch
// reaches _verify_go cleanly.

package smoke

// Smoke is the single public function pinned by the
// gate11-go-smoke-test fixture. Returns (result, error) per
// the Go may-fail convention; canonicalization rule 7
// iterates the return tuple as a list of types, not as a
// stringified "(int, error)".
func Smoke(a int, b int) (int, error) {
	return a + b, nil
}
