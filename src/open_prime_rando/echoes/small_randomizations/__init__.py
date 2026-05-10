from random import Random

from open_prime_rando.area_patcher import AreaPatcher
from open_prime_rando.echoes.small_randomizations import echo_locks, minigyro_chamber
from open_prime_rando.echoes.small_randomizations.rubiks import randomize_rubiks_puzzles


def apply_small_randomizations(area_patcher: AreaPatcher, configuration: dict) -> None:
    rng = Random(configuration["seed"])

    if configuration["echo_locks"]:
        echo_locks.register_patch_random_solution(area_patcher, rng)

    if configuration["minigyro_chamber"]:
        minigyro_chamber.register_patch_random_solution(area_patcher, rng)

    if configuration["rubiks"]:
        randomize_rubiks_puzzles(area_patcher.editor, rng)
