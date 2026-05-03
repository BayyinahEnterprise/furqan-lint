// Idiom: (int, error)-returning function with if branch that
// returns but no return on the fall-through path.
// Verdict: MARAD all_paths_return on Classify (Case P1 - missing
// return path).
// Pinning: tests/test_go_correctness.py::test_go_d24_fires_on_missing_return.

package missing

func Classify(x int) (int, error) {
	if x > 0 {
		return 1, nil
	}
	// Falls through to end of function with no return.
	// rustc would catch this; the Go compiler also catches it
	// (missing return at end of function), but linters that only
	// walk syntax may miss the structural firing condition.
}
