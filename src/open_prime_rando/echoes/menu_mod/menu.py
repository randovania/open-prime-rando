from open_prime_rando.echoes.asset_ids.world import NAME_TO_ID_MLVL
from open_prime_rando.patcher_editor import PatcherEditor
from open_prime_rando.echoes.vulnerabilities import resist_all_vuln

from construct import Container
from retro_data_structures.formats.mrea import (
    Area,
)
from retro_data_structures.properties.echoes.archetypes import (
    EditorProperties,
    ControllerActionStruct,
    Transform,
    LayerSwitch,
    ActorParameters,
    VisorParameters,
    TextProperties,
)
from retro_data_structures.properties.echoes.objects import (
    SpecialFunction,
    ControllerAction,
    AdvancedCounter,
    Switch,
    Timer,
    Dock,
    Relay,
    ScriptLayerController,
    Door,
    GuiMenu,
    GuiWidget,
    TextPane,
    ColorModulate,
    WorldTeleporter,
    MemoryRelay,
)
from retro_data_structures.properties.echoes.core import Vector, AnimationParameters, Color, Spline
from retro_data_structures.enums.echoes import Function, State, Message, VisorFlags
from retro_data_structures.formats.strg import Strg


TEXT_PANE_TEXT_PROPERTIES = TextProperties(
    text_bounding_width=15,
    text_bounding_height=15,
    foreground_color=Color(a=1.0),
    outline_color=Color(a=1.0),
    geometry_color=Color(a=1.0),
    default_font=227804281,
    wrap_text=False,
)


def create_color_modulate(
    name: str,
    color_a: Color = Color(0.5882353186607361, 0.5882353186607361, 0.5882353186607361, 1.0),
    color_b: Color = Color(1.0),
) -> ColorModulate:
    return ColorModulate(
        editor_properties=EditorProperties(name=f"{name} ColorModulate", unknown=0),
        color_a=color_a,
        color_b=color_b,
        time_a2_b=0.0,
        time_b2_a=0.0,
        control_spline=Spline(
            maximum_amplitude=1.0,
            clamp_mode=1,
        ),
    )


