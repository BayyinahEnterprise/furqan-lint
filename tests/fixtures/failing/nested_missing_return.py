def compute(x: int, y: int) -> float:
    if x > 0:
        if y > 0:
            return x / y
        else:
            return 0.0
    # x <= 0 path has no return
