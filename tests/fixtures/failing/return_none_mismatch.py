def get_name(data: dict) -> str:
    if "name" in data:
        return data["name"]
    return None
