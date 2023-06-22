from PyInstaller.utils.hooks import collect_data_files

import open_prime_rando.echoes.asset_ids.world

# https://pyinstaller.readthedocs.io/en/stable/hooks.html#provide-hooks-with-package

datas = collect_data_files('open_prime_rando', excludes=['__pyinstaller'])
hiddenimports = [
    f"open_prime_rando.echoes.asset_ids{module_name}"
    for module_name in open_prime_rando.echoes.asset_ids.world._DEDICATED_FILES.values()
]
