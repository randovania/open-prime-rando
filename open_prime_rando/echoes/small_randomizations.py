from enum import Enum
import random

from retro_data_structures.formats.strg import Strg
from retro_data_structures.properties.echoes.objects.Sound import Sound
from retro_data_structures.properties.echoes.objects.Switch import Switch
from retro_data_structures.properties.echoes.objects.Actor import Actor

from open_prime_rando.patcher_editor import PatcherEditor


ECHO_LOCK_MREAS = [0x64E640D6, 0xA4D81547, 0x73342A54]
ECHO_LOCK_STATES = ["ZERO", "IS00", "IS01", "IS02"]
ECHO_LOCK_SOUNDS = [1005, 1006, 1007]

def randomize_echo_locks(editor: PatcherEditor):
    for asset_id in ECHO_LOCK_MREAS:
        mrea = editor.get_mrea(asset_id)
        solution = [random.randint(0, 2) for _ in range(4)]

        counter = mrea.get_instance_by_name("Lock Solution Counter")
        correct_key_relays = [mrea.get_instance_by_name(f"[IN] Set Key {i} As Correct Choice") for i in range(3)]
        lock_tone_players = [mrea.get_instance_by_name(f"(Gate) Lock {i} Tone") for i in range(4)]
        key_switches = [mrea.get_instance_by_name(f"(Key {i}) Check Echo Key") for i in range(3)]

        for relay in correct_key_relays:
            counter.remove_connections(relay)
        
        for i, key in enumerate(solution):
            counter.add_connection(ECHO_LOCK_STATES[i], "ZERO", correct_key_relays[key])
            
            tone: Sound = lock_tone_players[i].get_properties()
            tone.sound = ECHO_LOCK_SOUNDS[key]
            lock_tone_players[i].set_properties(tone)
        
        for i, switch in enumerate(key_switches):
            props: Switch = switch.get_properties()
            props.is_open = i == solution[0]
            switch.set_properties(props)


GYRO_COLORS = ["AMBER", "COBALT", "CRIMSON", "EMERALD"]
GYRO_STATES = ["IS00", "IS01", "IS02", "IS03"]

def randomize_minigyro_chamber(editor: PatcherEditor):
    mrea = editor.get_mrea(0x96F4CA1E)
    solution = list(range(4))
    random.shuffle(solution)

    counter = mrea.get_instance_by_name("Stage gate activator")
    stage_gates = [mrea.get_instance_by_name(f"Stage gate {i+1}") for i in range(4)]

    for i, gate in enumerate(stage_gates):
        counter.remove_connections(gate)
        for j, gyro in enumerate(solution):
            message = "ACTV" if i == gyro else "DCTV"
            counter.add_connection(GYRO_STATES[j], message, gate)
    
    scan = editor.get_file(0xFBFF349D, Strg)
    solution_text = '\n'.join((GYRO_COLORS[i] for i in solution))
    strings = scan.strings
    strings[1] = f"Safety lockdown code is as follows:\n\n\n{solution_text}"
    scan.strings = strings


RUBIKS_CUBES = {
    "Puzzle 1": [
        0x240013, 0x2401A4, 0x240145,
        0x24010A, 0x24000E, 0x240192,
        0x240139, 0x24013A, 0x240148,
    ],
    "Puzzle 2": [
        0x2402BA, 0x2402AD, 0x2402A6,
        0x2401C6, 0x2401BE, 0x2401C0,
        0x24028B, 0x2401C3, 0x240290,
    ]
}

class RubiksColor(Enum):
    RED = "IS00"
    GREEN = "IS01"
    BLUE = "IS02"

    @property
    def cmdl(self) -> int:
        if self == RubiksColor.RED:
            return 0xF21AB8BF
        if self == RubiksColor.GREEN:
            return 0x5F2ADFC3
        if self == RubiksColor.BLUE:
            return 0x8F25F715

def randomize_rubiks_puzzles(editor: PatcherEditor):
    mrea = editor.get_mrea(0x73342A54)
    for puzzle_name, cubes in RUBIKS_CUBES.items():
        solution = [
            RubiksColor.RED, RubiksColor.RED, RubiksColor.RED,
            RubiksColor.GREEN, RubiksColor.GREEN, RubiksColor.GREEN,
            RubiksColor.BLUE, RubiksColor.BLUE, RubiksColor.BLUE,
        ]
        random.shuffle(solution)

        puzzle = mrea.get_instance_by_name(puzzle_name)
        for color, cube_id in zip(solution, cubes):
            cube = mrea.get_instance(cube_id)

            puzzle.remove_connections(cube)
            puzzle.add_connection(color.value, "ATCH", cube)

            props: Actor = cube.get_properties()
            props.model = color.cmdl
            cube.set_properties(props)
