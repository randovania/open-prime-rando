from __future__ import annotations

import functools
import logging
from random import Random
from typing import TYPE_CHECKING

import open_prime_rando_practice_mod
from PIL import Image
from ppc_asm.assembler import ppc
from retro_data_structures.formats.banner import Banner
from retro_data_structures.formats.frme import Frme
from retro_data_structures.formats.strg import Strg
from retro_data_structures.game_check import Game

from open_prime_rando import practice_mod
from open_prime_rando.area_patcher import AreaPatcher
from open_prime_rando.dol_patching import all_prime_dol_patches, ppc_helper
from open_prime_rando.dol_patching.dol_version import find_version_for_dol
from open_prime_rando.dol_patching.echoes import (
    beam_cost,
    dol_patches,
    dol_versions,
    game_options,
    inventory_slot,
    stk_on_map,
)
from open_prime_rando.echoes import (
    custom_assets,
    custom_items,
    damage_changes,
    dock_lock_rando,
    general_changes,
    inverted,
    logbook,
    pickups,
    small_randomizations,
    specific_area_patches,
    starting_items,
    suit_cosmetics,
    translator_gates,
)
from open_prime_rando.echoes.asset_ids import world
from open_prime_rando.echoes.elevators import auto_enabled_elevator_patches
from open_prime_rando.echoes.specific_area_patches import front_end
from open_prime_rando.echoes.version import EchoesVersion
from open_prime_rando.patcher_editor import IsoFileProvider, IsoFileWriter, PatcherEditor

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from open_prime_rando.dol_patching.echoes.dol_patches import EchoesDolVersion
    from open_prime_rando.echoes.rando_configuration import AreaReference, RandoConfiguration, StringChange, WorldChange

LOG = logging.getLogger("echoes_patcher")

type StatusUpdate = Callable[[str, float], None]


def _fix_dumb_broken_strg(editor: PatcherEditor):
    """These assets have an outdated version in FrontEnd.pak."""

    for asset_id, source in [
        (0xB4590AC3, "MiscData.pak"),
        (0xA5C74B8B, "LogBook.pak"),
    ]:
        asset = editor.pak_group.get_pak(source).get_asset(asset_id)
        if asset is not None:
            editor.replace_asset(asset_id, asset)


def edit_starting_area_dol(editor: PatcherEditor, version: EchoesDolVersion, starting_area: AreaReference) -> None:
    function_address = version.starting_area_serialize_clean_slot_address  # CGameState::SerializeNewForCleanSlot

    # SetMLvlId argument
    ppc_helper.load_32bit_int(
        editor.dol,
        ppc.r4,
        starting_area.mlvl_id,
        function_address + 12 * 4,
        function_address + 14 * 4,
    )

    # StateForWorld argument
    ppc_helper.load_32bit_int(
        editor.dol,
        ppc.r4,
        starting_area.mlvl_id,
        function_address + 16 * 4,
        function_address + 18 * 4,
    )

    # SetDesiredAreaAssetId
    ppc_helper.load_32bit_int(
        editor.dol,
        ppc.r4,
        starting_area.mrea_id,
        function_address + 20 * 4,
        function_address + 21 * 4,
    )


def patch_game_name_and_id(editor: PatcherEditor, output: IsoFileWriter, new_name: str, id_suffix: str) -> None:
    """
    Changes the suffix of the Game ID, name and banner image.
    """

    game_id = output.source.disc_reader.header().game_id
    game_id = game_id[:-2] + id_suffix

    output.patcher.set_header(
        game_id=game_id,
        game_title=new_name,
    )

    raw_banner = editor.provider.read_binary("opening.bnr")
    banner = Banner.parse(raw_banner)
    for metadata in banner.metadata:
        metadata.long_title = new_name

    with Image.open(custom_assets.custom_asset_path().joinpath("banner.png")) as banner_image:
        banner.image = banner_image

    with output.open_binary("opening.bnr") as new_banner:
        new_banner.write(banner.build())


def remove_attract_videos(editor: PatcherEditor, output: IsoFileWriter) -> None:
    """
    Replace all Attract THP files with 0-byte files, as that causes them to not be loaded.
    """
    for attract in list(editor.provider.rglob("Video/Attract*.thp")):
        with output.open_binary(attract) as f:
            f.write(b"")


def add_pickup_map_icon(editor: PatcherEditor) -> None:
    pickup_map_icon_id = editor.resolve_asset_id("pickup_map_icon.TXTR")

    # add custom icon to all the same paks as the Translator icon
    for pak in editor.find_paks(0xC6059D2F):
        editor.ensure_present(pak, pickup_map_icon_id)


