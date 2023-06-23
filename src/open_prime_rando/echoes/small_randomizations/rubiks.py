import random
from dataclasses import dataclass
from pathlib import Path

from open_prime_rando.echoes.asset_ids.sanctuary_fortress import MAIN_GYRO_CHAMBER_MREA
from open_prime_rando.echoes.asset_ids.world import SANCTUARY_FORTRESS_MLVL
from open_prime_rando.patcher_editor import PatcherEditor
from retro_data_structures.base_resource import RawResource
from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.formats.cmdl import Cmdl
from retro_data_structures.properties.echoes.objects.Actor import Actor

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


@dataclass(frozen=True)
class RubiksColor:
    name: str
    state: State
    cmdl: int
    old_txtr: int

    @property
    def txtr_name(self) -> str:
        return f"rubiks_{self.name.lower()}.TXTR"

    @property
    def txtr(self) -> RawResource:
        return RawResource(
            type="TXTR",
            data=Path(__file__).parent.parent.joinpath("custom_assets", "rubiks", self.txtr_name).read_bytes()
        )


COLORS = {
    "RED": RubiksColor(
        name="red",
        state=State.InternalState00,
        cmdl=0xF21AB8BF,
        old_txtr=0x29A5FF4B,
    ),
    "GREEN": RubiksColor(
        name="green",
        state=State.InternalState01,
        cmdl=0x5F2ADFC3,
        old_txtr=0xEE2889A3,
    ),
    "BLUE": RubiksColor(
        name="blue",
        state=State.InternalState02,
        cmdl=0x8F25F715,
        old_txtr=0xFED23B81,
    )
}


def randomize_rubiks_puzzles(editor: PatcherEditor, rng: random.Random):
    area = editor.get_area(SANCTUARY_FORTRESS_MLVL, MAIN_GYRO_CHAMBER_MREA)

    # Add custom textures so colorblind players can distinguish the cubes
    for color in COLORS.values():
        txtr_id = editor.add_file(color.txtr_name, color.txtr, editor.find_paks(MAIN_GYRO_CHAMBER_MREA))

        cmdl = editor.get_file(color.cmdl, Cmdl)
        file_ids = cmdl.raw.material_sets[0].texture_file_ids
        old_txtr = file_ids.index(color.old_txtr)
        file_ids[old_txtr] = txtr_id

    for puzzle_name, cubes in RUBIKS_CUBES.items():
        solution = [
            COLORS["RED"], COLORS["RED"], COLORS["RED"],
            COLORS["GREEN"], COLORS["GREEN"], COLORS["GREEN"],
            COLORS["BLUE"], COLORS["BLUE"], COLORS["BLUE"],
        ]
        rng.shuffle(solution)

        puzzle = area.get_instance(puzzle_name)
        for color, cube_id in zip(solution, cubes):
            cube = area.get_instance(cube_id)

            puzzle.remove_connections_from(cube)
            puzzle.add_connection(color.state, Message.Attach, cube)

            with cube.edit_properties(Actor) as props:
                props.model = color.cmdl

