// Idiom: caller declares (Config, error) with named returns and
// propagates the upstream Result via the named-return mechanism.
// Verdict: PASS (D11 silent: union honestly propagated).
// Pinning: tests/test_go_correctness.py::test_go_d11_clean_when_named_returns.

package config

type Config struct {
	Name string
}

func loadConfig(path string) (*Config, error) {
	return &Config{Name: path}, nil
}

func StartServer(path string) (cfg *Config, err error) {
	cfg, err = loadConfig(path)
	return
}
