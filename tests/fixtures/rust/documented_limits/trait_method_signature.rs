// Idiom: trait method DECLARATION (signature only, no body).
// Verdict: PASS (skipped by design per prompt §3.4). D24/D11 do
// not apply to interface declarations; only to implementations.
// The translator's function-discovery walker explicitly skips
// function_signature_item nodes.
// CST nodes: trait_item, function_signature_item (NOT
// function_item).

trait Repository {
    fn save(&self, id: u64) -> Result<(), std::io::Error>;
    fn load(&self, id: u64) -> Result<String, std::io::Error>;
}
