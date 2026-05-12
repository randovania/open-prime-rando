from __future__ import annotations

from random import Random
from typing import TYPE_CHECKING

from open_prime_rando.echoes.small_randomizations import echo_locks, minigyro_chamber, rubiks

if TYPE_CHECKING:
    from open_prime_rando.area_patcher import AreaPatcher


def register_small_randomizations(area_patcher: AreaPatcher, random_seed: int) -> None:
    """
    Register all the small changes.
    """
    echo_locks.register_patch_random_solution(area_patcher, Random(random_seed))
    minigyro_chamber.register_patch_random_solution(area_patcher, Random(random_seed))
    rubiks.register_patch_random_solution(area_patcher, Random(random_seed))
