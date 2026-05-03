// Diff fixture v2 (clean): adds GoroutineCount but does not
// remove anything. PASS the additive-only contract.
package api

type Server struct{}

type Client struct{}

func NewServer() *Server {
	return &Server{}
}

func NewClient() *Client {
	return &Client{}
}

func GoroutineCount() int {
	return 0
}

var Version = "1.0"
