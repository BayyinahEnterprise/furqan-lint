// Documented limit (v0.8.1) v2: Logger type and its Foo method
// removed entirely. Counter and its Foo method remain.
//
// v0.8.1 expected behavior: diff reports `'Logger'` removed
// (correct: type name disappears from the set), but does NOT
// report `'Foo'` removed (the false-negative: bare `Foo` is
// still in the set because Counter.Foo persists).
//
// v0.8.2 will emit qualified method names; the diff will then
// also surface 'Logger.Foo' as removed.

package api

type Counter struct{}

func (c *Counter) Foo() {}
