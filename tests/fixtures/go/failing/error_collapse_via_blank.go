// Idiom: caller declares a non-error return type and calls a
// (T, error)-returning helper, discarding the error via _ at
// assignment.
// Verdict: MARAD status_coverage on StartServer (Case S1: caller
// silently narrows the union the producer declared).
// Pinning: tests/test_go_correctness.py::test_go_d11_fires_on_error_collapse_via_blank.

package config

type Config struct {
	Name string
}

func loadConfig(path string) (*Config, error) {
	return &Config{Name: path}, nil
}

func StartServer(path string) *Config {
	// Caller declares -> *Config but calls a (T, error)-returning
	// helper and silently discards the error. D11 fires.
	cfg, _ := loadConfig(path)
	return cfg
}
