// Documented limit (v0.8.1): Go method-name conflation in
// public_names. The goast binary collects method names without
// receiver-type qualification, so `Counter.Foo` and `Logger.Foo`
// both appear as bare `Foo` in public_names. After
// frozenset() collapse in extract_public_names, the diff loses
// the ability to distinguish a Counter.Foo removal from a
// Logger.Foo removal: if either receiver-type still has a
// `Foo` method, the diff sees no removal of `Foo`.
//
// Pre-existing in goast since v0.8.0; documented in v0.8.1;
// fixed in v0.8.2 by emitting qualified method names from goast
// (e.g. 'Counter.Foo' and 'Logger.Foo' as distinct entries).
//
// This fixture is the v1 baseline. v2 removes Logger and its
// Foo method entirely; the diff should ideally report both
// Logger removed AND Logger.Foo removed; v0.8.1 reports only
// Logger.

package api

type Counter struct{}

type Logger struct{}

func (c *Counter) Foo() {}

func (l *Logger) Foo() {}
