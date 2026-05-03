// Idiom: function returning Box<dyn Trait>. Phase 1 treats trait
// objects as opaque TypePath; trait-object polymorphism is out of
// scope per ADR-001 §2 deferred-features list.
// Verdict: PASS (silent false negative possible if the body is
// underspecified; the fixture body is well-formed so this is not
// a marad-firing case in v0.7.0; the limit is "we do not analyze
// trait-object payloads").
// CST nodes: function_item, generic_type (Box), trait_object_type,
// dynamic_type.

trait Shape {
    fn area(&self) -> f64;
}

struct Circle {
    radius: f64,
}

impl Shape for Circle {
    fn area(&self) -> f64 {
        3.14159 * self.radius * self.radius
    }
}

fn shape_factory() -> Box<dyn Shape> {
    Box::new(Circle { radius: 1.0 })
}
