from unittest.mock import MagicMock, call

from open_prime_rando.echoes import custom_assets


def test_create_split_ammo():
    manager = MagicMock()

    custom_assets._create_split_ammo(manager)

    # Assert
    manager.duplicate_asset.assert_has_calls(
        [
            call(custom_assets.BEAM_AMMO_EXPANSION_CMDL, "dark_ammo_cmdl"),
            call(custom_assets.BEAM_AMMO_EXPANSION_ANCS, "dark_ammo_ancs"),
            call(custom_assets.BEAM_AMMO_EXPANSION_CMDL, "light_ammo_cmdl"),
            call(custom_assets.BEAM_AMMO_EXPANSION_ANCS, "light_ammo_ancs"),
        ]
    )
