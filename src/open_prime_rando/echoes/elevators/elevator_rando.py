from retro_data_structures.formats.mrea import Area
from retro_data_structures.formats.strg import Strg
from retro_data_structures.properties.echoes.objects.WorldTeleporter import WorldTeleporter

from open_prime_rando.patcher_editor import PatcherEditor


def patch_elevator(editor: PatcherEditor, area: Area, elevator_id: int,
                   target_mlvl: int, target_mrea: int, target_strg: int, target_name: str):

    elevator = area.get_instance(elevator_id)
    with elevator.edit_properties(WorldTeleporter) as props:
        props.world = target_mlvl
        props.area = target_mrea

    if target_strg is not None:
        strg = editor.get_file(target_strg, Strg)
        strg.set_string(1, f"Access to &push;&main-color=#FF3333;{target_name} &pop;granted. "
                           f"Step into the hologram to activate elevator.")
