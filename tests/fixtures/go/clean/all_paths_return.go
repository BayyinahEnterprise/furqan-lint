// Idiom: (int, error)-returning function with if/else where every
// path returns.
// Verdict: PASS (D24 satisfied: every control-flow path reaches
// a return).
// Pinning: tests/test_go_correctness.py::test_go_d24_clean_when_all_paths_return.

package allpaths

func Classify(x int) (int, error) {
	if x > 0 {
		return 1, nil
	} else {
		return -1, nil
	}
}
