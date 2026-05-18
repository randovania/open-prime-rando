from __future__ import annotations

from typing import TYPE_CHECKING

from retro_data_structures.enums.echoes import Message, State
from retro_data_structures.formats.script_object import Connection
from retro_data_structures.properties.echoes.archetypes.Connection import Connection as SequenceConnection
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.LayerSwitch import LayerSwitch
from retro_data_structures.properties.echoes.archetypes.Transform import Transform
from retro_data_structures.properties.echoes.core.Vector import Vector
from retro_data_structures.properties.echoes.objects import (
    Counter,
    MemoryRelay,
    ScriptLayerController,
    SequenceTimer,
    Switch,
    Timer,
    Trigger,
)

from open_prime_rando.area_patcher import decorate_patcher
from open_prime_rando.echoes.asset_ids import agon_wastes
from open_prime_rando.echoes.asset_ids.world import (
    AGON_WASTES_MLVL,
)

if TYPE_CHECKING:
    from retro_data_structures.formats.mlvl import Mlvl
    from retro_data_structures.formats.mrea import Area

    from open_prime_rando.patcher_editor import PatcherEditor


@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.MAIN_REACTOR_MREA)
def main_reactor_dynamic_layer_loading(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Dynamically loads/unloads layers so a room reload
    is not necesary after battling Dark Samus, then adjust
    scripting accordingly to compensate for the changes.
    """

    # Add new layer just for some DS Death effects
    ds_death_particle_layer = area.add_layer("Dark Samus Death Particles", active=False)

    # Move effect objects to new layer because their
    # origin layer now gets Dynamically unloaded
    for instances in (0x2E04AE, 0x2E0027, 0x2E001D, 0x2E0368, 0x2E039A, 0x2E04AD, 0x2E04AC, 0x2E0353):
        area.move_instance(instances, "Dark Samus Death Particles")

    # Particles Layer Dynamic controller
    ds_particles_dynamic_layer_controller = area.get_layer("Default").add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(
                name="Increment / Decrement Dark Samus Floating Particles (Dynamic)",
                transform=Transform(
                    position=Vector(436.5, 70.0, 4.3),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            layer=LayerSwitch(
                area_id=agon_wastes.MAIN_REACTOR_INTERNAL_ID,
                layer_number=ds_death_particle_layer.index,  # Dark Samus Death Particles
            ),
            is_dynamic=True,
        )
    )

    # non-dynamic controller that gets decremented immediately
    ds_particles_layer_controller = area.get_layer("Default").add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(
                name="Decrement Dark Samus Floating Particles (non-dynamic for player leaving room early)",
                transform=Transform(
                    position=Vector(436.5, 70.0, 5.3),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            layer=LayerSwitch(
                area_id=agon_wastes.MAIN_REACTOR_INTERNAL_ID,
                layer_number=ds_death_particle_layer.index,  # Dark Samus Death Particles
            ),
        )
    )

    # Counter to now Play this controller alongside the existing controller
    death_and_particles_counter = area.get_layer("Default").add_instance_with(
        Counter(
            editor_properties=EditorProperties(
                name="Layers Loaded",
                transform=Transform(
                    position=Vector(437.5, 66.7, 5.3),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            initial_count=0,
            max_count=2,
        )
    )

    # Timer to unload particles layer when the effects are fully done playing
    decrement_particles_layer_timer = area.get_layer("Default").add_instance_with(
        Timer(
            editor_properties=EditorProperties(
                name="Decrement Particles Layer",
                transform=Transform(
                    position=Vector(391.0, 89.0, 11.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            time=25.02,
        )
    )

    # Since Post-Dark Samus layer now get activated Dynamically, their
    # music players automatically play Pirate Encounter, overwritting
    # Boss Go playing, so we are rewiring those connections to a Switch
    # in the Default layer that decides when music plays

    # Trigger that changes the music Switch status,
    # It's placed exactly where the Storage D Pickup is
    music_change_trigger = area.get_layer("Default").add_instance_with(
        Trigger(
            editor_properties=EditorProperties(
                name="Open Pirate Encounter",
                transform=Transform(
                    position=Vector(340.610992, 73.113937, 23.076834),
                    scale=Vector(1.0, 1.0, 2.0),
                ),
                active=False,
            ),
            deactivate_on_enter=True,
        )
    )
    post_ds_music_switch = area.get_layer("Default").add_instance_with(
        Switch(
            editor_properties=EditorProperties(
                name="OPEN: Pirate Encounter / CLOSED: Boss Go",
                transform=Transform(
                    position=Vector(427.0, 77.0, 4.0),
                    scale=Vector(2.0, 2.0, 2.0),
                ),
            ),
            is_open=True,
        )
    )

    # Define existing objects
    layer_loading_sequence_timer = area.get_instance("Unload Intro, Load Death, Fire Death Load Check")
    dark_samus = area.get_instance("DarkSamus 001")
    start_death_cinema_relay = area.get_instance("[IN] Start Death Cinema")
    layer_switch_relay = area.get_instance("Switch Layers To Post-Dark Samus")
    ds_layer_load_switch = area.get_instance("Check for Dark Samus Death Cinema Load")
    end_death_cinema_relay = area.get_instance("[OUT] End Death Cinema")
    pirate_encounter_music_player = area.get_instance("Music Player For Area (pirate encounter)")
    pirate_encounter_sAudio = area.get_instance("Pirate Encounter Finale")
    boss_go_sAudio = area.get_instance("Boss Go")
    death_cinema_increment_layer_switch = area.get_instance("Increment Dark Samus Death Cinema (Dynamic)")
    death_cinema_decrement_layer_switch = area.get_instance("Decrement Dark Samus Death Cinema (Dynamic)")

    # Move StreamedAudio to Default
    area.move_instance("Boss Go", "Default")

    # Change room layer controllers to be Dynamic
    post_ds_layer_switch = area.get_instance(0x2E0334)
    war_chest_layer_switch = area.get_instance(0x2E04AA)
    ds_dec_layer_switch = area.get_instance(0x2E002D)

    for layer_switch in (post_ds_layer_switch, war_chest_layer_switch, ds_dec_layer_switch):
        with layer_switch.edit_properties(ScriptLayerController) as layer_switch_props:
            layer_switch_props.editor_properties.name += " (Dynamic)"
            layer_switch_props.is_dynamic = True

    # Since layers get activated Dynamically, make Memory Relays activate immediately
    ds_music_memory_relay = area.get_instance("Post Dark Samus Battle Music Setup")
    post_ds_memory_relay = area.get_instance("SWITCH TO POST-DARK SAMUS STATE (NON-LAYER ITEMS)")

    for memory_relays in (ds_music_memory_relay, post_ds_memory_relay):
        with memory_relays.edit_properties(MemoryRelay) as memory_relay_props:
            memory_relay_props.delayed_action = False

    # Remove connection to Switch as the Counter will now take care of the load check
    death_cinema_increment_layer_switch.remove_connection(death_cinema_increment_layer_switch.connections[0])

    # Don't make Dark Samus death switch layers immediately
    dark_samus.remove_connection(dark_samus.connections[7])

    # Remove controller connections because now they're at the end of cutscene
    layer_switch_connections = list(layer_switch_relay.connections)
    layer_switch_relay.remove_connection(layer_switch_connections[1])
    layer_switch_relay.remove_connection(layer_switch_connections[2])

    # Instead of playing music directly, close Switch
    death_cinema_relay_connections = list(end_death_cinema_relay.connections)
    death_cinema_relay_connections[4] = Connection(State.Zero, Message.Close, post_ds_music_switch.id)
    end_death_cinema_relay.connections = death_cinema_relay_connections
    end_death_cinema_relay.remove_connection(end_death_cinema_relay.connections[1])

    # Start loading Particles layer after DS Intro is done, add
    # new connection from SequenceTimer to layer controller
    with layer_loading_sequence_timer.edit_properties(SequenceTimer) as sequence_timer:
        sequence_timer.editor_properties.name = (
            "Unload Intro, Load Death + Particles, Fire Death and Particles Load Check"
        )
        sequence_timer.sequence_connections.append(
            SequenceConnection(
                connection_index=3,
                activation_times=[0.02],
            ),
        )
    layer_loading_sequence_timer.add_connection(
        State.Sequence, Message.Increment, ds_particles_dynamic_layer_controller
    )

    # Remove direct message to StreamedAudio because it's going to Switch now
    pirate_encounter_music_player.remove_connection(pirate_encounter_music_player.connections[0])

    # Music Player connection to Switch
    pirate_encounter_music_player.add_connection(State.Entered, Message.SetToZero, post_ds_music_switch)

    # Storage D trigger changes Switch back to Pirate Encounter
    music_change_trigger.add_connection(State.Entered, Message.Open, post_ds_music_switch)

    # Switch music controls
    post_ds_music_switch.add_connection(State.Open, Message.Play, pirate_encounter_sAudio)
    post_ds_music_switch.add_connection(State.Closed, Message.Play, boss_go_sAudio)

    # Make layer switch happen on cinema start instead
    start_death_cinema_relay.add_connection(State.Zero, Message.SetToZero, layer_switch_relay)

    # Once particles are done, decrement layer
    decrement_particles_layer_timer.add_connection(State.Zero, Message.Decrement, ds_particles_dynamic_layer_controller)

    # Controllers increment counter when done loading
    death_cinema_increment_layer_switch.add_connection(State.Arrived, Message.Increment, death_and_particles_counter)
    ds_particles_dynamic_layer_controller.add_connection(State.Arrived, Message.Increment, death_and_particles_counter)

    # Then counter opens the layer check switch
    death_and_particles_counter.add_connection(State.MaxReached, Message.Open, ds_layer_load_switch)

    # Switch now sends Play to both
    ds_layer_load_switch.add_connection(State.Open, Message.Play, ds_particles_dynamic_layer_controller)

    # Connections for Dynamic Layer Loading at the end of death cinema
    end_death_cinema_relay.add_connection(State.Zero, Message.Start, decrement_particles_layer_timer)
    end_death_cinema_relay.add_connection(State.Zero, Message.Decrement, death_cinema_decrement_layer_switch)
    end_death_cinema_relay.add_connection(State.Zero, Message.Decrement, ds_dec_layer_switch)
    end_death_cinema_relay.add_connection(State.Zero, Message.Decrement, ds_particles_layer_controller)
    end_death_cinema_relay.add_connection(State.Zero, Message.Play, post_ds_layer_switch)
    end_death_cinema_relay.add_connection(State.Zero, Message.Play, war_chest_layer_switch)
    end_death_cinema_relay.add_connection(State.Zero, Message.Activate, post_ds_memory_relay)
    end_death_cinema_relay.add_connection(State.Zero, Message.Activate, music_change_trigger)


# FIXME: make change in RDV instead
@decorate_patcher(AGON_WASTES_MLVL, agon_wastes.STORAGE_D_MREA)
def storage_d_room_reload(editor: PatcherEditor, mlvl: Mlvl, area: Area) -> None:
    """
    Remove room reload upon grabbing pickup.
    """
    dark_beam_relay = area.get_instance("[IN] Start Dark Beam Attainment")
    dark_beam_relay.remove_connection(dark_beam_relay.connections[0])