def add_area_elements(area: Area, menu_area: Area) -> None:
    string_table: Strg

    # Connect the area to the Menu
    area._raw.docks.append(Container(
        connecting_dock=[
            Container(
                area_index=menu_area.id, dock_index=0,
            ),
        ],
        dock_coordinates=[
            [0, 0, 0],
            [0, 5, 0],
            [5, 0, 0],
            [5, 5, 0],
        ],
    ))
    menu_area._raw.docks[0].connecting_dock.append(Container(
        area_index=area.id, dock_index=len(area._raw.docks) - 1,
    ))

    loader_layer = area.add_layer("Menu - Loader", active=False)

    # 13970313
    enable_controller = loader_layer.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(name="Player In Area Relay - Enable ControllerAction", unknown=0),
            function=Function.PlayerInAreaRelay,
        )
    )
    # 13970314
    check_for_dpad = loader_layer.add_instance_with(
        ControllerAction(
            editor_properties=EditorProperties(name="Check for D-Pad Up press"),
            controller_action_struct=ControllerActionStruct(command=58),
            one_shot=False,
        )
    )
    # 13970315
    dpad_count = loader_layer.add_instance_with(
        AdvancedCounter(
            editor_properties=EditorProperties(name="Count D-Pad Up presses", unknown=0),
            max_count=4,
        )
    )
    # 13970316
    load_menu = loader_layer.add_instance_with(
        Switch(
            editor_properties=EditorProperties(name="Load Menu", unknown=0),
            is_open=True,
        )
    )
    # 13970317
    reset_dpad_counter = loader_layer.add_instance_with(
        Timer(
            editor_properties=EditorProperties(name="Reset Counter if D-Pad not pressed quickly enough", unknown=0),
            time=0.5,
        )
    )
    # 13970318
    stop_quick_counter = loader_layer.add_instance_with(
        Timer(
            editor_properties=EditorProperties(
                name="Stop Counter increasing TOO quickly (cutscene skip workaround)", unknown=0
            ),
            time=0.1,
        )
    )

    # 13970319
    menu_dock = loader_layer.add_instance_with(
        Dock(
            editor_properties=EditorProperties(
                name="Menu Dock", transform=Transform(position=Vector(100000.0, 100000.0, 100000.0))
            ),
            # TODO: these are likely area-dependent
            dock_number=1,
            area_number=0,
            load_connected_immediate=False,
        )
    )

    # Exit Menu
    exit_menu_relay = loader_layer.add_instance_with(
        Relay(
            editor_properties=EditorProperties(
                name="Exit Menu"
            ),
            one_shot=False,
        )
    )
    # TODO: use a static id so the menu can connect to it


    enable_controller.add_connection(State.Entered, Message.Activate, check_for_dpad)
    enable_controller.add_connection(State.Exited, Message.Deactivate, check_for_dpad)
    check_for_dpad.add_connection(State.Open, Message.Increment, dpad_count)
    load_menu.add_connection(State.Open, Message.Deactivate, check_for_dpad)
    dpad_count.add_connection(State.InternalState00, Message.Deactivate, load_menu)
    dpad_count.add_connection(State.MaxReached, Message.SetToZero, load_menu)
    reset_dpad_counter.add_connection(State.Zero, Message.Reset, dpad_count)
    dpad_count.add_connection(State.Open, Message.ResetAndStart, reset_dpad_counter)
    dpad_count.add_connection(State.InternalState00, Message.ResetAndStart, stop_quick_counter)
    stop_quick_counter.add_connection(State.Zero, Message.Activate, load_menu)
    menu_dock.add_connection(State.MaxReached, Message.Increment, menu_dock)
    exit_menu_relay.add_connection(State.Zero, Message.Deactivate, CSettings.CameraID)
    exit_menu_relay.add_connection(State.Zero, Message.SetToZero, menu_dock)
    exit_menu_relay.add_connection(State.Zero, Message.Activate, check_for_dpad)

    # Layer Menu ScriptLayerController
    # Layer Menu Relay

    load_loader_layer = area.add_layer("Menu - Load Loader", active=True)

    # 13970320
    load_dock_layer = load_loader_layer.add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(name="Load Dock Layer", unknown=0),
            layer=LayerSwitch(
                area_id=area.id,
                layer_number=loader_layer.index,
            ),
            is_dynamic=True,
        )
    )
    load_dock_layer.add_connection(State.Arrived, Message.Play, load_dock_layer)
    load_dock_layer.add_connection(State.Arrived, Message.Decrement, load_dock_layer)

    # 13970321
    increment_load_loader = load_loader_layer.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(name="Increment Load Loader", unknown=0),
            function=Function.PlayerInAreaRelay,
        )
    )
    increment_load_loader.add_connection(State.Entered, Message.Increment, load_dock_layer)
    increment_load_loader.add_connection(State.Entered, Message.Deactivate, increment_load_loader)

    # 13970322
    disable_loading = load_loader_layer.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(name="Disable Loading", unknown=0),
            function=Function.AreaAutoLoadController,
        )
    )
    load_menu.add_connection(State.Open, Message.Stop, disable_loading)

    # 13970323
    door_to_menu_dock = load_loader_layer.add_instance_with(
        Door(
            editor_properties=EditorProperties(
                name="Disable Loading",
                transform=Transform(position=Vector(100000.0, 100000.0, 100000.0)),
            ),
            collision_box=Vector(0.35, 5.0, 4.0),
            collision_offset=(-0.175, 0.0, 2.0),
            vulnerability=resist_all_vuln,
            animation_information=AnimationParameters(ancs=0xCEB091F7, initial_anim=0xFFFFFFFF),
            actor_information=ActorParameters(
                visor=VisorParameters(scan_through=True, visor_flags=VisorFlags(0)),
                unknown_0xcd4c81a1=True,
                force_render_unsorted=True,
                unknown_0xf07981e8=True,
                unknown_0x6df33845=True,
            ),
            is_open=False,
            close_delay=0.25,
        )
    )
    door_to_menu_dock.add_connection(State.Closed, Message.Decrement, menu_dock)
    door_to_menu_dock.add_connection(State.Open, Message.Increment, menu_dock)

    # 13970324 Switch Layer 2

    layer_switch_layer = area.add_layer("Menu - Layer Switch Layer", active=False)

    for layer in area.layers:
        # Skip `Default` and `!No Load`, as well as our own layers
        if layer.index < 2 or layer.name.startswith("Menu - "):
            continue

        # 13970324
        switch_layer = layer_switch_layer.add_instance_with(
            ScriptLayerController(
                editor_properties=EditorProperties(name=f"Switch Layer {layer.index}", unknown=0),
                layer=LayerSwitch(
                    area_id=area.id,
                    layer_number=layer.index,
                ),
            )
        )

        # 13970325
        is_layer_on = load_loader_layer.add_instance_with(
            Switch(
                editor_properties=EditorProperties(name=f"Is Layer {layer.index} on?", unknown=0),
            )
        )

        # 13970326
        layer_is_on = layer.add_instance_with(
            Timer(
                editor_properties=EditorProperties(name="Layer is on", unknown=0),
                time=0.01,
                auto_start=True,
            )
        )
        layer_is_on.add_connection(State.Zero, Message.Open, is_layer_on)

    # 13970327
    layer_menu = layer_switch_layer.add_instance_with(
        GuiMenu(
            editor_properties=EditorProperties(name="Layer Menu", active=False),
            selection_changed_sound=-1,
        )
    )

    # 13970328
    layer_menu_occlusion = layer_switch_layer.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(name="Layer Menu Occlusion Relay", unknown=0),
            function=Function.OcclusionRelay,
        )
    )
    layer_menu_occlusion.add_connection(State.InternalState01, Message.Activate, layer_menu)

    # 13970329
    reload_widget = layer_switch_layer.add_instance_with(
        GuiWidget(
            editor_properties=EditorProperties(name="Reload Widget", active=False),
        )
    )
    layer_menu.add_connection(State.Connect, Message.Attach, reload_widget)

    # 13970330
    reload_textpane = layer_switch_layer.add_instance_with(
        TextPane(
            editor_properties=EditorProperties(
                name="Reload TextPane",
                transform=Transform(
                    position=Vector(4981.0, 4996.0, 5030.0),
                ),
                active=False,
            ),
            text_properties=TEXT_PANE_TEXT_PROPERTIES,
            default_string=1296979444,  # TODO: probably create this strg?
            default_string_name="1",
        )
    )
    layer_menu.add_connection(State.Active, Message.Activate, reload_textpane)
    layer_menu.add_connection(State.Inactive, Message.Deactivate, reload_textpane)

    # 13970331
    reload_colormodulate = layer_switch_layer.add_instance_with(create_color_modulate("Reload"))
    reload_colormodulate.add_connection(State.Play, Message.Activate, reload_textpane)
    layer_menu_occlusion.add_connection(State.InternalState01, Message.Increment, reload_colormodulate)
    reload_widget.add_connection(State.Entered, Message.Increment, reload_colormodulate)
    reload_widget.add_connection(State.Exited, Message.Decrement, reload_colormodulate)

    # 13970332
    reload_area = layer_switch_layer.add_instance_with(
        WorldTeleporter(
            editor_properties=EditorProperties(name="Reload area"),
            world=mlvl_id,
            area=area.mrea_asset_id,
            elevator=-1,
            is_teleport=True,
            display_font=3082539188,
            string=1296979444,  # TODO: probably create?
            characters_per_second=16.0,
            unknown_0x5657ca1c=True,
        )
    )
    reload_widget.add_connection(State.PressA, Message.SetToZero, reload_area)

    # 13970333
    memory_relay_widget = layer_switch_layer.add_instance_with(
        GuiWidget(
            editor_properties=EditorProperties(name="Memry Relay Widget", active=False),
        )
    )
    layer_menu.add_connection(State.Connect, Message.Attach, memory_relay_widget)
    # Reset all the relays
    for layer in area.layers:
        # Skip menu layers
        if layer.name.startswith("Menu - "):
            continue
        for instance in layer.instances:
            if instance.type is MemoryRelay:
                memory_relay_widget.add_connection(State.PressA, Message.Deactivate, instance)

    # 13970334
    pre_reset_memory_relay_textpane = layer_switch_layer.add_instance_with(
        TextPane(
            editor_properties=EditorProperties(
                name="Pre-Reset Memory Relay TextPane",
                transform=Transform(
                    position=Vector(4981.0, 4996.0, 5028.7001953125),
                ),
                active=False,
            ),
            text_properties=TEXT_PANE_TEXT_PROPERTIES,
            default_string=1296979444,  # TODO: probably create this strg?
            default_string_name="2",
        )
    )
    memory_relay_widget.add_connection(State.PressA, Message.Deactivate, pre_reset_memory_relay_textpane)

    # 13970335
    post_reset_memory_relay_textpane = layer_switch_layer.add_instance_with(
        TextPane(
            editor_properties=EditorProperties(
                name="Post-Reset Memory Relay TextPane",
                transform=Transform(
                    position=Vector(4981.0, 4996.0, 5028.7001953125),
                ),
                active=False,
            ),
            text_properties=TEXT_PANE_TEXT_PROPERTIES,
            default_string=1296979444,  # TODO: probably create this strg?
            default_string_name="3",
        )
    )
    memory_relay_widget.add_connection(State.PressA, Message.Activate, post_reset_memory_relay_textpane)

    # 13970336
    memory_relay_colormodulate = layer_switch_layer.add_instance_with(create_color_modulate("Memory Relay"))
    memory_relay_colormodulate.add_connection(State.Play, Message.Activate, pre_reset_memory_relay_textpane)
    memory_relay_colormodulate.add_connection(State.Play, Message.Activate, post_reset_memory_relay_textpane)
    layer_menu_occlusion.add_connection(State.InternalState01, Message.Decrement, memory_relay_colormodulate)
    memory_relay_widget.add_connection(State.Entered, Message.Increment, memory_relay_colormodulate)
    memory_relay_widget.add_connection(State.Exited, Message.Decrement, memory_relay_colormodulate)

    for layer in area.layers:
        # Skip `Default` and `!No Load`, as well as our own layers
        if layer.index < 2 or layer.name.startswith("Menu - "):
            continue

        # 13970337
        layer_name_widget = layer_switch_layer.add_instance_with(
            TextPane(
                editor_properties=GuiWidget(
                    name=f"Layer Menu - {layer.name} Widget",
                    active=False,
                ),
            )
        )

        # 13970338
        layer_name_text_pane = layer_switch_layer.add_instance_with(
            TextPane(
                editor_properties=EditorProperties(
                    name=f"Layer Menu - {layer.name} TextPane",
                    transform=Transform(
                        position=Vector(4981.0, 4996.0, 5026.10009765625),
                    ),
                    active=False,
                ),
                text_properties=TEXT_PANE_TEXT_PROPERTIES,
                default_string=1296979444,  # TODO: probably create this strg?
                default_string_name="4",
            )
        )

        # 13970339
        layer_name_colormodulate = layer_switch_layer.add_instance_with(
            create_color_modulate(
                f"Layer Menu - {layer.name}",
                Color(0.501960813999176, 0, 0, 1),
                Color(0, 0.10196078568696976, 0.10196078568696976, 1.0),
            )
        )
        layer_name_colormodulate.add_connection(State.Play, Message.Activate, layer_name_text_pane)
        layer_name_widget.add_connection(State.Entered, Message.Increment, layer_name_colormodulate)
        layer_name_widget.add_connection(State.Exited, Message.Decrement, layer_name_colormodulate)


def add_menu_mod(editor: PatcherEditor) -> None:
    for asset_id in NAME_TO_ID_MLVL.values():
        mlvl = editor.get_mlvl(asset_id)
        for area in mlvl.areas:
            add_area_elements(area)
