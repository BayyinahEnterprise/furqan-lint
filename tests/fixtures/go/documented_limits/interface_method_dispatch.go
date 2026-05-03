// Documented limit (v0.8.0): calls through interface receivers
// do not have a special model; the receiver type is opaque to
// the adapter, so D11's call-graph view sees the bare method
// name without dispatch resolution.
//
// Resolution path: a future phase may integrate `go/types`
// data to resolve interface method dispatch.
package limits

type Reader interface {
	Read() string
}

func InterfaceDispatch(r Reader) string {
	return r.Read()
}
