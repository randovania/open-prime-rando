from __future__ import annotations

import functools
from enum import Enum
from typing import TYPE_CHECKING

from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.formats.strg import Strg

from open_prime_rando.echoes.asset_ids.sanctuary_fortress import MINIGYRO_CHAMBER_MREA
from open_prime_rando.echoes.asset_ids.world import SANCTUARY_FORTRESS_MLVL

if TYPE_CHECKING:
    import random

    from retro_data_structures.formats.mlvl import Mlvl
    from retro_data_structures.formats.mrea import Area

    from open_prime_rando.area_patcher import AreaPatcher
    from open_prime_rando.patcher_editor import PatcherEditor


class GyroColor(Enum):
    AMBER = 0
    COBALT = 1
    CRIMSON = 2
    EMERALD = 3

    @property
    def color(self) -> str:
        colors = {
            GyroColor.AMBER: "#A45600",
            GyroColor.COBALT: "#56789D",
            GyroColor.CRIMSON: "#FF6562",
            GyroColor.EMERALD: "#4E9761",
        }
        return colors[self]

    @property
    def bomb_slot_number(self) -> int:
        """The order of this color's bomb slot, numbered right to left."""
        numbers = {
            GyroColor.EMERALD: 4,
            GyroColor.AMBER: 3,
            GyroColor.CRIMSON: 2,
            GyroColor.COBALT: 1,
        }
        return numbers[self]

    @property
    def gyro_stop_name(self) -> str:
        return f"[IN/OUT] Stop gyroscope {self.bomb_slot_number}"

    @property
    def display_id(self) -> str:
        """Identifies the color with a letter, from left to right."""
        ids = {
            GyroColor.EMERALD: "A",
            GyroColor.AMBER: "B",
            GyroColor.CRIMSON: "C",
            GyroColor.COBALT: "D",
        }
        return ids[self]

    @property
    def text(self) -> str:
        return f"&push;&main-color={self.color};({self.display_id}) {self.name}&pop;"


GYRO_STATES = [
    State.InternalState00,
    State.InternalState01,
    State.InternalState02,
    State.InternalState03,
]


def create_random_solution(rng: random.Random) -> list[GyroColor]:
    """
    Creates a random solution to the Minigyro Chamber puzzle.
    """
    solution = [GyroColor.AMBER, GyroColor.COBALT, GyroColor.CRIMSON, GyroColor.EMERALD]
    rng.shuffle(solution)
    return solution


def patch_minigyro_chamber_puzzle(editor: PatcherEditor, mlvl: Mlvl, area: Area, solution: list[GyroColor]) -> None:
    """
    Modifies the puzzle in Minigyro Chamber to use the given solution.
    """
    counter = area.get_instance("Stage gate activator")
    stage_gates = [area.get_instance(f"Stage gate {i + 1}") for i in range(4)]

    for i, gate in enumerate(stage_gates):
        counter.remove_all_connections_to(gate)
        for j, gyro in enumerate(solution):
            message = Message.Activate if i == gyro.value else Message.Deactivate
            counter.add_connection(GYRO_STATES[j], message, gate)

    # play jingle on the final gyro
    jingle = area.get_instance("StreamedAudio - Event Jingle")

    area.get_instance(GyroColor.EMERALD.gyro_stop_name).remove_all_connections_to(jingle)
    area.get_instance(solution[-1].gyro_stop_name).add_connection(State.Zero, Message.Play, jingle)

    scan = editor.get_file(0xFBFF349D, Strg)
    solution_text = "\n".join(gyro.text for gyro in solution)
    scan.set_single_string(1, f"Safety lockdown code is as follows:\n\n\n{solution_text}")


def register_patch_random_solution(area_patcher: AreaPatcher, rng: random.Random) -> None:
    """
    Creates a random solution and register the Minigyro Chamber to be changed via AreaPatcher.
    """
    area_patcher.add_raw_function(
        SANCTUARY_FORTRESS_MLVL,
        MINIGYRO_CHAMBER_MREA,
        functools.partial(
            patch_minigyro_chamber_puzzle,
            solution=create_random_solution(rng),
        ),
    )
