from __future__ import annotations

from typing import TYPE_CHECKING

from open_prime_rando.echoes.small_randomizations import echo_locks, minigyro_chamber, rubiks

if TYPE_CHECKING:
    from random import Random

    from open_prime_rando.area_patcher import AreaPatcher


def register_small_randomizations(area_patcher: AreaPatcher, rng: Random) -> None:
    """
    Register all the small changes.
    """
    echo_locks.register_patch_random_solution(area_patcher, rng)
    minigyro_chamber.register_patch_random_solution(area_patcher, rng)
    rubiks.register_patch_random_solution(area_patcher, rng)
