from collections.abc import Iterator

from construct import Container
from retro_data_structures.enums.echoes import Message, PlayerItemEnum, State
from retro_data_structures.formats import Strg
from retro_data_structures.formats.mrea import (
    Area,
)
from retro_data_structures.formats.script_layer import ScriptLayer
from retro_data_structures.formats.script_object import Connection, InstanceId, ScriptInstance
from retro_data_structures.properties.echoes.archetypes import (
    ActorParameters,
    ControllerActionStruct,
    EditorProperties,
    LayerSwitch,
    TextProperties,
    Transform,
    VisorParameters,
)
from retro_data_structures.properties.echoes.archetypes.VisorParameters import VisorFlags
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
from retro_data_structures.properties.echoes.objects.SpecialFunction import Function

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
kOffUnselectedColor = Color(0.5, 0.0, 0.0, 1.0)
kOffSelectedColor = Color(1.0, 0.1, 0.1, 1.0)
kOnUnselectedColor = Color(0.0, 0.35, 0.0, 1.0)
kOnSelectedColor = Color(0.0, 1.0, 0.0, 1.0)


def editor_props(name: str) -> EditorProperties:
    """
    An EditorProperties with given name, and unknown set to 0.
    :param name:
    :return:
    """
    return EditorProperties(name=name, unknown=0)


def _get_connections_to(area: Area, target: InstanceId) -> Iterator[tuple[ScriptInstance, Connection]]:
    for instance in area.all_instances:
        for conn in instance.connections:
            if conn.target == target:
                yield instance, conn


def create_color_modulate(
    name: str,
    color_a: Color = Color(0.5882353186607361, 0.5882353186607361, 0.5882353186607361, 1.0),
    color_b: Color = Color(1.0),
    active: bool = True,
) -> ColorModulate:
    return ColorModulate(
        editor_properties=EditorProperties(name=f"{name} ColorModulate", active=active, unknown=0),
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


def _add_conn(
    layer: ScriptLayer, instance: ScriptInstance, conn: Connection, target: ScriptInstance, message: Message
) -> None:
    pass


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
            if instance.get_properties_as(SpecialFunction).inventory_item_parm == PlayerItemEnum.UnknownItem62:
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


def create_load_loader(
    area: Area,
    loader_layer: ScriptLayer,
    menu_dock: ScriptInstance,
    load_menu: ScriptInstance,
    exit_menu_relay: ScriptInstance,
    special_functions_ids: set[int],
) -> ScriptLayer:
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

    # 13970321
    increment_load_loader = load_loader_layer.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(name="Increment Load Loader", unknown=0),
            function=Function.PlayerInAreaRelay,
        )
    )

    # 13970322
    disable_loading = load_loader_layer.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(name="Disable Loading", unknown=0),
            function=Function.AreaAutoLoadController,
        )
    )

    # 13970323
    door_to_menu_dock = load_loader_layer.add_instance_with(create_door("Door to load Menu Dock"))

    # Connections
    load_dock_layer.add_connection(State.Arrived, Message.Play, load_dock_layer)
    load_dock_layer.add_connection(State.Arrived, Message.Decrement, load_dock_layer)
    increment_load_loader.add_connection(State.Entered, Message.Increment, load_dock_layer)
    increment_load_loader.add_connection(State.Entered, Message.Deactivate, increment_load_loader)
    door_to_menu_dock.add_connection(State.Closed, Message.Decrement, menu_dock)
    door_to_menu_dock.add_connection(State.Open, Message.Increment, menu_dock)
    load_menu.add_connection(State.Open, Message.Stop, disable_loading)
    load_menu.add_connection(State.Open, Message.Open, door_to_menu_dock)
    exit_menu_relay.add_connection(State.Zero, Message.Clear, door_to_menu_dock)
    exit_menu_relay.add_connection(State.Zero, Message.Start, disable_loading)

    for instance in area.all_instances:
        for conn in instance.connections:
            if conn.target in special_functions_ids:
                match conn.message:
                    case Message.Stop:
                        _add_conn(load_loader_layer, instance, conn, disable_loading, Message.Deactivate)
                    case Message.Start:
                        _add_conn(load_loader_layer, instance, conn, disable_loading, Message.Activate)

    return load_loader_layer


