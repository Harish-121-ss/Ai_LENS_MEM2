def normalize_string(value: str) -> str:
    if value is None:
        return ""
    return value.strip().casefold()
