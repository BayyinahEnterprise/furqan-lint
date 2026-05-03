// Documented limit (v0.8.0): `switch` statement bodies wrap as
// may-runs-0-or-N opaque IfStmt. D24 cannot recognize an
// exhaustive switch with a `default` arm as guaranteed
// coverage.
//
// Resolution path: a future phase may add exhaustive-switch
// recognition by detecting a `default` clause and splicing it
// into a synthesized IfStmt's else_body.
package limits

func SwitchOpaque(n int) string {
	switch n {
	case 0:
		return "zero"
	default:
		return "nonzero"
	}
}
