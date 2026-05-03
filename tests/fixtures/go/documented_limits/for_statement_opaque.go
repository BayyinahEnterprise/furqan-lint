// Documented limit (v0.8.0): `for` and `for-range` bodies wrap
// as may-runs-0-or-N opaque IfStmt. D24 cannot prove that a
// `for` body that always returns guarantees coverage.
//
// Resolution path: a future phase may extend if a concrete
// false negative warrants it.
package limits

func ForOpaque(items []int) int {
	for _, n := range items {
		return n
	}
	return 0
}
