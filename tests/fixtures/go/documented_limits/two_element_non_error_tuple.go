// Documented limit (v0.8.0): 2-element non-error tuple returns
// (e.g. `(int, string)`) translate to opaque
// TypePath("(int, string)"). D11's may-fail predicate does NOT
// fire on these; only `(T, error)` shapes are recognized as
// may-fail per locked decision 4.
//
// Resolution path: out of scope; locked decision 4.
package limits

func TwoNonError() (int, string) {
	return 0, ""
}
