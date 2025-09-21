import logging

import construct
from retro_data_structures.formats import Mrea
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.objects.Dock import Dock

from open_prime_rando.echoes.asset_ids import world

# from open_prime_rando.echoes.custom_assets import custom_asset_path
from open_prime_rando.echoes.menu_mod import menu
from open_prime_rando.patcher_editor import PatcherEditor


def add_menu_mod(editor: PatcherEditor) -> None:
    # template_mrea_raw: bytes = custom_asset_path().joinpath("EmptyArea.MREA").read_bytes()

    for world_name, world_id in world.NAME_TO_ID_MLVL.items():
        mlvl = editor.get_mlvl(world_id)

        editor_mrea_id = editor.duplicate_asset(0x131C3388, f"{world_name} Menu Area")
        for pak in editor.find_paks(world_id):
            editor.ensure_present(pak, editor_mrea_id)
        mrea = editor.get_file(editor_mrea_id, Mrea)

        mrea.get_section("script_layers_section").clear()

        menu_area = mlvl.add_area(editor_mrea_id, editor.target_game.invalid_asset_id, internal_name="Menu")

        default_layer = menu_area.add_layer("Default", True)
        menu_area.add_layer("!No Load", False)

        default_layer.add_instance_with(
            Dock(
                editor_properties=EditorProperties(
                    "Special",
                ),
                dock_number=0,
                area_number=menu_area._index,
            )
        )
        menu_area._raw.docks.append(
            construct.Container(
                connecting_dock=[],
                dock_coordinates=[
                    [0, 0, 0],
                    [0, 5, 0],
                    [5, 0, 0],
                    [5, 5, 0],
                ],
            )
        )

        for area in mlvl.areas:
            if area.index == menu_area.index:
                continue

            menu.add_area_elements(
                editor,
                world_id,
                area,
                # None,
                menu_area,
            )

    for world_name, world_id in world.NAME_TO_ID_MLVL.items():
        mlvl = editor.get_mlvl(world_id)
        for area in mlvl.areas:
            logging.info("Updating %s", area.name)
            area.update_all_dependencies()
