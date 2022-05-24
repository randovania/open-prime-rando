from unittest.mock import MagicMock, call

from open_prime_rando.echoes import custom_assets


def test_create_split_ammo():
    manager = MagicMock()
    asset = manager.get_parsed_asset.return_value
    find_paks = manager.find_paks.return_value

    custom_assets._create_split_ammo(manager)

    # Assert
    manager.add_new_asset.assert_has_calls([
        call('dark_ammo_cmdl', asset, find_paks),
        call('dark_ammo_ancs', asset, find_paks),
        call('light_ammo_cmdl', asset, find_paks),
        call('light_ammo_ancs', asset, find_paks)
    ])
