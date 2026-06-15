from __future__ import annotations

import dataclasses
import functools
from typing import TYPE_CHECKING

import pydantic
from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.formats import Scan, Strg
from retro_data_structures.formats.mapa import MappableObject, ObjectTypeMP2, ObjectVisibility
from retro_data_structures.properties.echoes.archetypes import EditorProperties, Transform
from retro_data_structures.properties.echoes.core import Vector
from retro_data_structures.properties.echoes.objects import Dock, ScannableObjectInfo
from retro_data_structures.properties.echoes.objects.PointOfInterest import PointOfInterest
from retro_data_structures.properties.echoes.objects.SpawnPoint import SpawnPoint
from retro_data_structures.transform import Transform as _Transform

from open_prime_rando import area_utils
from open_prime_rando.area_patcher import AreaPatcher, decorate_patcher
from open_prime_rando.echoes.asset_ids import agon_wastes, sanctuary_fortress, temple_grounds, world
from open_prime_rando.echoes.asset_ids.agon_wastes import PORTAL_TERMINAL_MREA
from open_prime_rando.echoes.pydantic_models import PydanticAssetId
from open_prime_rando.echoes.specific_area_patches.rebalance_patches import ObjectWithEditorProperties

if TYPE_CHECKING:
    from collections.abc import Iterable

    from retro_data_structures.formats.mlvl import Mlvl
    from retro_data_structures.formats.mrea import Area
    from retro_data_structures.formats.script_object import InstanceId, ScriptInstance

    from open_prime_rando.echoes.rando_configuration import MapVisibility
    from open_prime_rando.patcher_editor import PatcherEditor


class PortalChange(pydantic.BaseModel):
    """
    Changes a portal to connect to a different one.

    All portals must connect to a portal that connects back.
    """

    source_dock_name: str
    """Name of the script object of type Dock associated with the portal to change."""

    target_mrea_id: PydanticAssetId
    """The ID of the area to connect to. Must belong to the same world."""

    target_dock_name: str
    """Similar to source_dock_name, but in the target area."""

    portal_scan_destination: str
    """The name to use as the portal destination in the scan."""


@dataclasses.dataclass(frozen=True)
class NewPortalDef:
    mlvl_id: PydanticAssetId
    mrea_id: PydanticAssetId
    dock_name: str


def _get_transform(obj: ScriptInstance) -> Transform:
    prop = obj.get_properties()
    assert isinstance(prop, ObjectWithEditorProperties)
    assert isinstance(prop.editor_properties, EditorProperties)
    return prop.editor_properties.transform


_PORTAL_POSITION_REFERENCE = "RadialDamage 001"


def _get_portal(editor: PatcherEditor, light_portal: bool) -> tuple[Transform, dict[InstanceId, ScriptInstance]]:
    sanc = editor.get_mlvl(world.SANCTUARY_FORTRESS_MLVL)
    storage = sanc.get_area(
        sanctuary_fortress.HIVE_CACHE_3_MREA if light_portal else sanctuary_fortress.DYNAMO_STORAGE_MREA
    )

    position_reference = storage.get_instance(_PORTAL_POSITION_REFERENCE)
    rift_controller = storage.get_instance("PORTAL TO RIFT CONTROLLER")
    return _get_transform(position_reference), area_utils.get_all_ids_related_to(
        storage, rift_controller.id, {SpawnPoint}
    )


def _is_dark_area(area: Area) -> bool:
    return area.mapa.is_dark_world


def _get_connecting_dock(mlvl: Mlvl, dock: Dock) -> tuple[Area, ScriptInstance]:
    areas = list(mlvl.areas)
    connecting_dock = areas[dock.area_number]._raw.docks[dock.dock_number].connecting_dock
    if len(connecting_dock) != 1:
        raise KeyError(f"Dock {dock} has more then one connection")

    area_index: int = connecting_dock[0].area_index
    dock_index: int = connecting_dock[0].dock_index
    area = areas[area_index]
    for instance in area.all_instances:
        if instance.script_type == Dock and instance.get_properties_as(Dock).dock_number == dock_index:
            return area, instance
    raise RuntimeError(f"Dock with number {dock_index} does not exist in {area}")


def _find_object_with_name(name: str, instances: Iterable[ScriptInstance]) -> ScriptInstance:
    for inst in instances:
        if inst.name == name:
            return inst
    raise KeyError(f"No instance with name {name} found")


