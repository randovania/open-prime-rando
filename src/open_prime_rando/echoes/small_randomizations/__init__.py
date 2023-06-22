from random import Random

from open_prime_rando.echoes.small_randomizations.echo_locks import randomize_echo_locks
from open_prime_rando.echoes.small_randomizations.minigyro_chamber import randomize_minigyro_chamber
from open_prime_rando.echoes.small_randomizations.rubiks import randomize_rubiks_puzzles
from open_prime_rando.patcher_editor import PatcherEditor


def apply_small_randomizations(editor: PatcherEditor, configuration: dict):
    rng = Random(configuration["seed"])

    if configuration["echo_locks"]:
        randomize_echo_locks(editor, rng)

    if configuration["minigyro_chamber"]:
        randomize_minigyro_chamber(editor, rng)

    if configuration["rubiks"]:
        randomize_rubiks_puzzles(editor, rng)
