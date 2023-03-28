import open_prime_rando.echoes.asset_ids.agon_wastes as agon_wastes
import open_prime_rando.echoes.asset_ids.great_temple as great_temple
import open_prime_rando.echoes.asset_ids.sanctuary_fortress as sanctuary_fortress
import open_prime_rando.echoes.asset_ids.temple_grounds as temple_grounds
import open_prime_rando.echoes.asset_ids.torvus_bog as torvus_bog
from open_prime_rando.patcher_editor import PatcherEditor

from retro_data_structures.formats.script_object import ScriptInstanceHelper
from retro_data_structures.game_check import Game
from retro_data_structures.properties.echoes.objects.Timer import Timer

ELEVATOR_MEMORY_RELAY_PER_MREA = {
    # Great Temple elevators
    great_temple.TEMPLE_TRANSPORT_A_MREA: 0x00000107,
    great_temple.TEMPLE_TRANSPORT_B_MREA: 0x0008002f,
    great_temple.TEMPLE_TRANSPORT_C_MREA: 0x00060046,
    # Temple Grounds elevators
    temple_grounds.TRANSPORT_TO_AGON_WASTES_MREA: 0x00180040,
    temple_grounds.TRANSPORT_TO_SANCTUARY_FORTRESS_MREA: 0x00330058,
    temple_grounds.TRANSPORT_TO_TORVUS_BOG_MREA: 0x001e0061,
    # Agon Wastes elevators
    agon_wastes.TRANSPORT_TO_SANCTUARY_FORTRESS_MREA: 0x002d0064,
    agon_wastes.TRANSPORT_TO_TEMPLE_GROUNDS_MREA: 0x0000003f,
    agon_wastes.TRANSPORT_TO_TORVUS_BOG_MREA: 0x0013004d,
    # Torvus Bog elevators
    torvus_bog.TRANSPORT_TO_AGON_WASTES_MREA: 0x00210038,
    torvus_bog.TRANSPORT_TO_SANCTUARY_FORTRESS_MREA: 0x0045004b,
    torvus_bog.TRANSPORT_TO_TEMPLE_GROUNDS_MREA: 0x0000002e,
    # Sanctuary Fortress elevators
    sanctuary_fortress.TRANSPORT_TO_AGON_WASTES_MREA: 0x00130088,
    sanctuary_fortress.TRANSPORT_TO_TEMPLE_GROUNDS_MREA: 0x00000035,
    sanctuary_fortress.TRANSPORT_TO_TORVUS_BOG_MREA: 0x00190036,
}


def apply_auto_enabled_elevators_patch(editor: PatcherEditor):
    """
    Patches that activates every elevator on room load
    """
    for elevator_mrea, memory_relay_id in ELEVATOR_MEMORY_RELAY_PER_MREA.items():
        area = editor.get_mrea(elevator_mrea)

        """
        Add timer that activates the memory relay of the elevator hologram
        """
        timer = ScriptInstanceHelper.new_instance(Game.ECHOES, "TIMR")
        properties = timer.get_properties_as(Timer)

        properties.editor_properties.transform.position = [0.000000, 0.000000, 0.000000]
        properties.editor_properties.transform.rotation = [0.000000, 0.000000, 0.000000]
        properties.editor_properties.transform.scale = [1.000000, 1.000000, 1.000000]
        properties.editor_properties.name = "Timer - Auto enable elevator"
        properties.editor_properties.active = 0
        properties.editor_properties.unknown = 3
        properties.time = 0.001
        properties.random_adjust = 0.0
        properties.auto_reset = False
        properties.auto_start = True

        timer.add_connection("ZERO", "ACTV", memory_relay_id)

