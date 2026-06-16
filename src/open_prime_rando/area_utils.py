from __future__ import annotations

import collections
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from retro_data_structures.formats.mrea import Area
    from retro_data_structures.formats.script_object import InstanceId, ScriptInstance
    from retro_data_structures.properties import BaseObjectType


def get_all_ids_related_to(
    area: Area,
    target: InstanceId,
    stop_at_types: set[type[BaseObjectType]] | None = None,
) -> dict[InstanceId, ScriptInstance]:
    """
    Gets all object ids that send a message to, or receives a message from the target object, or any object involved.
    """

    if stop_at_types is None:
        stop_at_types = set()
    obj_conn_to: dict[InstanceId, set[InstanceId]] = collections.defaultdict(set)

    for instance in area.all_instances:
        for conn in instance.connections:
            obj_conn_to[conn.target].add(instance.id)

    related_objects = {}

    def add_related_objs(t_id: InstanceId, depth: int) -> None:
        if t_id in related_objects:
            return

        try:
            obj = area.get_instance(t_id)
        except KeyError:
            # An object was deleted and left connections behind.
            return
        related_objects[t_id] = obj

        # print("  " * depth + f"({obj.id}) [{obj.script_type.__name__}] {obj.name}")
        if obj.script_type in stop_at_types:
            return

        for c in obj.connections:
            add_related_objs(c.target, depth + 1)
        for c in obj_conn_to[t_id]:
            add_related_objs(c, depth + 1)

    add_related_objs(target, 0)

    return related_objects
