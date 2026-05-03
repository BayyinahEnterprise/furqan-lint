// Diff fixture v2 (clean): adds goroutine_count but removes
// nothing. PASS the additive-only contract.

pub struct Server;

pub struct Client;

pub fn new_server() -> Server {
    Server
}

pub fn new_client() -> Client {
    Client
}

pub fn task_count() -> usize {
    0
}

pub const VERSION: &str = "1.0";
