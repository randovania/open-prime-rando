from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.objects.Timer import Timer

import open_prime_rando.echoes.asset_ids.agon_wastes as agon_wastes
import open_prime_rando.echoes.asset_ids.great_temple as great_temple
import open_prime_rando.echoes.asset_ids.sanctuary_fortress as sanctuary_fortress
import open_prime_rando.echoes.asset_ids.temple_grounds as temple_grounds
import open_prime_rando.echoes.asset_ids.torvus_bog as torvus_bog
import open_prime_rando.echoes.asset_ids.world as world
from open_prime_rando.patcher_editor import PatcherEditor

ELEVATOR_MEMORY_RELAY_PER_MREA = {
    world.GREAT_TEMPLE_MLVL: {
        great_temple.TEMPLE_TRANSPORT_A_MREA: 0x00000107,
        great_temple.TEMPLE_TRANSPORT_B_MREA: 0x0008002f,
        great_temple.TEMPLE_TRANSPORT_C_MREA: 0x00060046,
    },

    world.TEMPLE_GROUNDS_MLVL: {
        temple_grounds.TRANSPORT_TO_AGON_WASTES_MREA: 0x00180040,
        temple_grounds.TRANSPORT_TO_SANCTUARY_FORTRESS_MREA: 0x00330058,
        temple_grounds.TRANSPORT_TO_TORVUS_BOG_MREA: 0x001e0061,
    },

    world.AGON_WASTES_MLVL: {
        agon_wastes.TRANSPORT_TO_SANCTUARY_FORTRESS_MREA: 0x002d0064,
        agon_wastes.TRANSPORT_TO_TEMPLE_GROUNDS_MREA: 0x0000003f,
        agon_wastes.TRANSPORT_TO_TORVUS_BOG_MREA: 0x0013004d,
    },

    world.TORVUS_BOG_MLVL: {
        torvus_bog.TRANSPORT_TO_AGON_WASTES_MREA: 0x00210038,
        torvus_bog.TRANSPORT_TO_SANCTUARY_FORTRESS_MREA: 0x0045004b,
        torvus_bog.TRANSPORT_TO_TEMPLE_GROUNDS_MREA: 0x0000002e,
    },

    world.SANCTUARY_FORTRESS_MLVL: {
        sanctuary_fortress.TRANSPORT_TO_AGON_WASTES_MREA: 0x00130088,
        sanctuary_fortress.TRANSPORT_TO_TEMPLE_GROUNDS_MREA: 0x00000035,
        sanctuary_fortress.TRANSPORT_TO_TORVUS_BOG_MREA: 0x00190036,
    }
}


def apply_auto_enabled_elevators_patch(editor: PatcherEditor):
    """
    Patches that activates every elevator on room load
    """
    for mlvl_id, areas in ELEVATOR_MEMORY_RELAY_PER_MREA.items():
        for mrea_id, memory_relay_id in areas.items():
            area = editor.get_area(mlvl_id, mrea_id)
            timer = area.get_layer("Default").add_instance_with(Timer(
                editor_properties=EditorProperties(
                    name="Timer - Auto enable elevator",
                    active=False
                ),
                time=0.001,
                auto_start=True
            ))
            relay = area.get_instance(memory_relay_id)
            timer.add_connection(State.Zero, Message.Activate, relay)
