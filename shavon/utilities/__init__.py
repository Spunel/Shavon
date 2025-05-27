import random
import string


def random_alphanumeric(length: int = 4, choices: str|None = None) -> str:
    if choices is None:
        choices = f'{string.ascii_letters}{string.digits}'

    return ''.join(random.choices(choices[:], k=length))

