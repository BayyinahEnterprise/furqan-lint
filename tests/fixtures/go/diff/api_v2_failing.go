// Diff fixture v2 (failing): removes Client and NewClient. The
// additive-only diff should fire one MARAD per removed name.
package api

type Server struct{}

func NewServer() *Server {
	return &Server{}
}

var Version = "1.0"
