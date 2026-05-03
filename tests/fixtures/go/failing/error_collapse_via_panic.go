// Idiom: caller declares non-error return type and calls a
// (T, error)-returning helper. The error is checked but the
// caller's signature still lies (returns Config, not Result).
// This pattern is more idiomatic Go than the blank-discard form
// but structurally equally dishonest.
// Verdict: MARAD status_coverage on StartServer (Case S1).
// Pinning: tests/test_go_correctness.py::test_go_d11_fires_on_error_collapse_via_panic.

package config

type Config struct {
	Name string
}

func loadConfig(path string) (*Config, error) {
	return &Config{Name: path}, nil
}

func StartServer(path string) *Config {
	cfg, err := loadConfig(path)
	if err != nil {
		panic(err)
	}
	return cfg
}
