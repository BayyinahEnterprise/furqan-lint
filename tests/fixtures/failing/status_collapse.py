from typing import Optional


def validate(input_data: str) -> Optional[dict]:
    if not input_data:
        return None
    return {"value": input_data}


def run(input_data: str) -> dict:
    result = validate(input_data)
    return result
