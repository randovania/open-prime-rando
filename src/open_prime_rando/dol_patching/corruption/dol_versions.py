from retro_data_structures.game_check import Game

from open_prime_rando.dol_patching.all_prime_dol_patches import PowerupFunctionsAddresses
from open_prime_rando.dol_patching.corruption.dol_patches import CorruptionDolVersion

ALL_VERSIONS = [
    CorruptionDolVersion(
        game=Game.CORRUPTION,
        description="Wii NTSC",
        build_string_address=0x805822B0,
        build_string=b"!#$MetroidBuildInfo!#$2007/07/27 13:13 Build v3.436 (MP3)",
        sda2_base=0x806869C0,
        sda13_base=0x806801C0,
        game_state_pointer=0x8067DC0C,
        cplayer_vtable=0x80592C78,
        cstate_manager_global=0x805C4F70,
        string_display=None,
        # string_display=StringDisplayPatchAddresses(
        #     update_hint_state=None,
        #     message_receiver_string_ref=0x805a4200,
        #     wstring_constructor=None,
        #     display_hud_memo=0x801c6480,
        #     max_message_size=200,
        # ),
        powerup_functions=PowerupFunctionsAddresses(
            add_power_up=0x8019111C,
            incr_pickup=0x801913A0,
            decr_pickup=0x8019151C,
        ),
    ),
    CorruptionDolVersion(
        game=Game.CORRUPTION,
        description="Wii PAL",
        build_string_address=0x805843A8,
        build_string=b"!#$MetroidBuildInfo!#$2007/08/24 16:52 Build v3.453 (mp3)",
        sda2_base=0x80688FE0,
        sda13_base=0x806827C0,
        game_state_pointer=0x80680234,
        cplayer_vtable=0x80595238,
        cstate_manager_global=0x805C7570,
        string_display=None,
        powerup_functions=PowerupFunctionsAddresses(
            add_power_up=0x80191E2C,
            incr_pickup=0x801920B0,
            decr_pickup=0x8019222C,
        ),
    ),
    CorruptionDolVersion(
        game=Game.CORRUPTION,
        description="Wii NTSC-J",
        build_string_address=0x80587C2C,
        build_string=b"!#$MetroidBuildInfo!#$2007/11/12 14:15 Build v3.495 (jpn)",
        sda2_base=0x8068C840,
        sda13_base=0x80686000,
        game_state_pointer=0x80683A7C,
        cplayer_vtable=0x80598650,
        cstate_manager_global=0x805CAA30,
        string_display=None,
        powerup_functions=PowerupFunctionsAddresses(
            add_power_up=0x801932D0,
            incr_pickup=0x80193554,
            decr_pickup=0x801936D0,
        ),
    ),
]
