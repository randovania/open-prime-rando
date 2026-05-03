from __future__ import annotations

import logging
from enum import Enum
from typing import TYPE_CHECKING

from retro_data_structures.properties.echoes.archetypes.Transform import Transform
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects import Actor, Counter, Platform

from open_prime_rando.area_patcher import AreaPatcher, decorate_patcher
from open_prime_rando.echoes.asset_ids import agon_wastes, great_temple, temple_grounds, torvus_bog
from open_prime_rando.echoes.asset_ids.world import (
    AGON_WASTES_MLVL,
    GREAT_TEMPLE_MLVL,
    TEMPLE_GROUNDS_MLVL,
    TORVUS_BOG_MLVL,
)

if TYPE_CHECKING:
    from retro_data_structures.formats.mlvl import Mlvl
    from retro_data_structures.formats.mrea import Area

    from open_prime_rando.patcher_editor import PatcherEditor

LOG = logging.getLogger("echoes_patcher")


class EchoesVersion(float, Enum):
    NTSC_U = 1.028
    PAL = 1.035
    NTSC_J = 1.036
    NEW_PLAY_CONTROL = 3.561
    TRILOGY_NTSC = 3.593
    TRILOGY_PAL = 3.629


def register_all(area_patcher: AreaPatcher, version: EchoesVersion):
    """
    Patches version differences that affect gameplay or logic. Usually restores NTSC-U functionality.
    Note: only NTSC-U and PAL are officially supported. Version differences introduced in later versions
    do not strictly need to be patched.
    """

    if version >= EchoesVersion.PAL:
        area_patcher.add_function(transport_a_access)
        area_patcher.add_function(path_of_eyes)
        area_patcher.add_function(venomous_pond)

    if version >= EchoesVersion.NTSC_J:
        area_patcher.add_function(portal_terminal)


@decorate_patcher(GREAT_TEMPLE_MLVL, great_temple.TRANSPORT_A_ACCESS_MREA)
def transport_a_access(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Ensures the vulnerability for the blocker is correct.
    """
    with area.get_instance("blocker").edit_properties(Platform) as blocker:
        blocker.vulnerability.boost_ball.damage_multiplier = 100.0
        blocker.vulnerability.screw_attack.damage_multiplier = 100.0
        blocker.vulnerability.super_missle.damage_multiplier = 100.0


@decorate_patcher(TEMPLE_GROUNDS_MLVL, temple_grounds.PATH_OF_EYES_MREA)
def path_of_eyes(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Edits area collision to restore a gap you can boost through.
    """
    LOG.warning("Path of Eyes version differences have not been patched! Area collision edits are not yet implemented.")


@decorate_patcher(TORVUS_BOG_MLVL, torvus_bog.VENOMOUS_POND_MREA)
def venomous_pond(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Edits the collision of an Ing Bearerpod to restore a standable to reach the item.
    """
    with area.get_instance(0x10003E).edit_properties(Actor) as piggyplant:
        piggyplant.editor_properties.transform = Transform(
            position=Vector(17.589201, -148.844849, 37.929966),
            scale=Vector(1.5, 1.5, 1.5),
            rotation=piggyplant.editor_properties.transform.rotation,
        )
        piggyplant.collision_model = 0x8E4170D5


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.PORTAL_TERMINAL_MREA)
def portal_terminal(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    In GC NTSC-J version a counter was added to check for each cork to be broken
    """
    counter = area.get_instance(0x12044E)

    # Remove counter increment on the 2 first corks to destroy
    relay_ids = [0x12033A, 0x120343]  # 0x120307 is the last cork to destroy
    for relay_id in relay_ids:
        relay = area.get_instance(relay_id)
        relay.remove_all_connections_to(counter)

    # Set the destroyed cork counter to expect only one cork to be destroyed
    with counter.edit_properties(Counter) as props:
        props.editor_properties.unknown = 1
        props.max_count = 1
