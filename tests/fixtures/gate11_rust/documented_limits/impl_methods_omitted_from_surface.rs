pub struct Counter { pub count: i32 }
impl Counter {
    pub fn increment(&mut self) { self.count += 1; }
    pub fn value(&self) -> i32 { self.count }
}
