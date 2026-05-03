// Documented limit (v0.8.0): 3+-element return signatures
// translate to opaque TypePath("<multi-return>") rather than
// an n-ary IR encoding. D24 and D11 still see the function but
// cannot reason about the individual arms.
//
// Resolution path: a future phase may add n-ary IR support if a
// concrete user-reported false negative warrants it.
package limits

func ThreeReturns() (int, string, error) {
	return 0, "", nil
}
