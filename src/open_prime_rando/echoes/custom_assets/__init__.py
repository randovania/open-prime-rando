import functools
from pathlib import Path


@functools.cache
def custom_asset_path() -> Path:
    return Path(__file__).parent
