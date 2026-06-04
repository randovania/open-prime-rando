from __future__ import annotations

from typing import TYPE_CHECKING

from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.properties.echoes.archetypes.Connection import Connection as SequenceConnection
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.LayerSwitch import LayerSwitch
from retro_data_structures.properties.echoes.archetypes.Transform import Transform
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects import (
    Relay,
    ScriptLayerController,
    SequenceTimer,
)

from open_prime_rando.area_patcher import decorate_patcher
from open_prime_rando.echoes.asset_ids import sanctuary_fortress
from open_prime_rando.echoes.asset_ids.world import (
    SANCTUARY_FORTRESS_MLVL,
)

if TYPE_CHECKING:
    from retro_data_structures.formats.mlvl import Mlvl
    from retro_data_structures.formats.mrea import Area

    from open_prime_rando.patcher_editor import PatcherEditor


@decorate_patcher(SANCTUARY_FORTRESS_MLVL, sanctuary_fortress.SANCTUARY_ENTRANCE_MREA)
def sanctuary_entrance_dynamic_layer_loading(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Dynamically loads "Post-Intro Cinematic" after
    battling the commandos, then adjust scripting
    accordingly to compensate for the changes.
    (non-dynamic layer change remains in case
    player performs DLC)
    """

    default = area.get_layer("Default")

    # Move Phazon Crates to a dedicated layer so
    # 1st Pass can be Decremented Dynamically
    phazon_crates = area.add_layer("Phazon Crates")

    for first_pass_instances in _MOVE_TO_PHAZON_CRATES:
        area.move_instance(first_pass_instances, "Phazon Crates")

    # Phazon Crates layer controller
    phazon_crates_controller = default.add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(
                name="Decrement Phazon Crates",
                transform=Transform(position=Vector(61.9, -248.1, -152.1), scale=Vector(2.0, 2.0, 2.0)),
            ),
            layer=LayerSwitch(
                area_id=sanctuary_fortress.SANCTUARY_ENTRANCE_INTERNAL_ID,
                layer_number=phazon_crates.index,
            ),
        )
    )

    # Post-Intro Cinematic layer controller
    post_intro_controller = default.add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(
                name="Increment Post Intro Cinematic Layer (Dynamic)",
                transform=Transform(position=Vector(65.2, -248.1, -151.0), scale=Vector(2.0, 2.0, 2.0)),
            ),
            layer=LayerSwitch(
                area_id=sanctuary_fortress.SANCTUARY_ENTRANCE_INTERNAL_ID,
                layer_number=area.get_layer("Post-Intro Cinematic").index,
            ),
            is_dynamic=True,
        )
    )

    # Repurpose existing redundant Dynamic 1st Pass
    # Increment layer controller and remove increment
    # elements (Layer is already active)
    area.remove_instance("Timer 003")

    first_pass_controller = area.get_instance("Increment 1st Pass")
    first_pass_controller.remove_connection(first_pass_controller.connections[0])
    with first_pass_controller.edit_properties(ScriptLayerController) as layer_switch_props:
        layer_switch_props.editor_properties.name = "Decrement 1st Pass (Dynamic)"
        layer_switch_props.is_dynamic = True

    intro_end_layer_change_relay = area.get_instance("Decrement Intro Cinematic and Swap Music in 0A_Cliff_Hall")
    intro_end_layer_change_relay.remove_connection(intro_end_layer_change_relay.connections[1])

    # Decrement Phazon Crates, Unload 1st Pass, Load Post-Intro Cinematic
    area.get_instance("Swap 1st to 2nd Pass").add_connection(State.Zero, Message.Decrement, phazon_crates_controller)

    door_opening_sequence_timer = area.get_instance("Door opening cut")
    with door_opening_sequence_timer.edit_properties(SequenceTimer) as sequence_timer:
        sequence_timer.sequence_connections.append(
            SequenceConnection(
                connection_index=6,
                activation_times=[3.00],
            ),
        )
        sequence_timer.sequence_connections.append(
            SequenceConnection(
                connection_index=7,
                activation_times=[3.00],
            )
        )
    door_opening_sequence_timer.add_connection(State.Sequence, Message.Decrement, first_pass_controller)
    door_opening_sequence_timer.add_connection(State.Sequence, Message.Increment, post_intro_controller)
    post_intro_controller.add_connection(State.Arrived, Message.Play, post_intro_controller)

    # Use this relay as a surrogate, to automatically enable the cannon
    # when the layer is loaded if the panel was scanned already
    check_elevator_relay = default.add_instance_with(
        Relay(
            editor_properties=EditorProperties(
                name="Cannon activated Check",
                transform=Transform(position=Vector(36.5, -110.3, -140.4), scale=Vector(2.0, 2.0, 2.0)),
                active=False,
            ),
        )
    )
    memory_relay = area.get_instance("Memory Relay - dim scan holo")
    memory_relay.add_connection(State.Active, Message.Activate, check_elevator_relay)
    post_intro_controller.add_connection(State.Arrived, Message.SetToZero, check_elevator_relay)
    check_elevator_relay.add_connection(State.Zero, Message.Activate, memory_relay)


_MOVE_TO_PHAZON_CRATES = [
    0x201F9,  # Exploding Crate
    0x201FC,  # Exploding Crate
    0x201FB,  # Exploding Crate_Lean
    0x201C7,  # Light Damage to Enemies
    0x201FA,  # Light Damage to Enemies
    0x20221,  # Light Damage to Enemies
    0x2036F,  # Blowback
    0x20370,  # Blowback
    0x20371,  # Blowback
    0x20379,  # Crate Stay Away
    0x2037A,  # Crate Stay Away
    0x2037B,  # Crate Stay Away
    0x2038A,  # BLOW CRATE
]
