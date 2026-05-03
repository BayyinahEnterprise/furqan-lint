// Documented limit (v0.8.1): R3 (zero-return) is not applicable
// to Go. The Go compiler rejects functions with annotated
// return types and no return statement at compile time:
//
//   func F() int { }          // compile error: missing return
//   func F() (r int) { }      // compile error: missing return
//
// Named returns with bare `return` DO compile (the named
// returns implicitly initialize as zero values), but the
// `return` keyword means body_statements is non-empty, so R3
// would NOT fire even if it were wired into the Go runner.
//
// This fixture is the nearest-edge compilable case. The
// pinning test asserts three claims:
//   1. furqan-lint correctly does NOT fire any diagnostic
//      (R3 is not wired into the Go runner; D24 sees a return
//      statement and PASSes).
//   2. The fixture compiles cleanly under `go build` (verified
//      via a transient go.mod + entry.go in tmp_path).
//   3. A counter-example with no return statement at all is
//      rejected by `go build` with 'missing return' (proving
//      the limit is not applicable -- R3's firing condition is
//      unreachable on any compilable Go source).

package main

func NearestEdge() (result int) {
	return
}
