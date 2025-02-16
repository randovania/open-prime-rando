from construct import Container
from retro_data_structures.enums.echoes import Function, Message, PlayerItem, State, VisorFlags
from retro_data_structures.formats.mrea import (
    Area,
)
from retro_data_structures.formats.script_layer import ScriptLayer
from retro_data_structures.formats.script_object import ScriptInstance
from retro_data_structures.properties.echoes.archetypes import (
    ActorParameters,
    ControllerActionStruct,
    EditorProperties,
    LayerSwitch,
    TextProperties,
    Transform,
    VisorParameters,
)
from retro_data_structures.properties.echoes.core import AnimationParameters, Color, Spline, Vector
from retro_data_structures.properties.echoes.objects import (
    AdvancedCounter,
    AreaAttributes,
    ColorModulate,
    ControllerAction,
    Dock,
    Door,
    GuiMenu,
    GuiWidget,
    MemoryRelay,
    Relay,
    ScriptLayerController,
    SpecialFunction,
    Switch,
    TextPane,
    Timer,
    WorldTeleporter,
)

from open_prime_rando.echoes.asset_ids.world import NAME_TO_ID_MLVL
from open_prime_rando.echoes.vulnerabilities import resist_all_vuln
from open_prime_rando.patcher_editor import PatcherEditor

TEXT_PANE_TEXT_PROPERTIES = TextProperties(
    text_bounding_width=15,
    text_bounding_height=15,
    foreground_color=Color(a=1.0),
    outline_color=Color(a=1.0),
    geometry_color=Color(a=1.0),
    default_font=227804281,
    wrap_text=False,
)


def editor_props(name: str) -> EditorProperties:
    """
    An EditorProperties with given name, and unknown set to 0.
    :param name:
    :return:
    """
    return EditorProperties(name=name, unknown=0)


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


def add_dock_to_menu(area: Area, menu_area: Area) -> int:
    """
    Creates a new dock in the target area that connects to the special dock in menu_area
    :param area:
    :param menu_area:
    :return: Index of the new dock.
    """
    area._raw.docks.append(
        Container(
            connecting_dock=[
                Container(
                    area_index=menu_area.id,
                    dock_index=0,
                ),
            ],
            dock_coordinates=[
                [0, 0, 0],
                [0, 5, 0],
                [5, 0, 0],
                [5, 5, 0],
            ],
        )
    )
    dock_index = len(area._raw.docks) - 1
    menu_area._raw.docks[0].connecting_dock.append(
        Container(
            area_index=area.id,
            dock_index=dock_index,
        )
    )
    return dock_index


def player_in_area_relay(name: str) -> SpecialFunction:
    """
    Creates a `SpecialFunction` for PlayerInAreaRelay.
    :param name:
    :return:
    """
    return SpecialFunction(
        editor_properties=EditorProperties(name=name, unknown=0),
        function=Function.PlayerInAreaRelay,
    )


def controller_action(name: str, command: int, one_shot: bool) -> ControllerAction:
    """
    Creates a ControllerAction for detecting the given controller command.
    :param name:
    :param command:
    :param one_shot:
    :return:
    """
    return ControllerAction(
        editor_properties=EditorProperties(name=name),
        controller_action_struct=ControllerActionStruct(command=command),
        one_shot=one_shot,
    )


def advanced_counter(name: str, max_count: int) -> AdvancedCounter:
    """
    Creates an AdvancedCount with given max_count.
    :param name:
    :param max_count:
    :return:
    """
    return AdvancedCounter(
        editor_properties=EditorProperties(name=name, unknown=0),
        max_count=max_count,
    )


def create_dock(name: str, dock_num: int, area_num: int) -> Dock:
    """
    Creates a Dock with custom position
    :param name:
    :param dock_num:
    :param area_num:
    :return:
    """
    return Dock(
        editor_properties=EditorProperties(
            name=name, transform=Transform(position=Vector(100000.0, 100000.0, 100000.0))
        ),
        dock_number=dock_num,
        area_number=area_num,
        load_connected_immediate=False,
    )


