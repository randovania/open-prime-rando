

import dataclasses
from construct import Path
import construct
from ppc_asm.assembler import ppc
from open_prime_rando.patcher_editor import PatcherEditor
from retro_data_structures.common_types import Transform4f, AssetId32


SQuickplayParameters = construct.Struct(
    construct.Const(0x00BADB01, construct.Int32ub),
    construct.Const(2, construct.Int32ub),
    "FeatureFlags" / construct.FlagsEnum(
        construct.Int32ub,
        JumpToArea=1,
        SetSpawnPosition=2,
        GiveAllItems=4,
    ),
    "BootWorldAssetID" / AssetId32,
    "BootAreaAssetID" / AssetId32,
    construct.Const(0, construct.Int32ub),  # padding to 64
    "BootAreaLayerFlags" / construct.Int64ub,
    "SpawnTransform" / Transform4f,
)


def add_quickplay(editor: PatcherEditor) -> None:
    quickplay_dir = Path(__file__).parent.joinpath("custom_assets", "quickplay")
    patch_data = quickplay_dir.joinpath("v1.028.bin").read_bytes()

    aligned_dol_size = (len(editor.dol.dol_file) + 31) & ~31
    patch_size = len(patch_data)
    aligned_patch_size = (patch_size + 31) & ~31

    new_sections = list(editor.dol.header.sections)
    for section in new_sections:
        if section.size == 0:
            # Use this section for quickplay code
            section.base_address = 0x80002000
            section.offset = aligned_dol_size
            section.size = aligned_patch_size
        break

    editor.dol.header = dataclasses.replace(
        editor.dol.header,
        sections=tuple(new_sections),
    )
    editor.dol.write(0x80002000, patch_data + bytes(aligned_patch_size - patch_size))
    editor.dol.symbols["PPCSetFpIEEEMode"] = 0x8035712c
    editor.dol.symbols["rel_loader_hook"] = 0x8000207c
    editor.dol.write_instructions("PPCSetFpIEEEMode", [
        ppc.b("rel_loader_hook"),
    ])

    editor.custom_files["patches.rel"] = quickplay_dir.joinpath("v1.028.rel").read_bytes()
    editor.custom_files["dbgconfig"] = SQuickplayParameters.build({
        "FeatureFlags": [],
        "BootWorldAssetID": 0,
        "BootAreaAssetID": 0,
        "BootAreaLayerFlags": 0xFFFFFFFFFFFFFFFF,
        "SpawnTransform": [0.0] * 12,
    })
