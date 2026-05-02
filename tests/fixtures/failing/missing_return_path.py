def process(data: dict) -> str:
    if "name" in data:
        return data["name"]
    # Missing else: falls through with no return
