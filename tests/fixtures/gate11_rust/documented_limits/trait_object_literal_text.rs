pub trait Shape { fn area(&self) -> f64; }
pub fn make_shape() -> Box<dyn Shape> { todo!() }