def edit_string(editor: PatcherEditor, change: StringChange) -> None:
    strg = editor.get_file(change.strg_id, Strg)
    strg.set_string_list(change.strings)


def apply_stk_on_map(editor: PatcherEditor, dol_version: EchoesDolVersion) -> None:
    stk_on_map.apply_stk_on_map(dol_version.stk_map_icon, editor.dol)

    if dol_version.echoes_version == EchoesVersion.NTSC_U:
        frme_id = 0x834E8FA4
    elif dol_version.echoes_version == EchoesVersion.PAL:
        frme_id = 0xBAF48D93
    else:
        raise RuntimeError(f"Unsupported EchoesVersion: {dol_version.echoes_version}")

    map_screen = editor.get_file(frme_id, Frme)  # FRME_MapScreen_0

    for widget in map_screen.raw.widgets:
        if widget.name != "textpane_keylegend":
            continue
        widget.specific.vec[0] -= 1.3  # shift to the left a bit
        widget.specific.word_wrap = 2  # change justification to Right

    main_strg = editor.get_file(0xB4590AC3, Strg)
    main_strg.append_string(
        f"&image=SI,1.0,1.0,{editor.resolve_asset_id('stk_icon_found.TXTR'):08X};",
        name="STKOn",
    )

    for pak in editor.find_paks(0x07180ADA):
        editor.ensure_present(pak, "stk_icon_found.TXTR")


def apply_dol_patches(editor: PatcherEditor, configuration: RandoConfiguration, dol_version: EchoesDolVersion) -> None:
    """Applies all the dol patches that aren't specific to some other place."""

    dol_patches.apply_mandatory_fixes(dol_version, editor.code_cave)
    all_prime_dol_patches.apply_remote_execution_patch(Game.ECHOES, dol_version.string_display, editor.dol)
    all_prime_dol_patches.apply_build_info_patch(dol_version, editor.dol, configuration.world_uuid)
    dol_patches.apply_map_door_changes(dol_version.map_door_types, editor.dol)
    dol_patches.apply_unvisited_room_names(dol_version, editor.dol, configuration.map_visibility.unvisited_room_names)
    beam_cost.apply_patch(dol_version.beam_cost_addresses, editor.dol, configuration.beam_configuration)
    game_options.apply_patch(
        dol_version.game_options_constructor_address, editor.dol, configuration.game_options_defaults
    )
    inventory_slot.setup_inventory_slot_to_item(dol_version, editor)


def register_world_changes(area_patcher: AreaPatcher, world_changes: list[WorldChange]) -> None:
    """Register all WorldChanges in the AreaPatcher."""

    disable_hud_popup = True
    for world_change in world_changes:
        for area_change in world_change.area_changes:
            for pickup_change in area_change.pickups:
                area_patcher.add_raw_function(
                    world_change.mlvl_id,
                    area_change.mrea_id,
                    functools.partial(
                        pickups.patch_pickup,
                        modification=pickup_change,
                        disable_hud_popup=disable_hud_popup,
                    ),
                )

            for translator_gate_change in area_change.translator_gates:
                area_patcher.add_raw_function(
                    world_change.mlvl_id,
                    area_change.mrea_id,
                    functools.partial(
                        translator_gates.patch_translator_gate,
                        modification=translator_gate_change,
                    ),
                )

            for dock_type_change in area_change.door_locks:
                area_patcher.add_raw_function(
                    world_change.mlvl_id,
                    area_change.mrea_id,
                    functools.partial(
                        dock_lock_rando.apply_door_rando,
                        change=dock_type_change,
                    ),
                )


