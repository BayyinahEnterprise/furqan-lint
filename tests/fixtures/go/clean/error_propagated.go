// Idiom: caller declares (*Config, error) and propagates the
// upstream Result via direct return.
// Verdict: PASS (D11 silent: union honestly propagated).
// Pinning: tests/test_go_correctness.py::test_go_d11_clean_when_error_propagated.

package config

type Config struct {
	Name string
}

func loadConfig(path string) (*Config, error) {
	return &Config{Name: path}, nil
}

func StartServer(path string) (*Config, error) {
	cfg, err := loadConfig(path)
	return cfg, err
}
