import random
from dataclasses import dataclass
from pathlib import Path

from retro_data_structures.base_resource import RawResource
from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.formats.cmdl import Cmdl
from retro_data_structures.properties.echoes.archetypes.Transform import Transform
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects.Actor import Actor
from retro_data_structures.properties.echoes.objects.DamageableTrigger import DamageableTrigger
from retro_data_structures.properties.echoes.objects.Waypoint import Waypoint

from open_prime_rando.echoes.asset_ids.sanctuary_fortress import MAIN_GYRO_CHAMBER_MREA
from open_prime_rando.echoes.asset_ids.world import SANCTUARY_FORTRESS_MLVL
from open_prime_rando.patcher_editor import PatcherEditor

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
        txtr_id = editor.add_file(color.txtr_name, color.txtr)

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

    patch_upstairs_puzzle_transform(editor)

    area.update_all_dependencies()


def patch_upstairs_puzzle_transform(editor: PatcherEditor):
    """
    The vanilla transform for these angles them with the glass, making the lock-on points
    awfully inconsistent. This patches them to be straight up and down, and adjusts the
    in/out lasers to match properly.
    """
    area = editor.get_area(SANCTUARY_FORTRESS_MLVL, MAIN_GYRO_CHAMBER_MREA)

    cubes = tuple(RUBIKS_CUBES["Puzzle 2"])
    # inner lasers
    lasers = (0x2402A9, 0x24028D, 0x240293, 0x2402A7, 0x2402B4, 0x2402B0)
    # buttons
    buttons = (0x2401C9, 0x2401C7, 0x2402B9, 0x2402AE)
    # damageable triggers
    damageable = (0x240294, 0x2402B2, 0x2402A8, 0x2401BC)

    Y_POS = 249.3522

    for actor_id in cubes + lasers:
        with area.get_instance(actor_id).edit_properties(Actor) as actor:
            actor.editor_properties.transform.rotation.x = 0.0
            actor.editor_properties.transform.position.y = Y_POS
            actor.is_solid = True

    for button_id in buttons:
        with area.get_instance(button_id).edit_properties(Actor) as actor:
            actor.editor_properties.transform.rotation.x = 0.0
            actor.editor_properties.transform.position.y = Y_POS

    for actor_id in damageable:
        with area.get_instance(actor_id).edit_properties(DamageableTrigger) as actor:
            actor.editor_properties.transform.rotation.x = 0.0
            actor.editor_properties.transform.position.y = Y_POS

    # axis ref. this needs to be updated so the puzzle rotates properly
    with area.get_instance(0x2402A5).edit_properties(Waypoint) as axis_ref:
        axis_ref.editor_properties.transform.rotation.x = 0.0

    big_lasers = {
        # red in
        0x2401C1: Transform(
            position=Vector(60.9426, 250.63, 12.0627),
            rotation=Vector(0.0, 0.1, 164.48),
            scale=Vector(0.9, 1.0, 1.0)
        ),
        # red out
        0x24028A: Transform(
            position=Vector(76.1287, 250.63, 12.0627),
            rotation=Vector(0.0, -0.7, -164.08),
            scale=Vector(0.9, 1.0, 1.0)
        ),
        # green in
        0x2401C2: Transform(
            position=Vector(60.342598, 250.13, 12.3027),
            rotation=Vector(0.0, 0.5, -187.5),
            scale=Vector(1.0, 1.0, 1.0)
        ),
        # green out
        0x2402BB: Transform(
            position=Vector(76.62867, 250.11, 12.2827),
            rotation=Vector(0.0, -0.5, 188.0),
            scale=Vector(0.9, 1.0, 1.0)
        ),
        # blue in
        0x24028F: Transform(
            position=Vector(60.142597, 249.51, 12.5127),
            rotation=Vector(0.0, 0.5, -180.0),
            scale=Vector(1.0, 1.0, 1.0)
        ),
        # blue out
        0x2402B6: Transform(
            position=Vector(77.1287, 249.51, 12.5127),
            rotation=Vector(0.0, -0.5, -180.0),
            scale=Vector(1.0, 1.0, 1.0)
        )
    }

    for laser_id, transform in big_lasers.items():
        with area.get_instance(laser_id).edit_properties(Actor) as laser:
            laser.editor_properties.transform = transform
            laser.is_solid = True