def add_area_elements(editor: PatcherEditor, mlvl_id: int, area: Area, menu_area: Area) -> None:
    # string_table: Strg

    docks, special_functions, script_layer_controllers, memory_relays, in_dark_world = _collect_details_from_instances(
        area
    )

    add_menu, add_load_loader = should_add_menu(area, docks)
    if not add_menu:
        print(f"Not adding menu to {area.name}")
        return

    print(f"Adding menu to {area.name}")

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

    if add_load_loader:
        menu_loader_layer = create_load_loader(
            area,
            loader_layer,
            menu_dock,
            load_menu,
            exit_menu_relay,
            {obj.id for obj in special_functions},
        )
    else:
        for obj in docks:
            load_menu.add_connection(State.Open, Message.SetToZero, obj)
        load_menu.add_connection(State.Open, Message.SetToMax, menu_dock)

        menu_loader_layer = loader_layer

    layer_switch_menu = create_layer_switch_menu(
        editor, mlvl_id, area, menu_loader_layer, script_layer_controllers, memory_relays
    )

    # Layer Menu ScriptLayerController
    # Layer Menu Relay

    layer_switch_controller = menu_loader_layer.add_instance_with(
        ScriptLayerController(
            editor_properties=EditorProperties(name="Layer Menu ScriptLayerController", unknown=0),
            layer=LayerSwitch(
                area_id=area.id,
                layer_number=layer_switch_menu.index,
            ),
            is_dynamic=True,
        )
    )
    relay = menu_loader_layer.add_instance_with(
        Relay(
            EditorProperties(name="Layer Menu Relay", unknown=0),
        )
    )
    # relay.id = MenuLayerInstanceId

    relay.add_connection(State.Zero, Message.Close, load_menu)
    relay.add_connection(State.Zero, Message.Increment, layer_switch_controller)
    # relay.add_connection(State.Zero, Message.Deactivate, kMainMenu)
    # relay.add_connection(State.Zero, Message.Deactivate, kLoadingPane)
    # layer_switch_controller.add_connection(State.Arrived, Message.Deactivate, kLoadingPane)
    layer_switch_controller.add_connection(State.Arrived, Message.Play, layer_switch_controller)
    layer_switch_controller.add_connection(State.Arrived, Message.Deactivate, layer_switch_controller)

    if True:  # Do Exceptions
        if area.mrea_asset_id == 0xDF073157:  # Aerie Access
            exit_menu_relay.add_connection(State.Zero, Message.SetToMax, 3997706)
            exit_menu_relay.add_connection(State.Zero, Message.Deactivate, 3997704)

        elif area.mrea_asset_id == 0xC0113CE8:  # Dynamo Works
            pass
            # load_menu.add_connection(
            #     State.Open, Message.Increment,
            #     area.get_layer("Load during Spiderball Battle, Unload Post-Pickup Cinematic").add_instance_with(
            #         kEnableMMULayer)
            # )

        elif area.mrea_asset_id == 0x5D3A0001:  # Aerie
            pass
            # load_menu.add_connection(
            #     State.Open, Message.Increment,
            #     area.get_layer("Dark Samus Battle 2").add_instance_with(kEnableMMULayer)
            # )

        elif area.mrea_asset_id == 1894024576:
            area.get_layer("Echo Bot").active = False


def _replicate_connections(
    area: Area, layer: ScriptLayer, target: ScriptInstance, message_mapping: dict[Message, Message]
) -> None:
    for source, conn in _get_connections_to(area, target.id):
        new_message = message_mapping.get(conn.message)
        if new_message is not None:
            _add_conn(layer, source, conn, target, new_message)


