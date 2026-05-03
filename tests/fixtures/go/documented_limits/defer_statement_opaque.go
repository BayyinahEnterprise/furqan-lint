// Documented limit (v0.8.0): `defer` statements wrap as opaque.
// The deferred call's effect on control flow (panic recovery,
// resource cleanup) is not modeled.
//
// Resolution path: a future phase may add panic-recovery
// recognition.
package limits

func DeferOpaque() int {
	defer func() {}()
	return 0
}
