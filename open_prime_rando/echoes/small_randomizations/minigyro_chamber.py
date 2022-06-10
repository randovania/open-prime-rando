from enum import Enum
import random
from open_prime_rando.echoes.asset_ids.sanctuary_fortress import MINIGYRO_CHAMBER_MREA
from open_prime_rando.patcher_editor import PatcherEditor

from retro_data_structures.formats.strg import Strg


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

GYRO_STATES = ["IS00", "IS01", "IS02", "IS03"]


def randomize_minigyro_chamber(editor: PatcherEditor, rng: random.Random):
    mrea = editor.get_mrea(MINIGYRO_CHAMBER_MREA)
    solution = [GyroColor.AMBER, GyroColor.COBALT, GyroColor.CRIMSON, GyroColor.EMERALD]
    rng.shuffle(solution)

    counter = mrea.get_instance_by_name("Stage gate activator")
    stage_gates = [mrea.get_instance_by_name(f"Stage gate {i+1}") for i in range(4)]

    for i, gate in enumerate(stage_gates):
        counter.remove_connections(gate)
        for j, gyro in enumerate(solution):
            message = "ACTV" if i == gyro.value else "DCTV"
            counter.add_connection(GYRO_STATES[j], message, gate)
    
    # play jingle on the final gyro
    stop_gyros = [mrea.get_instance_by_name(f"[IN/OUT] Stop gyroscope {i+1}") for i in range(4)]
    jingle = mrea.get_instance_by_name(f"StreamedAudio - Event Jingle")

    stop_gyros[3].remove_connections(jingle)
    stop_gyros[solution[3].value].add_connection("ZERO", "PLAY", jingle)
    
    # print([f"{mrea.get_instance(c.target).name} - {c.state}: {c.message}" for c in counter.connections])
    
    scan = editor.get_file(0xFBFF349D, Strg)
    solution_text = '\n'.join((gyro.text for gyro in solution))
    scan.set_string(1, f"Safety lockdown code is as follows:\n\n\n{solution_text}")
