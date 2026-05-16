from __future__ import annotations

import functools
import logging
import uuid
from random import Random
from typing import TYPE_CHECKING

import open_prime_rando_practice_mod
from PIL import Image
from ppc_asm.assembler import ppc
from retro_data_structures.formats.banner import Banner
from retro_data_structures.game_check import Game

from open_prime_rando import practice_mod
from open_prime_rando.area_patcher import AreaPatcher
from open_prime_rando.dol_patching import ppc_helper
from open_prime_rando.dol_patching.echoes import dol_patcher
from open_prime_rando.dol_patching.echoes.beam_configuration import BeamAmmoConfiguration
from open_prime_rando.dol_patching.echoes.user_preferences import OprEchoesUserPreferences
from open_prime_rando.echoes import (
    custom_assets,
    general_changes,
    inverted,
    logbook,
    pickups,
    small_randomizations,
    specific_area_patches,
    starting_items,
    translator_gates,
)
from open_prime_rando.echoes.asset_ids import world
from open_prime_rando.echoes.elevators import auto_enabled_elevator_patches
from open_prime_rando.echoes.specific_area_patches import front_end
from open_prime_rando.patcher_editor import IsoFileProvider, IsoFileWriter, PatcherEditor

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from open_prime_rando.dol_patching.echoes.dol_patches import EchoesDolVersion
    from open_prime_rando.echoes.rando_configuration import AreaReference, RandoConfiguration


LOG = logging.getLogger("echoes_patcher")


def _default_dol_patches() -> dol_patcher.EchoesDolPatchesData:
    return dol_patcher.EchoesDolPatchesData(
        world_uuid=uuid.UUID("00000000-0000-1111-0000-000000000000"),
        energy_per_tank=100,
        beam_configurations=[
            BeamAmmoConfiguration.from_json(it)
            for it in [
                {
                    "item_index": 0,
                    "ammo_a": -1,
                    "ammo_b": -1,
                    "uncharged_cost": 0,
                    "charged_cost": 0,
                    "combo_missile_cost": 5,
                    "combo_ammo_cost": 0,
                },
                {
                    "item_index": 1,
                    "ammo_a": 45,
                    "ammo_b": -1,
                    "uncharged_cost": 1,
                    "charged_cost": 5,
                    "combo_missile_cost": 5,
                    "combo_ammo_cost": 30,
                },
                {
                    "item_index": 2,
                    "ammo_a": 46,
                    "ammo_b": -1,
                    "uncharged_cost": 1,
                    "charged_cost": 5,
                    "combo_missile_cost": 5,
                    "combo_ammo_cost": 30,
                },
                {
                    "item_index": 3,
                    "ammo_a": 46,
                    "ammo_b": 45,
                    "uncharged_cost": 1,
                    "charged_cost": 5,
                    "combo_missile_cost": 5,
                    "combo_ammo_cost": 30,
                },
            ]
        ],
        safe_zone_heal_per_second=1.0,
        user_preferences=OprEchoesUserPreferences(),
        default_items={"visor": "Combat Visor", "beam": "Power Beam"},
        unvisited_room_names=True,
        teleporter_sounds=True,
        dangerous_energy_tank=False,
    )


_ALL_FEATURES = False


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


def _apply_patches(editor: PatcherEditor, configuration: RandoConfiguration, output: IsoFileWriter) -> None:
    custom_assets.create_custom_assets(editor)
    dol_version = dol_patcher.apply_patches(editor.dol, _default_dol_patches())

    if configuration.inverted_mode:
        inverted.apply_inverted(editor)

    area_patcher = AreaPatcher(editor, list(world.NAME_TO_ID_MLVL.values()))
    rng = Random(configuration.seed)

    specific_area_patches.required_fixes.register_all(area_patcher)
    specific_area_patches.version_differences.register_all(area_patcher, dol_version.echoes_version)
    specific_area_patches.rebalance_patches.register_all(area_patcher)

    add_pickup_map_icon(editor)

    # edit frontend
    area_patcher.add_frontend_function(
        functools.partial(
            front_end.edit_front_end,
            title_screen_text=configuration.title_screen_text,
        )
    )
    logbook.patch_logbook(editor, dol_version)

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

    # area changes
    small_randomizations.register_small_randomizations(area_patcher, rng)

    disable_hud_popup = True
    for world_change in configuration.world_changes:
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

    if _ALL_FEATURES:
        auto_enabled_elevator_patches.apply_auto_enabled_elevators_patch(editor)

    if configuration.practice_mod != open_prime_rando_practice_mod.PracticeModMode.disabled:
        practice_mod.patch_dol(
            editor.dol,
            open_prime_rando_practice_mod.get_elf_for(dol_version.practice_mod_version, configuration.practice_mod),
        )

    # Save our changes
    area_patcher.perform_changes()
    editor.build_modified_files()
    patch_game_name_and_id(editor, output, new_name=configuration.game_title, id_suffix="NR")
    remove_attract_videos(editor, output)
    editor.save_modifications(output)


def patch_iso(
    input_iso: Path,
    output_iso: Path,
    configuration: RandoConfiguration,
    status_update: Callable[[str, float], None] = lambda s, _: LOG.info(s),
) -> None:
    """

    :param input_iso:
    :param output_iso:
    :param configuration:
    :param status_update:
    :return:
    """
    file_provider = IsoFileProvider(input_iso)

    editor = PatcherEditor(file_provider, Game.ECHOES)
    output = IsoFileWriter(file_provider)
    _apply_patches(editor, configuration, output)

    _last_percent = None

    def _write_callback(bytes_written: int, total_bytes: int) -> None:
        nonlocal _last_percent
        percent = int(100 * (bytes_written / total_bytes))
        if percent != _last_percent:
            status_update(f"Writing ISO: {percent}%", bytes_written / total_bytes)
            _last_percent = percent

    output.commit(
        output_iso,
        callback=_write_callback,
    )

    status_update("Finished", 1.0)