def add_portal_to(
    editor: PatcherEditor,
    mlvl: Mlvl,
    area: Area,
    dock_name: str,
    map_icon_visibility: ObjectVisibility,
) -> None:

    source_transform, all_ids = _get_portal(editor, _is_dark_area(area))

    # Where to put
    target_layer = area.get_layer("Default")
    target_dock = area.get_instance(dock_name)
    existing_arrival = next(
        obj
        for connection in target_dock.connections
        if (obj := area.get_instance(connection.target)).script_type == SpawnPoint
    )

    connected_area, connected_dock = _get_connecting_dock(area.parent_mlvl, target_dock.get_properties_as(Dock))
    other_area_objects = area_utils.get_all_ids_related_to(connected_area, connected_dock.id)
    target_transform = _get_transform(_find_object_with_name(_PORTAL_POSITION_REFERENCE, other_area_objects.values()))

    delta_position = target_transform.position - source_transform.position
    delta_rotation = target_transform.rotation - source_transform.rotation

    old_to_new: dict[InstanceId, ScriptInstance] = {}
    for source_id, source_obj in all_ids.items():
        if source_obj.script_type == Dock:
            old_to_new[source_id] = target_dock
        elif source_obj.script_type == SpawnPoint:
            old_to_new[source_id] = existing_arrival
        else:
            source_props = source_obj.get_properties()
            if isinstance(source_props, ObjectWithEditorProperties):
                assert isinstance(source_props.editor_properties, EditorProperties)
                transform = source_props.editor_properties.transform
                transform.position = (
                    transform.position.rotate(delta_rotation, source_transform.position) + delta_position
                )
                transform.rotation += delta_rotation

            old_to_new[source_id] = target_layer.add_instance_with(source_props)

    for source_id, new_obj in old_to_new.items():
        if new_obj.script_type == SpawnPoint:
            continue

        new_obj.connections = new_obj.connections + tuple(
            dataclasses.replace(
                old_connection,
                target=old_to_new[old_connection.target].id,
            )
            for old_connection in all_ids[source_id].connections
        )

        if new_obj.name.strip() == "PORTAL TO RIFT":
            area.mapa.mappable_objects.append(
                MappableObject[ObjectTypeMP2].create(
                    object_type=ObjectTypeMP2.Portal,
                    visibility_mode=map_icon_visibility,
                    editor_id=new_obj.id,
                    transform=_Transform.from_vectors(
                        position=new_obj.editor_properties.transform.position,
                        rotation=Vector(),
                        scale=Vector(1.0, 1.0, 1.0),
                    ),
                )
            )


_NEW_PORTALS = [
    NewPortalDef(world.SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.TRANSIT_STATION_MREA, "VirtualDock_North_Middle"),
    NewPortalDef(world.SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.TRANSIT_STATION_MREA, "VirtualDock_North_Left"),
    NewPortalDef(world.SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.MAIN_RESEARCH_MREA, "VirtualNorth"),
    NewPortalDef(world.SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.HIVE_PORTAL_CHAMBER_MREA, "VirtualDock_North_Right"),
    NewPortalDef(world.SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.HIVE_PORTAL_CHAMBER_MREA, "VirtualDock_South"),
    NewPortalDef(world.SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.GRAND_ABYSS_MREA, "VirtualNorth"),
    NewPortalDef(world.SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.AERIE_MREA, "VirtualArenaDock"),
    NewPortalDef(world.SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.HIVE_SUMMIT_MREA, "VirtualUnderStatueDock"),
    NewPortalDef(world.AGON_WASTES_MLVL, agon_wastes.MINING_PLAZA_MREA, "VirtualDock"),
    NewPortalDef(world.AGON_WASTES_MLVL, agon_wastes.CROSSROADS_MREA, "VirtualNorth"),
    NewPortalDef(world.AGON_WASTES_MLVL, agon_wastes.MAIN_REACTOR_MREA, "VirtualEast"),
    NewPortalDef(world.AGON_WASTES_MLVL, agon_wastes.DOOMED_ENTRY_MREA, "VirtualNorth"),
    NewPortalDef(world.TEMPLE_GROUNDS_MLVL, temple_grounds.PATH_OF_EYES_MREA, "VirtualNorth"),
]


