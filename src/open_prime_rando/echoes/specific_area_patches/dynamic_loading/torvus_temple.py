from __future__ import annotations

from typing import TYPE_CHECKING

from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.LayerSwitch import LayerSwitch
from retro_data_structures.properties.echoes.archetypes.Transform import Transform
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects import (
    Relay,
    ScriptLayerController,
)

from open_prime_rando.area_patcher import decorate_patcher
from open_prime_rando.echoes.asset_ids import torvus_bog
from open_prime_rando.echoes.asset_ids.world import (
    TORVUS_BOG_MLVL,
)

if TYPE_CHECKING:
    from retro_data_structures.formats.mlvl import Mlvl
    from retro_data_structures.formats.mrea import Area

    from open_prime_rando.patcher_editor import PatcherEditor


@decorate_patcher(TORVUS_BOG_MLVL, torvus_bog.TORVUS_TEMPLE_MREA)
def torvus_temple_second_pass(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Activate the second pass after collecting the pickup. The Shriekers are moved
    to a new layer, activated non-dynamically, as a courtesy to the player. The
    central elevator and the rest of the second pass layer are activated dynamically.
    """

    _patch_elevator(editor, mlvl, area)
    _patch_shriekers(editor, mlvl, area)
    _patch_music(editor, mlvl, area)


def _patch_elevator(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    default = area.get_layer("Default")
    second_pass = area.get_layer("2nd PAss")  # [sic]

    # add layer controller for elevator
    elevator_layer_controller = default.add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(
                name="Increment - 2nd PAss (Dynamic)",
                transform=Transform(
                    position=Vector(-62.5, -185.0, 46.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            layer=LayerSwitch(
                area_id=torvus_bog.TORVUS_TEMPLE_INTERNAL_ID,
                layer_number=second_pass.index,
            ),
            is_dynamic=True,
        )
    )

    # start loading the layer when pickup is collected
    area.get_instance("Post Pickup").add_connection(State.Zero, Message.Increment, elevator_layer_controller)

    # activate the layer immediately once it's been loaded
    elevator_layer_controller.add_connection(State.Arrived, Message.Play, elevator_layer_controller)

    # use this relay as a surrogate, to automatically enable the elevator
    # when the layer is loaded if the hologram was scanned already
    check_elevator_relay = default.add_instance_with(
        Relay(
            editor_properties=EditorProperties(
                name="Check if central elevator is active",
                transform=Transform(
                    position=Vector(-158.3, -129.1, 48.1),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
                active=False,
            ),
        )
    )
    area.get_instance("Remember Central Elevator Active").add_connection(
        State.Active, Message.Activate, check_elevator_relay
    )
    area.get_instance("[IN] Switch Luminoth Hologram To Elevator").add_connection(
        State.Zero, Message.Activate, check_elevator_relay
    )
    check_elevator_relay.add_connection(
        State.Zero, Message.Activate, area.get_instance("OcclusionRelay - Enable Elevator")
    )
    elevator_layer_controller.add_connection(State.Arrived, Message.SetToZero, check_elevator_relay)

    # Move waypoints and holograms to the Default layer
    # so elevator components connect properly
    instances = (
        second_pass.get_instance("Top"),
        second_pass.get_instance("Bottom"),
        second_pass.get_instance(0x1B040C),  # Elevator Holo
        second_pass.get_instance(0x1B03F7),  # Key Beam
    )
    for instance in instances:
        area.move_instance(instance, "Default")


def _patch_shriekers(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    # add new layer
    shrieker_layer = area.add_layer("Shriekers", False)

    # move shrieker instances to new layer
    second_pass = area.get_layer("2nd PAss")  # [sic]
    to_move = [
        second_pass.get_instance("Generator 001"),
        *second_pass.get_all_instances_with_name("ShriekerBuried"),
    ]

    for instance in to_move:
        area.move_instance(instance, "Shriekers")

    # add layer controller for elevator
    shrieker_layer_controller = area.get_layer("Default").add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(
                name="Increment - Shriekers",
                transform=Transform(
                    position=Vector(-62.5, -183.5, 46.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            layer=LayerSwitch(
                area_id=torvus_bog.TORVUS_TEMPLE_INTERNAL_ID,
                layer_number=shrieker_layer.index,
            ),
        )
    )

    # activate the layer when pickup is collected
    area.get_instance("Post Pickup").add_connection(State.Zero, Message.Increment, shrieker_layer_controller)


def _patch_music(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    # Prevent music interrupts caused by dynamic layer
    # loading by adding relay checks
    default = area.get_layer("Default")

    # Move music player to Default
    area.move_instance("Music Player For Area", "Default")
    area.move_instance("Swamp World", "Default")

    # Add relays to decide which music will play based on room state
    swamp_world_relay = default.add_instance_with(
        Relay(
            editor_properties=EditorProperties(
                name="Play Swamp World",
                transform=Transform(
                    position=Vector(-92.5, -124.8, 47.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            )
        )
    )

    pirate_encounter_relay = default.add_instance_with(
        Relay(
            editor_properties=EditorProperties(
                name="Play Pirate Encounter",
                transform=Transform(
                    position=Vector(-92.5, -124.8, 46.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
                active=False,
            )
        )
    )

    pirate_encounter_finale_relay = default.add_instance_with(
        Relay(
            editor_properties=EditorProperties(
                name="Play Pirate Encounter Finale",
                transform=Transform(
                    position=Vector(-88.8, -124.8, 46.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
                active=False,
            )
        )
    )

    # Rewire Music Player connections
    music_player = area.get_instance("Music Player For Area")
    swamp_world = area.get_instance("Swamp World")
    pirate_encounter = area.get_instance("Pirate Encounter")
    pirate_encounter_finale = area.get_instance("Pirate Encounter Finale")
    music_player.remove_connection(music_player.connections[0])
    music_player.add_connection(State.Entered, Message.SetToZero, swamp_world_relay)
    music_player.add_connection(State.Entered, Message.SetToZero, pirate_encounter_relay)
    music_player.add_connection(State.Entered, Message.SetToZero, pirate_encounter_finale_relay)

    # Relay connections to music
    swamp_world_relay.add_connection(State.Zero, Message.Play, swamp_world)
    pirate_encounter_relay.add_connection(State.Zero, Message.Play, pirate_encounter)
    pirate_encounter_finale_relay.add_connection(State.Zero, Message.Play, pirate_encounter_finale)

    # Update music depending on room state
    pirate_trigger = area.get_instance("Trigger Skiff Flyby")
    barrier_cine_start = area.get_instance("[IN] Start Barriers Off Cinematic")
    pirate_trigger.add_connection(State.Entered, Message.Deactivate, swamp_world_relay)
    pirate_trigger.add_connection(State.Entered, Message.Activate, pirate_encounter_relay)
    barrier_cine_start.add_connection(State.Zero, Message.Deactivate, pirate_encounter_relay)
    barrier_cine_start.add_connection(State.Zero, Message.Activate, pirate_encounter_finale_relay)
