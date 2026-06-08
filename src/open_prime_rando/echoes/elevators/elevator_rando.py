import functools

import pydantic
from retro_data_structures.base_resource import AssetId
from retro_data_structures.formats.mlvl import Mlvl
from retro_data_structures.formats.mrea import Area
from retro_data_structures.formats.strg import Strg
from retro_data_structures.properties.echoes.objects.WorldTeleporter import WorldTeleporter

from open_prime_rando.area_patcher import AreaPatcher
from open_prime_rando.echoes.pydantic_models import AreaReference, PydanticAssetId, PydanticInstanceId
from open_prime_rando.patcher_editor import PatcherEditor


class ElevatorChange(pydantic.BaseModel):
    elevator_id: PydanticInstanceId
    """The WorldTeleporter instance to modify."""

    target: AreaReference
    """The new Area for this elevator to travel to."""

    scan_strg: PydanticAssetId | None
    """The STRG file with the scan text for this elevator."""

    target_name: str
    """The name for the target Area to use in the scan text."""


def patch_elevator(editor: PatcherEditor, mlvl: Mlvl, area: Area, change: ElevatorChange) -> None:
    """
    Patches an elevator to target a different Area.
    """

    elevator = area.get_instance(change.elevator_id)
    with elevator.edit_properties(WorldTeleporter) as props:
        props.world = change.target.mlvl_id
        props.area = change.target.mrea_id

    if change.scan_strg is not None:
        strg = editor.get_file(change.scan_strg, Strg)
        strg.set_single_string(
            1,
            f"Access to &push;&main-color=#FF3333;{change.target_name} &pop;granted. "
            f"Step into the hologram to activate elevator.",
        )


def register_elevator_patch(
    area_patcher: AreaPatcher, mlvl_id: AssetId, mrea_id: AssetId, change: ElevatorChange
) -> None:
    """
    Registers an elevator change into the AreaPatcher, as well as any needed special handling for specific edge cases.
    """

    area_patcher.add_raw_function(
        mlvl_id,
        mrea_id,
        functools.partial(
            patch_elevator,
            change=change,
        ),
    )

    # TODO: register handlers for special cases such as Aerie