@decorate_patcher(world.AGON_WASTES_MLVL, agon_wastes.MAIN_REACTOR_MREA)
def adjust_main_reactor_portal_spawn(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    area.move_instance(area.get_instance("Arrival"), "Default")

    with area.get_instance("Arrival").edit_properties(SpawnPoint) as prop:
        prop.editor_properties.transform.position.y = 83


@decorate_patcher(world.AGON_WASTES_MLVL, agon_wastes.DUELLING_RANGE_MREA)
def adjust_duelling_range_portal_spawn(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    spawn = area.get_layer("Default").add_instance_with(
        SpawnPoint(
            editor_properties=EditorProperties(
                name="Arrival",
                transform=Transform(
                    position=Vector(-326, 8, -14.23),
                ),
            )
        )
    )
    area.get_instance("VirtualDock").add_connection(State.MaxReached, Message.Activate, spawn)


@decorate_patcher(world.AGON_WASTES_MLVL, agon_wastes.DARK_OASIS_MREA)
def adjust_dark_oasis_portal_spawn(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    spawn = area.get_layer("Default").add_instance_with(
        SpawnPoint(
            editor_properties=EditorProperties(
                name="Arrival",
                transform=Transform(
                    position=Vector(417.814056, 83, 19.031952),
                    rotation=Vector(0, 0, 180),
                ),
            )
        )
    )
    area.get_instance("VirtualEast").add_connection(State.MaxReached, Message.Activate, spawn)


def register_make_portals_two_way(area_patcher: AreaPatcher, map_visibility: MapVisibility) -> None:
    """
    Adds a new portal to every virtual dock that is on the other side of a one-way portal.
    """

    area_patcher.add_function(adjust_main_reactor_portal_spawn)
    area_patcher.add_function(adjust_duelling_range_portal_spawn)
    area_patcher.add_function(adjust_dark_oasis_portal_spawn)

    for portal_def in _NEW_PORTALS:
        area_patcher.add_raw_function(
            portal_def.mlvl_id,
            portal_def.mrea_id,
            functools.partial(
                add_portal_to,
                dock_name=portal_def.dock_name,
                map_icon_visibility=ObjectVisibility.AreaVisitOrMapStation
                if map_visibility.unvisited_map_icons
                else ObjectVisibility.AreaVisitOrMapStation2,
            ),
        )


def _find_dock_named(area: Area, name: str) -> tuple[ScriptInstance, Dock]:
    for instance in area.all_instances:
        if instance.script_type == Dock and instance.name == name:
            return instance, instance.get_properties_as(Dock)
    raise KeyError(name)


def _duplicate_and_edit_scan_string(
    editor: PatcherEditor,
    asset_name_base: str,
    scan_poi: ScriptInstance,
    string_index: int,
    new_string_text: str,
) -> None:
    with scan_poi.edit_properties(PointOfInterest) as prop:
        new_scan_id = editor.duplicate_asset(prop.scan_info.scannable_info0, f"{asset_name_base}.SCAN")
        prop.scan_info.scannable_info0 = new_scan_id

        new_scan = editor.get_file(new_scan_id, Scan)
        with new_scan.scannable_object_info.edit_properties(ScannableObjectInfo) as info:
            info.string = editor.duplicate_asset(info.string, f"{asset_name_base}.STRG")
            editor.get_file(info.string, Strg).set_single_string(string_index, new_string_text)


def _adjust_rift_scan(
    editor: PatcherEditor,
    area: Area,
    scan_poi: ScriptInstance,
    change: PortalChange,
) -> None:
    """
    Edits the scan of the inactive rift to point to the direction.

    Does not work with scan portals.
    """
    _duplicate_and_edit_scan_string(
        editor,
        f"PortalScan_{area.mrea_asset_id}_{change.source_dock_name}",
        scan_poi,
        0,
        f"This rift portal to &push;&main-color=#FF3333;{change.portal_scan_destination}&pop; is inactive.",
    )


def _adjust_scan_portal_scan(
    editor: PatcherEditor,
    area: Area,
    all_objects: dict[InstanceId, ScriptInstance],
    change: PortalChange,
) -> None:
    color_target = f"&push;&main-color=#FF3333;{change.portal_scan_destination}&pop;"

    _duplicate_and_edit_scan_string(
        editor,
        f"PortalScanActive_{area.mrea_asset_id}_{change.source_dock_name}",
        _find_object_with_name("Portal Activated", all_objects.values()),
        1,
        f"Console used to energize and open a portal to {color_target}, currently online.\n\n"
        "Portal generation system initiated.",
    )

    _duplicate_and_edit_scan_string(
        editor,
        f"PortalScanInactive_{area.mrea_asset_id}_{change.source_dock_name}",
        _find_object_with_name("Portal Inactive", all_objects.values()),
        1,
        f"Console used to energize and open a portal to {color_target}, currently offline.\n\n"
        "Restore power to the system to enable portal creation.",
    )


def apply_portal_change(
    editor: PatcherEditor,
    mlvl: Mlvl,
    area: Area,
    change: PortalChange,
) -> None:
    """Change the portal the given portal is connected to."""

    dock_instance, source_dock = _find_dock_named(area, change.source_dock_name)
    target_area = area.parent_mlvl.get_area(change.target_mrea_id)
    _, target_dock = _find_dock_named(target_area, change.target_dock_name)

    area._raw_connect_to(
        source_dock.dock_number,
        target_area,
        target_dock.dock_number,
    )

    all_objs = area_utils.get_all_ids_related_to(
        area,
        dock_instance.id,
    )
    try:
        scan_poi = _find_object_with_name("RIFT Portal Scan", all_objs.values())
    except KeyError:
        scan_poi = None

    if area.mrea_asset_id == PORTAL_TERMINAL_MREA:
        # TODO: deactivate the auto-warp after scanning the portal the first time
        pass

    if scan_poi is not None:
        _adjust_rift_scan(editor, area, scan_poi, change)
    else:
        _adjust_scan_portal_scan(editor, area, all_objs, change)
