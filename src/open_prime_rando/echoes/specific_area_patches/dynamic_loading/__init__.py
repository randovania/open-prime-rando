from __future__ import annotations

import typing

from open_prime_rando.echoes.specific_area_patches.dynamic_loading.aerie import aerie_dynamic_layer_loading
from open_prime_rando.echoes.specific_area_patches.dynamic_loading.central_mining_station import (
    central_mining_station_dynamic_layer_loading,
)
from open_prime_rando.echoes.specific_area_patches.dynamic_loading.dynamo_works import (
    dynamo_works_dynamic_layer_loading,
)
from open_prime_rando.echoes.specific_area_patches.dynamic_loading.main_gyro_chamber import (
    main_gyro_chamber_dynamic_layer_loading,
)
from open_prime_rando.echoes.specific_area_patches.dynamic_loading.main_reactor import (
    main_reactor_dynamic_layer_loading,
    storage_d_room_reload,
)
from open_prime_rando.echoes.specific_area_patches.dynamic_loading.main_research import (
    main_research_dynamic_layer_loading,
)
from open_prime_rando.echoes.specific_area_patches.dynamic_loading.sacrificial_chamber import (
    sacrificial_chamber_static_floor,
)
from open_prime_rando.echoes.specific_area_patches.dynamic_loading.sanctuary_entrance import (
    sanctuary_entrance_dynamic_layer_loading,
)
from open_prime_rando.echoes.specific_area_patches.dynamic_loading.torvus_temple import torvus_temple_second_pass

if typing.TYPE_CHECKING:
    from open_prime_rando.area_patcher import AreaPatcher


def register_all(area_patcher: AreaPatcher) -> None:
    """
    Applies changes to certain complex rooms, dynamically loading
    and unloading layers and assets to prevent memory and
    object limit related crashes, as well as to eliminate any
    cases of required room reloads.
    """

    for func in [
        dynamo_works_dynamic_layer_loading,
        main_reactor_dynamic_layer_loading,
        storage_d_room_reload,
        main_research_dynamic_layer_loading,
        torvus_temple_second_pass,
        aerie_dynamic_layer_loading,
        central_mining_station_dynamic_layer_loading,
        sanctuary_entrance_dynamic_layer_loading,
        sacrificial_chamber_static_floor,
        main_gyro_chamber_dynamic_layer_loading,
    ]:
        area_patcher.add_function(func)
