import os


def get_env_variable(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing environment variable '{name}'")
    return value
