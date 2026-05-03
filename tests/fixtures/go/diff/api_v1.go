// Diff fixture v1: baseline public surface.
package api

type Server struct{}

type Client struct{}

func NewServer() *Server {
	return &Server{}
}

func NewClient() *Client {
	return &Client{}
}

var Version = "1.0"