def create_layer_switch_menu(
    editor: PatcherEditor,
    mlvl_id: int,
    area: Area,
    menu_loader_layer: ScriptLayer,
    existing_layer_controllers: list[ScriptInstance],
    memory_relays: list[ScriptInstance],
) -> ScriptLayer:
    # 13970324 Switch Layer 2

    layers: list[ScriptLayer] = []
    script_layer_controllers = []
    layer_switches = []

    for layer in area.layers:
        if should_process_layer(layer):
            layers.append(layer)
            script_layer_controllers.append(
                ScriptLayerController(
                    editor_properties=EditorProperties(name=f"Switch Layer {layer.index}", unknown=0),
                    layer=LayerSwitch(
                        area_id=area.id,
                        layer_number=layer.index,
                    ),
                )
            )

            # Exclusion
            if area.mrea_asset_id == 0x914F1381:
                continue

            is_layer_on = menu_loader_layer.add_instance_with(
                Switch(editor_properties=EditorProperties(name=f"Is Layer {layer.index} on?", unknown=0))
            )
            layer_switches.append(is_layer_on)

            layer_is_on = layer.add_instance_with(
                Timer(
                    editor_properties=EditorProperties(name="Layer is on", unknown=0),
                    time=0.01,
                    auto_start=True,
                )
            )
            layer_is_on.add_connection(State.Zero, Message.Open, is_layer_on)

            for layer_controller in existing_layer_controllers:
                ctrl: ScriptLayerController = layer_controller.get_properties_as(ScriptLayerController)
                if ctrl.layer.layer_number == layer.index:
                    _replicate_connections(
                        area,
                        menu_loader_layer,
                        layer_controller,
                        {
                            Message.Decrement: Message.Close,
                            Message.Increment: Message.Open,
                        },
                    )

    layer_switch_layer = area.add_layer("Menu - Layer Switch Layer", active=False)

    # 13970327
    gui_menu = layer_switch_layer.add_instance_with(
        GuiMenu(
            editor_properties=EditorProperties(name="Layer Menu", active=False),
            selection_changed_sound=-1,
        )
    )

    # 13970328
    occlusion_relay = layer_switch_layer.add_instance_with(
        SpecialFunction(
            editor_properties=EditorProperties(name="Layer Menu Occlusion Relay", unknown=0),
            function=Function.OcclusionRelay,
        )
    )
    occlusion_relay.add_connection(State.InternalState01, Message.Activate, gui_menu)

    string_table_asset_id, string_table = editor.create_strg(
        f"menu_mod_{mlvl_id}_{area.mrea_asset_id}_{area.name}.strg"
    )

    create_area_menu(
        mlvl_id,
        area,
        gui_menu,
        occlusion_relay,
        layer_switch_layer,
        layers,
        script_layer_controllers,
        layer_switches,
        memory_relays,
        string_table,
        string_table_asset_id,
    )

    return layer_switch_layer


