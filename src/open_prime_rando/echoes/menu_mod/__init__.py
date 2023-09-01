from retro_data_structures.formats import Mrea

from open_prime_rando.echoes.asset_ids import world
from open_prime_rando.echoes.custom_assets import custom_assets_path
from open_prime_rando.patcher_editor import PatcherEditor


def add_menu_mod(editor: PatcherEditor) -> None:
    template_mrea_raw: bytes = custom_assets_path().joinpath("EmptyArea.MREA").read_bytes()

    for world_name, world_id in world.NAME_TO_ID_MLVL.items():
        mlvl = editor.get_mlvl(world_id)

        mrea = Mrea.parse(template_mrea_raw, editor.target_game, editor)
        editor_mrea_id = editor.add_new_asset(f"{world_name} Menu Area", mrea, editor.find_paks(world_id))

        mlvl.add_area(editor_mrea_id)

        mlvl.areas
        pass

    pass
