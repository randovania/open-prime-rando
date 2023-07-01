from open_prime_rando.echoes.specific_area_patches.rebalance_patches import rebalance_patches
from open_prime_rando.echoes.specific_area_patches.required_fixes import required_fixes
from open_prime_rando.echoes.specific_area_patches.version_differences import EchoesVersion, patch_version_differences
from open_prime_rando.patcher_editor import PatcherEditor


def specific_patches(editor: PatcherEditor, area_patches: dict):
    required_fixes(editor)
    patch_version_differences(editor, EchoesVersion.NTSC_U)
    if area_patches["rebalance_world"]:
        rebalance_patches(editor)