def create_area_menu(
    mlvl_id: int,
    area: Area,
    gui_menu: ScriptInstance,
    occlusion_relay: ScriptInstance,
    layer_switch_layer: ScriptLayer,
    layers: list[ScriptLayer],
    script_layer_controllers: list[ScriptLayerController],
    layer_switches: list[ScriptInstance],
    memory_relays: list[ScriptInstance],
    string_table: Strg,
    string_table_asset_id: int,
):
    strings = [
        "Reloading...",
        "Reload Area",
        "Reset Loaded Memory Relays",
        "[Memory Relays Have Been Reset]",
    ]

    def create_text_pane(
        name: str,
        position: Vector,
        string_name: str,
    ) -> TextPane:
        return TextPane(
            editor_properties=EditorProperties(
                name=name,
                transform=Transform(
                    position=position,
                ),
                active=False,
            ),
            text_properties=TEXT_PANE_TEXT_PROPERTIES,
            default_string=string_table_asset_id,
            default_string_name=string_name,
        )

    # 13970329
    reload_widget = layer_switch_layer.add_instance_with(
        GuiWidget(
            editor_properties=EditorProperties(name="Reload Widget", active=False),
        )
    )

    # 13970330
    reload_textpane = layer_switch_layer.add_instance_with(
        create_text_pane("Reload TextPane", Vector(4981.0, 4996.0, 5030.0), "1")
    )

    # 13970331
    reload_colormodulate = layer_switch_layer.add_instance_with(create_color_modulate("Reload"))
    occlusion_relay.add_connection(State.InternalState01, Message.Increment, reload_colormodulate)

    # 13970332
    reload_area = layer_switch_layer.add_instance_with(
        WorldTeleporter(
            editor_properties=EditorProperties(name="Reload area"),
            world=mlvl_id,
            area=area.mrea_asset_id,
            elevator=-1,
            is_teleport=True,
            display_font=3082539188,
            string=string_table_asset_id,
            characters_per_second=16.0,
            unknown_0x5657ca1c=True,
        )
    )

    reload_widget.add_connection(State.PressA, Message.SetToZero, reload_area)

    gui_menu.add_connection(State.Connect, Message.Attach, reload_widget)
    gui_menu.add_connection(State.Active, Message.Activate, reload_textpane)
    gui_menu.add_connection(State.Inactive, Message.Deactivate, reload_textpane)
    reload_colormodulate.add_connection(State.Play, Message.Activate, reload_textpane)
    reload_widget.add_connection(State.Entered, Message.Increment, reload_colormodulate)
    reload_widget.add_connection(State.Exited, Message.Decrement, reload_colormodulate)

    # Layer.Assets.Add(new CDependency(0xB7BBD0B4, "FONT"));

    # 13970333
    memory_relay_widget = layer_switch_layer.add_instance_with(
        GuiWidget(
            editor_properties=EditorProperties(name="Memory Relay Widget", active=False),
        )
    )

    # 13970334
    pre_reset_memory_relay_textpane = layer_switch_layer.add_instance_with(
        create_text_pane("Pre-Reset Memory Relay TextPane", Vector(4981.0, 4996.0, 5028.7), "2")
    )

    # 13970335
    post_reset_memory_relay_textpane = layer_switch_layer.add_instance_with(
        create_text_pane("Post-Reset Memory Relay TextPane", Vector(4981.0, 4996.0, 5028.7), "3")
    )

    # 13970336
    memory_relay_colormodulate = layer_switch_layer.add_instance_with(create_color_modulate("Memory Relay"))
    occlusion_relay.add_connection(State.InternalState01, Message.Decrement, memory_relay_colormodulate)

    # Reset all the relays
    for instance in memory_relays:
        memory_relay_widget.add_connection(State.PressA, Message.Deactivate, instance)
    memory_relay_widget.add_connection(State.PressA, Message.Deactivate, pre_reset_memory_relay_textpane)
    memory_relay_widget.add_connection(State.PressA, Message.Activate, post_reset_memory_relay_textpane)

    # connections
    gui_menu.add_connection(State.Connect, Message.Attach, memory_relay_widget)
    gui_menu.add_connection(State.Active, Message.Activate, pre_reset_memory_relay_textpane)
    gui_menu.add_connection(State.Inactive, Message.Deactivate, pre_reset_memory_relay_textpane)

    memory_relay_colormodulate.add_connection(State.Play, Message.Activate, pre_reset_memory_relay_textpane)
    memory_relay_colormodulate.add_connection(State.Play, Message.Activate, post_reset_memory_relay_textpane)
    memory_relay_widget.add_connection(State.Entered, Message.Increment, memory_relay_colormodulate)
    memory_relay_widget.add_connection(State.Exited, Message.Decrement, memory_relay_colormodulate)

    text_name_position = 5026.1
    for layer, layer_controller_props in zip(layers, script_layer_controllers, strict=True):
        strings.append(layer.name)

        # 13970337
        layer_name_widget = layer_switch_layer.add_instance_with(
            GuiWidget(
                editor_properties=EditorProperties(
                    name=f"Layer Menu - {layer.name} Widget",
                    active=False,
                ),
            )
        )

        # 13970338
        layer_name_text_pane = layer_switch_layer.add_instance_with(
            create_text_pane(
                f"Layer Menu - {layer.name} TextPane", Vector(4981.0, 4996.0, text_name_position), str(len(strings))
            ),
        )
        text_name_position -= 1.3

        # 13970339
        layer_name_colormodulate_props = create_color_modulate(f"Layer Menu - {layer.name}")
        layer_name_colormodulate_props.color_a = kOffUnselectedColor
        layer_name_colormodulate_props.color_b = kOffSelectedColor
        layer_name_color_modulate = layer_switch_layer.add_instance_with(layer_name_colormodulate_props)

        layer_name_color_indicator_props = create_color_modulate(f"{layer.name} Indicator", active=False)
        layer_name_color_indicator_props.color_a = kOnUnselectedColor
        layer_name_color_indicator_props.color_b = kOnSelectedColor
        layer_name_color_indicator = layer_switch_layer.add_instance_with(layer_name_color_indicator_props)

        layer_controller = layer_switch_layer.add_instance_with(layer_controller_props)

        layer_switch = layer_switch_layer.add_instance_with(
            Switch(
                editor_properties=EditorProperties(name=f"{layer.name} Switch"),
                is_open=False,
            )
        )

        gui_menu.add_connection(State.Connect, Message.Attach, layer_name_widget)
        gui_menu.add_connection(State.Active, Message.Activate, layer_name_text_pane)
        gui_menu.add_connection(State.Inactive, Message.Deactivate, layer_name_text_pane)

        layer_name_color_modulate.add_connection(State.Play, Message.Activate, layer_name_text_pane)
        layer_name_color_indicator.add_connection(State.Play, Message.Activate, layer_name_text_pane)
        layer_name_widget.add_connection(State.Entered, Message.Increment, layer_name_color_modulate)
        layer_name_widget.add_connection(State.Exited, Message.Decrement, layer_name_color_modulate)
        layer_name_widget.add_connection(State.Entered, Message.Increment, layer_name_color_indicator)
        layer_name_widget.add_connection(State.Exited, Message.Decrement, layer_name_color_indicator)
        layer_name_widget.add_connection(State.PressA, Message.SetToZero, layer_switch)
        layer_switch.add_connection(State.Open, Message.Decrement, layer_controller)
        layer_switch.add_connection(State.Open, Message.Deactivate, layer_name_color_indicator)
        layer_switch.add_connection(State.Open, Message.Activate, layer_name_color_modulate)
        layer_switch.add_connection(State.Open, Message.Increment, layer_name_color_modulate)
        layer_switch.add_connection(State.Open, Message.Close, layer_switch)
        layer_switch.add_connection(State.Closed, Message.Increment, layer_controller)
        layer_switch.add_connection(State.Closed, Message.Activate, layer_name_color_indicator)
        layer_switch.add_connection(State.Closed, Message.Deactivate, layer_name_color_modulate)
        layer_switch.add_connection(State.Closed, Message.Decrement, layer_name_color_modulate)
        layer_switch.add_connection(State.Closed, Message.Open, layer_switch)
        if layer_switches:
            for switch in layer_switches:
                occlusion_relay.add_connection(State.InternalState01, Message.SetToZero, switch)
                switch.add_connection(State.Closed, Message.Deactivate, layer_name_color_indicator)
                switch.add_connection(State.Closed, Message.Activate, layer_name_color_modulate)
                switch.add_connection(State.Closed, Message.Decrement, layer_name_color_modulate)
                switch.add_connection(State.Open, Message.Activate, layer_name_color_indicator)
                switch.add_connection(State.Open, Message.Deactivate, layer_name_color_modulate)
                switch.add_connection(State.Open, Message.Decrement, layer_name_color_indicator)
                switch.add_connection(State.Open, Message.Open, layer_switch)
        else:
            target_layer = list(area.layers)[layer_controller_props.layer.layer_number]
            if target_layer.active:
                occlusion_relay.add_connection(State.InternalState01, Message.Activate, layer_name_color_indicator)
                occlusion_relay.add_connection(State.InternalState01, Message.Deactivate, layer_name_color_modulate)
                occlusion_relay.add_connection(State.InternalState01, Message.Decrement, layer_name_color_indicator)
                occlusion_relay.add_connection(State.InternalState01, Message.Increment, layer_controller)
                occlusion_relay.add_connection(State.InternalState01, Message.Open, layer_switch)
            else:
                occlusion_relay.add_connection(State.InternalState01, Message.Deactivate, layer_name_color_indicator)
                occlusion_relay.add_connection(State.InternalState01, Message.Activate, layer_name_color_modulate)
                occlusion_relay.add_connection(State.InternalState01, Message.Decrement, layer_name_color_modulate)
                occlusion_relay.add_connection(State.InternalState01, Message.Decrement, layer_controller)
            # FIXME: add notice that it's not working

    string_table.set_string_list(strings)
