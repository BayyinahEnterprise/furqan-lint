// Documented limit (v0.8.0): `select` statement bodies wrap as
// may-runs-0-or-N opaque IfStmt. The case-arm structure is
// discarded.
//
// Resolution path: a future phase may add channel-aware
// recognition.
package limits

func SelectOpaque(ch chan int) int {
	select {
	case v := <-ch:
		return v
	}
	return 0
}
