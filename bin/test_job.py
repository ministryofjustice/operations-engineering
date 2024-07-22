def convert_str_to_bool(the_string: str | bool) -> bool:
    if the_string in {"True", "true", True}:
        return True
    return False


def get_username(user: dict[str, any]) -> str:
    return user["username "]