def create_door(name: str) -> Door:
    return Door(
        editor_properties=EditorProperties(
            name=name,
            transform=Transform(position=Vector(100000.0, 100000.0, 100000.0)),
        ),
        collision_box=Vector(0.35, 5.0, 4.0),
        collision_offset=Vector(-0.175, 0.0, 2.0),
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


def _collect_details_from_instances(
    area: Area,
) -> tuple[list[ScriptInstance], list[ScriptInstance], list[ScriptInstance], list[ScriptInstance], bool]:
    """
    Collect details needed for later
    :param area:
    :return:
    """
    docks = []
    special_functions = []
    script_layer_controllers = []
    memory_relays = []
    in_dark_world = False

    for instance in area.all_instances:
        if instance.type == Dock:
            docks.append(instance)

        elif instance.type == AreaAttributes:
            in_dark_world = instance.get_properties_as(AreaAttributes).dark_world

        elif instance.type == SpecialFunction:
            if instance.get_properties_as(SpecialFunction).inventory_item_parm == PlayerItem.UnknownItem62:
                special_functions.append(instance)

        elif instance.type == ScriptLayerController:
            script_layer_controllers.append(instance)

        elif instance.type == MemoryRelay:
            memory_relays.append(instance)

    return docks, special_functions, script_layer_controllers, memory_relays, in_dark_world


def should_add_menu(area: Area, docks: list[ScriptInstance]) -> tuple[bool, bool]:
    """
    :param area
    :param docks:
    :return:
    """
    add_load_loader = False
    set_add_load_loader = False
    add_menu = True
    for dock_instance in docks:
        dock: Dock = dock_instance.get_properties_as(Dock)
        if not dock.is_virtual and len(area._raw.docks[dock.dock_number].connecting_dock) > 0:
            if not set_add_load_loader:
                add_load_loader = dock.load_connected_immediate
                set_add_load_loader = True

            elif add_load_loader != dock.load_connected_immediate:
                # does not happen
                add_menu = False
                break

    return add_menu, add_load_loader


def should_process_layer(layer: ScriptLayer) -> bool:
    """Skip `Default` and `!No Load`, as well as our own layers"""
    return layer.index >= 2 and not layer.name.startswith("Menu - ")


def create_layer_switch(
    target_layer: ScriptLayer,
    layer_switch_layer: ScriptLayer,
    load_loader_layer: ScriptLayer,
) -> None:
    # 13970324
    layer_switch_layer.add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(name=f"Switch Layer {target_layer.index}", unknown=0),
            layer=LayerSwitch(
                area_id=target_layer._parent_area.id,
                layer_number=target_layer.index,
            ),
        )
    )

    # 13970325
    is_layer_on = load_loader_layer.add_instance_with(
        Switch(
            editor_properties=EditorProperties(name=f"Is Layer {target_layer.index} on?", unknown=0),
        )
    )

    # 13970326
    layer_is_on = target_layer.add_instance_with(
        Timer(
            editor_properties=EditorProperties(name="Layer is on", unknown=0),
            time=0.01,
            auto_start=True,
        )
    )
    layer_is_on.add_connection(State.Zero, Message.Open, is_layer_on)


def add_area_elements(mlvl_id: int, area: Area, menu_area: Area) -> None:
    # string_table: Strg

    docks, special_functions, script_layer_controllers, memory_relays, in_dark_world = _collect_details_from_instances(
        area
    )

    add_menu, add_load_loader = should_add_menu(area, docks)
    if not add_menu:
        return

    # Connect the area to the Menu
    dock_index = add_dock_to_menu(area, menu_area)

    loader_layer = area.add_layer("Menu - Loader", active=False)

    # 13970313
    enable_controller = loader_layer.add_instance_with(
        player_in_area_relay("Player In Area Relay - Enable ControllerAction")
    )
    # 13970314
    check_for_dpad = loader_layer.add_instance_with(controller_action("Check for D-Pad Up press", 58, False))
    # 13970315
    dpad_count = loader_layer.add_instance_with(advanced_counter("Count D-Pad Up presses", 4))
    # 13970316
    load_menu = loader_layer.add_instance_with(Switch(editor_props("Load Menu"), is_open=True))
    # 13970317
    reset_dpad_counter = loader_layer.add_instance_with(
        Timer(editor_props("Reset Counter if D-Pad not pressed quickly enough"), time=0.5)
    )
    # 13970318
    stop_quick_counter = loader_layer.add_instance_with(
        Timer(editor_props("Stop Counter increasing TOO quickly (cutscene skip workaround)"), time=0.1)
    )

    # 13970319
    menu_dock = loader_layer.add_instance_with(create_dock("Menu Dock", dock_index, area.index))

    # Exit Menu
    exit_menu_relay = loader_layer.add_instance_with(Relay(EditorProperties(name="Exit Menu"), one_shot=False))
    # TODO: use a static id so the menu can connect to it

    enable_controller.add_connection(State.Entered, Message.Activate, check_for_dpad)
    enable_controller.add_connection(State.Exited, Message.Deactivate, check_for_dpad)
    check_for_dpad.add_connection(State.Open, Message.Increment, dpad_count)
    check_for_dpad.add_connection(State.Open, Message.ResetAndStart, reset_dpad_counter)

    dpad_count.add_connection(State.InternalState00, Message.Deactivate, load_menu)
    dpad_count.add_connection(State.InternalState00, Message.ResetAndStart, stop_quick_counter)
    dpad_count.add_connection(State.MaxReached, Message.SetToZero, load_menu)

    load_menu.add_connection(State.Open, Message.Deactivate, check_for_dpad)

    reset_dpad_counter.add_connection(State.Zero, Message.Reset, dpad_count)
    stop_quick_counter.add_connection(State.Zero, Message.Activate, load_menu)

    menu_dock.add_connection(State.MaxReached, Message.Increment, menu_dock)
    # exit_menu_relay.add_connection(State.Zero, Message.Deactivate, CSettings.CameraID)  TODO
    exit_menu_relay.add_connection(State.Zero, Message.SetToZero, menu_dock)
    exit_menu_relay.add_connection(State.Zero, Message.Activate, check_for_dpad)

    # Layer Menu ScriptLayerController
    # Layer Menu Relay

    if add_load_loader:
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
    door_to_menu_dock = load_loader_layer.add_instance_with(create_door("Door to load Menu Dock"))
    door_to_menu_dock.add_connection(State.Closed, Message.Decrement, menu_dock)
    door_to_menu_dock.add_connection(State.Open, Message.Increment, menu_dock)


def create_layer_switch_menu(area: Area, mlvl_id: int):
    # 13970324 Switch Layer 2

    layer_switch_layer = area.add_layer("Menu - Layer Switch Layer", active=False)

    for layer in area.layers:
        if should_process_layer(layer):
            create_layer_switch(layer)

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
        if not should_process_layer(layer):
            continue

        # 13970337
        layer_name_widget = layer_switch_layer.add_instance_with(
            TextPane(
                editor_properties=EditorProperties(
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