def _apply_patches(
    editor: PatcherEditor,
    configuration: RandoConfiguration,
    output: IsoFileWriter,
    area_status_update: StatusUpdate,
    build_files_status_update: StatusUpdate,
    build_paks_status_update: StatusUpdate,
) -> None:
    custom_assets.create_custom_assets(editor)
    dock_lock_rando.add_custom_models(editor)

    dol_version: EchoesDolVersion = find_version_for_dol(editor.dol, dol_versions.ALL_VERSIONS)

    if dol_version.echoes_version == EchoesVersion.NTSC_U:
        _fix_dumb_broken_strg(editor)

    apply_dol_patches(editor, configuration, dol_version)
    custom_items.apply_changes(dol_version, editor.code_cave, configuration.custom_items)

    apply_stk_on_map(editor, dol_version)

    damage_changes.apply_damage_changes(editor, configuration.damage_changes, dol_version)

    if configuration.inverted_mode:
        inverted.apply_inverted(editor)

    area_patcher = AreaPatcher(editor, list(world.NAME_TO_ID_MLVL.values()))
    rng = Random(configuration.seed)

    specific_area_patches.required_fixes.register_all(area_patcher)
    specific_area_patches.quality_of_life.register_all(area_patcher)
    specific_area_patches.rebalance_patches.register_all(area_patcher)
    specific_area_patches.dynamic_loading.register_all(area_patcher)

    specific_area_patches.version_differences.register_all(area_patcher, dol_version.echoes_version)

    add_pickup_map_icon(editor)
    suit_cosmetics.apply_custom_suits(editor, configuration.suit_replacement)

    # edit frontend
    area_patcher.add_frontend_function(
        functools.partial(
            front_end.edit_front_end,
            title_screen_text=configuration.title_screen_text,
        )
    )
    logbook.patch_logbook(editor, dol_version, configuration)

    for string_change in configuration.string_changes:
        edit_string(editor, string_change)

    # edit starting area
    edit_starting_area_dol(editor, dol_version, configuration.starting_area)
    area_patcher.add_frontend_function(
        functools.partial(front_end.edit_starting_area_teleporter, starting_area=configuration.starting_area)
    )

    area_patcher.add_raw_function(
        configuration.starting_area.mlvl_id,
        configuration.starting_area.mrea_id,
        functools.partial(
            starting_items.edit_starting_items,
            items_config=configuration.starting_items,
        ),
    )

    # general changes
    general_changes.apply_corrupted_memory_card_change(editor)
    area_patcher.add_global_function(general_changes.allow_skippable_cutscenes)
    area_patcher.add_global_function(general_changes.loop_conditional_relays)
    area_patcher.add_global_function(
        functools.partial(general_changes.change_map_visibility, map_visibility=configuration.map_visibility)
    )

    if configuration.auto_enabled_elevators:
        auto_enabled_elevator_patches.register(area_patcher)

    # area changes
    small_randomizations.register_small_randomizations(area_patcher, rng)
    register_world_changes(area_patcher, configuration.world_changes)

    if configuration.practice_mod != open_prime_rando_practice_mod.PracticeModMode.disabled:
        practice_mod.patch_dol(
            editor.dol,
            open_prime_rando_practice_mod.get_elf_for(dol_version.practice_mod_version, configuration.practice_mod),
        )

    inventory_slot.create_new_inventory_slot_array(dol_version, editor)

    # Save our changes
    area_patcher.perform_changes(area_status_update)
    editor.build_modified_files(build_files_status_update)
    patch_game_name_and_id(editor, output, new_name=configuration.game_title, id_suffix="NR")
    remove_attract_videos(editor, output)
    editor.code_cave.fulfill_requests()
    editor.save_modifications(output, build_paks_status_update)


def patch_iso(
    input_iso: Path,
    output_iso: Path,
    configuration: RandoConfiguration,
    area_status_update: StatusUpdate | None = None,
    build_files_status_update: StatusUpdate | None = None,
    build_paks_status_update: StatusUpdate | None = None,
    nod_status_update: StatusUpdate | None = None,
) -> None:
    """

    :param input_iso:
    :param output_iso:
    :param configuration:
    :param status_update:
    :return:
    """

    def default_status_update(text: str, percent: float) -> None:
        LOG.info(text)

    if area_status_update is None:
        area_status_update = default_status_update

    if build_files_status_update is None:
        build_files_status_update = default_status_update

    if build_paks_status_update is None:
        build_paks_status_update = default_status_update

    if nod_status_update is None:
        nod_status_update = default_status_update

    file_provider = IsoFileProvider(input_iso)

    editor = PatcherEditor(file_provider, Game.ECHOES)
    output = IsoFileWriter(file_provider)
    _apply_patches(
        editor, configuration, output, area_status_update, build_files_status_update, build_paks_status_update
    )

    _last_percent = None

    def _write_callback(bytes_written: int, total_bytes: int) -> None:
        nonlocal _last_percent
        percent = int(100 * (bytes_written / total_bytes))
        if percent != _last_percent:
            nod_status_update(f"Writing ISO: {percent}%", bytes_written / total_bytes)
            _last_percent = percent

    output.commit(
        output_iso,
        callback=_write_callback,
    )

    nod_status_update("Finished", 1.0)
