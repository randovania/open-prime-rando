import logging
from enum import Enum

from retro_data_structures.properties.echoes.archetypes.Transform import Transform
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects import Actor, Counter, Platform

from open_prime_rando.echoes.asset_ids import agon_wastes, great_temple, torvus_bog
from open_prime_rando.echoes.asset_ids.world import (
    AGON_WASTES_MLVL,
    GREAT_TEMPLE_MLVL,
    TORVUS_BOG_MLVL,
)
from open_prime_rando.patcher_editor import PatcherEditor

LOG = logging.getLogger("echoes_patcher")


class EchoesVersion(float, Enum):
    NTSC_U = 1.028
    PAL = 1.035
    NTSC_J = 1.036
    NEW_PLAY_CONTROL = 3.561
    TRILOGY_NTSC = 3.593
    TRILOGY_PAL = 3.629


def patch_version_differences(editor: PatcherEditor, version: EchoesVersion):
    """
    Patches version differences that affect gameplay or logic. Usually restores NTSC-U functionality.
    Note: only NTSC-U and PAL are officially supported. Version differences introduced in later versions
    do not strictly need to be patched.
    """
    transport_a_access(editor, version)
    path_of_eyes(editor, version)
    venomous_pond(editor, version)
    portal_terminal(editor, version)


def transport_a_access(editor: PatcherEditor, version: EchoesVersion):
    """
    Ensures the vulnerability for the blocker is correct.
    """
    if version == EchoesVersion.NTSC_U:
        return

    area = editor.get_area(GREAT_TEMPLE_MLVL, great_temple.TRANSPORT_A_ACCESS_MREA)

    with area.get_instance("blocker").edit_properties(Platform) as blocker:
        blocker.vulnerability.boost_ball.damage_multiplier = 100.0
        blocker.vulnerability.screw_attack.damage_multiplier = 100.0
        blocker.vulnerability.super_missle.damage_multiplier = 100.0


def path_of_eyes(editor: PatcherEditor, version: EchoesVersion):
    """
    Edits area collision to restore a gap you can boost through.
    """
    if version == EchoesVersion.NTSC_U:
        return

    LOG.warning(
        "Path of Eyes version differences have not been patched! " "Area collision edits are not yet implemented."
    )


def venomous_pond(editor: PatcherEditor, version: EchoesVersion):
    """
    Edits the collision of an Ing Bearerpod to restore a standable to reach the item.
    """
    if version == EchoesVersion.NTSC_U:
        return

    area = editor.get_area(TORVUS_BOG_MLVL, torvus_bog.VENOMOUS_POND_MREA)

    with area.get_instance(0x10003E).edit_properties(Actor) as piggyplant:
        piggyplant.editor_properties.transform = Transform(
            position=Vector(17.589201, -148.844849, 37.929966),
            scale=Vector(1.5, 1.5, 1.5),
            rotation=piggyplant.editor_properties.transform.rotation,
        )
        piggyplant.collision_model = 0x8E4170D5


def portal_terminal(editor: PatcherEditor, version: EchoesVersion):
    """
    In GC NTSC-J version a counter was added to check for each cork to be broken
    """
    if version < EchoesVersion.NTSC_J:
        return

    area = editor.get_area(AGON_WASTES_MLVL, agon_wastes.PORTAL_TERMINAL_MREA)

    counter = area.get_instance(0x12044E)

    # Remove counter increment on the 2 first corks to destroy
    relay_ids = [0x12033A, 0x120343]  # 0x120307 is the last cork to destroy
    for relay_id in relay_ids:
        relay = area.get_instance(relay_id)
        relay.remove_connections_from(counter)

    # Set the destroyed cork counter to expect only one cork to be destroyed
    with counter.edit_properties(Counter) as props:
        props.editor_properties.unknown = 1
        props.max_count = 1
