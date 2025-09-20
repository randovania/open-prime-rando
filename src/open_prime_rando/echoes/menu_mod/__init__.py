import logging

# import construct
# from retro_data_structures.formats import Mrea
from open_prime_rando.echoes.asset_ids import world

# from open_prime_rando.echoes.custom_assets import custom_asset_path
from open_prime_rando.echoes.menu_mod import menu
from open_prime_rando.patcher_editor import PatcherEditor


def add_menu_mod(editor: PatcherEditor) -> None:
    # template_mrea_raw: bytes = custom_asset_path().joinpath("EmptyArea.MREA").read_bytes()

    for world_name, world_id in world.NAME_TO_ID_MLVL.items():
        mlvl = editor.get_mlvl(world_id)

        # mrea = Mrea.parse(template_mrea_raw, editor.target_game, editor)
        # mrea.get_section("script_layers_section").clear()

        # editor_mrea_id = editor.add_new_asset(f"{world_name} Menu Area", mrea, editor.find_paks(world_id))
        # menu_area = mlvl.add_area(editor_mrea_id, editor.target_game.invalid_asset_id, internal_name="Menu")
        # menu_area._raw.docks.append(
        #     construct.Container(
        #         connecting_dock=[],
        #         dock_coordinates=[
        #             [0, 0, 0],
        #             [0, 5, 0],
        #             [5, 0, 0],
        #             [5, 5, 0],
        #         ],
        #     )
        # )

        for area in mlvl.areas:
            # if area.index == menu_area.index:
            #     continue

            menu.add_area_elements(
                editor,
                world_id,
                area,
                None,
                # menu_area,
            )

    for world_name, world_id in world.NAME_TO_ID_MLVL.items():
        mlvl = editor.get_mlvl(world_id)
        for area in mlvl.areas:
            logging.info("Updating %s", area.name)
            area.update_all_dependencies()
