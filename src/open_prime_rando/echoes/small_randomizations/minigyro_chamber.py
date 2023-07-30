import random
from enum import Enum

from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.formats.strg import Strg

from open_prime_rando.echoes.asset_ids.sanctuary_fortress import MINIGYRO_CHAMBER_MREA
from open_prime_rando.echoes.asset_ids.world import SANCTUARY_FORTRESS_MLVL
from open_prime_rando.patcher_editor import PatcherEditor


class GyroColor(Enum):
    AMBER = 0
    COBALT = 1
    CRIMSON = 2
    EMERALD = 3

    @property
    def color(self) -> str:
        if self == GyroColor.AMBER:
            return "#A45600"
        if self == GyroColor.COBALT:
            return "#56789D"
        if self == GyroColor.CRIMSON:
            return "#FF6562"
        if self == GyroColor.EMERALD:
            return "#4E9761"

    @property
    def text(self) -> str:
        return f"&push;&main-color={self.color};{self.name}&pop;"

GYRO_STATES = [
    State.InternalState00,
    State.InternalState01,
    State.InternalState02,
    State.InternalState03,
]


def randomize_minigyro_chamber(editor: PatcherEditor, rng: random.Random):
    area = editor.get_area(SANCTUARY_FORTRESS_MLVL, MINIGYRO_CHAMBER_MREA)
    solution = [GyroColor.AMBER, GyroColor.COBALT, GyroColor.CRIMSON, GyroColor.EMERALD]
    rng.shuffle(solution)

    counter = area.get_instance("Stage gate activator")
    stage_gates = [area.get_instance(f"Stage gate {i+1}") for i in range(4)]

    for i, gate in enumerate(stage_gates):
        counter.remove_connections_from(gate)
        for j, gyro in enumerate(solution):
            message = Message.Activate if i == gyro.value else Message.Deactivate
            counter.add_connection(GYRO_STATES[j], message, gate)

    # play jingle on the final gyro
    stop_gyros = [area.get_instance(f"[IN/OUT] Stop gyroscope {i+1}") for i in range(4)]
    jingle = area.get_instance("StreamedAudio - Event Jingle")

    stop_gyros[3].remove_connections_from(jingle)
    stop_gyros[solution[3].value].add_connection(State.Zero, Message.Play, jingle)

    scan = editor.get_file(0xFBFF349D, Strg)
    solution_text = '\n'.join(gyro.text for gyro in solution)
    scan.set_string(1, f"Safety lockdown code is as follows:\n\n\n{solution_text}")

    area.update_all_dependencies()
