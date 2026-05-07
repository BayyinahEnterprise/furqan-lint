pub trait Trait {}
pub fn i<'a>(x: Box<dyn Trait + 'a>) -> () { todo!() }
