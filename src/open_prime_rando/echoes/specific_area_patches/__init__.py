from open_prime_rando.echoes.specific_area_patches import rebalance_patches, required_fixes
from open_prime_rando.echoes.specific_area_patches.version_differences import EchoesVersion, patch_version_differences
from open_prime_rando.patcher_editor import PatcherEditor


def specific_patches(editor: PatcherEditor, area_patches: dict, legacy_compatibility: bool):
    if legacy_compatibility:
        required_fixes.torvus_temple(editor)
        required_fixes.command_center_door(editor)
    else:
        required_fixes.apply_all(editor)
        patch_version_differences(editor, EchoesVersion.NTSC_U)  # TODO: detect version
        if area_patches["rebalance_world"]:
            rebalance_patches.apply_all(editor)
