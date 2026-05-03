// Documented limit (v0.8.0): generic type parameters in
// function signatures are syntactically allowed; their
// constraints (`comparable`, `~int`, etc.) are ignored. The
// translator preserves the function name and arity but
// discards type-parameter information.
//
// Resolution path: a future phase may add type-parameter
// awareness once a concrete checker needs it.
package limits

func GenericIdentity[T any](v T) T {
	return v
}
