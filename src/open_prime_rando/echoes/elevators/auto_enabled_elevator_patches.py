from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.objects.Timer import Timer

from open_prime_rando.echoes.asset_ids import (
    agon_wastes,
    great_temple,
    sanctuary_fortress,
    temple_grounds,
    torvus_bog,
    world,
)

if TYPE_CHECKING:
    from retro_data_structures.formats.mlvl import Mlvl
    from retro_data_structures.formats.mrea import Area

    from open_prime_rando.area_patcher import AreaPatcher
    from open_prime_rando.patcher_editor import PatcherEditor

ELEVATOR_MEMORY_RELAY_PER_MREA = {
    world.GREAT_TEMPLE_MLVL: {
        great_temple.TEMPLE_TRANSPORT_A_MREA: 0x00000107,
        great_temple.TEMPLE_TRANSPORT_B_MREA: 0x0008002F,
        great_temple.TEMPLE_TRANSPORT_C_MREA: 0x00060046,
    },
    world.TEMPLE_GROUNDS_MLVL: {
        temple_grounds.TRANSPORT_TO_AGON_WASTES_MREA: 0x00180040,
        temple_grounds.TRANSPORT_TO_SANCTUARY_FORTRESS_MREA: 0x00330058,
        temple_grounds.TRANSPORT_TO_TORVUS_BOG_MREA: 0x001E0061,
    },
    world.AGON_WASTES_MLVL: {
        agon_wastes.TRANSPORT_TO_SANCTUARY_FORTRESS_MREA: 0x002D0064,
        agon_wastes.TRANSPORT_TO_TEMPLE_GROUNDS_MREA: 0x0000003F,
        agon_wastes.TRANSPORT_TO_TORVUS_BOG_MREA: 0x0013004D,
    },
    world.TORVUS_BOG_MLVL: {
        torvus_bog.TRANSPORT_TO_AGON_WASTES_MREA: 0x00210038,
        torvus_bog.TRANSPORT_TO_SANCTUARY_FORTRESS_MREA: 0x0045004B,
        torvus_bog.TRANSPORT_TO_TEMPLE_GROUNDS_MREA: 0x0000002E,
    },
    world.SANCTUARY_FORTRESS_MLVL: {
        sanctuary_fortress.TRANSPORT_TO_AGON_WASTES_MREA: 0x00130088,
        sanctuary_fortress.TRANSPORT_TO_TEMPLE_GROUNDS_MREA: 0x00000035,
        sanctuary_fortress.TRANSPORT_TO_TORVUS_BOG_MREA: 0x00190036,
    },
}


def patch_elevator(
    editor: PatcherEditor,
    mlvl: Mlvl,
    area: Area,
    memory_relay_id: int,
) -> None:
    """Makes it that the elevator is automatically started, by activating the given memory relay."""
    relay = area.get_instance(memory_relay_id)

    timer = area.get_layer("Default").add_instance_with(
        Timer(
            editor_properties=EditorProperties(name="Timer - Auto enable elevator", active=False),
            time=0.001,
            auto_start=True,
        )
    )
    timer.add_connection(State.Zero, Message.Activate, relay)


def register(area_patcher: AreaPatcher) -> None:
    """
    Register for every area that has a cross-region elevator to be automatically enabled.
    """
    for mlvl_id, areas in ELEVATOR_MEMORY_RELAY_PER_MREA.items():
        for mrea_id, memory_relay_id in areas.items():
            area_patcher.add_raw_function(
                mlvl_id,
                mrea_id,
                functools.partial(patch_elevator, memory_relay_id=memory_relay_id),
            )
