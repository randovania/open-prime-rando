from open_prime_rando.echoes.asset_ids.world import NAME_TO_ID_MLVL
from open_prime_rando.patcher_editor import PatcherEditor
from open_prime_rando.echoes.vulnerabilities import resist_all_vuln

from retro_data_structures.formats.mrea import (
    Area,
)
from retro_data_structures.properties.echoes.archetypes import EditorProperties, ControllerActionStruct, Transform, LayerSwitch, ActorParameters, VisorParameters
from retro_data_structures.properties.echoes.objects import SpecialFunction, ControllerAction, AdvancedCounter, Switch, Timer, Dock, Relay, ScriptLayerController, Door
from retro_data_structures.properties.echoes.core import Vector, AnimationParameters
from retro_data_structures.enums.echoes import Function, State, Message, VisorFlags


def add_area_elements(area: Area) -> None:
    loader_layer = area.add_layer("Menu - Loader", active=False)

    # 13970313
    enable_controller = loader_layer.add_instance_with(SpecialFunction(
        editor_properties=EditorProperties(name="Player In Area Relay - Enable ControllerAction", unknown=0),
        function=Function.PlayerInAreaRelay,
    ))
    # 13970314
    check_for_dpad = loader_layer.add_instance_with(ControllerAction(
        editor_properties=EditorProperties(name="Check for D-Pad Up press"),
        controller_action_struct=ControllerActionStruct(command=58),
        one_shot=False,
    ))
    enable_controller.add_connection(State.Entered, Message.Activate, check_for_dpad)
    enable_controller.add_connection(State.Exited, Message.Deactivate, check_for_dpad)

    # 13970315
    dpad_count = loader_layer.add_instance_with(AdvancedCounter(
        editor_properties=EditorProperties(name="Count D-Pad Up presses", unknown=0),
        max_count=4,
    ))
    check_for_dpad.add_connection(State.Open, Message.Increment, dpad_count)

    # 13970316
    load_menu = loader_layer.add_instance_with(Switch(
        editor_properties=EditorProperties(name="Load Menu", unknown=0),
        is_open=True,
    ))
    load_menu.add_connection(State.Open, Message.Deactivate, check_for_dpad)
    dpad_count.add_connection(State.InternalState00, Message.Deactivate, load_menu)
    dpad_count.add_connection(State.MaxReached, Message.SetToZero, load_menu)

    # 13970317
    reset_dpad_counter = loader_layer.add_instance_with(Timer(
        editor_properties=EditorProperties(name="Reset Counter if D-Pad not pressed quickly enough", unknown=0),
        time=0.5,
    ))
    reset_dpad_counter.add_connection(State.Zero, Message.Reset, dpad_count)
    dpad_count.add_connection(State.Open, Message.ResetAndStart, reset_dpad_counter)

    # 13970318
    stop_quick_counter = loader_layer.add_instance_with(Timer(
        editor_properties=EditorProperties(name="Stop Counter increasing TOO quickly (cutscene skip workaround)", unknown=0),
        time=0.1,
    ))
    dpad_count.add_connection(State.InternalState00, Message.ResetAndStart, stop_quick_counter)
    stop_quick_counter.add_connection(State.Zero, Message.Activate, load_menu)

    # 13970319
    menu_dock = loader_layer.add_instance_with(Dock(
        editor_properties=EditorProperties(
            name="Menu Dock",
            transform=Transform(position=Vector(100000.0, 100000.0, 100000.0))
        ),
        # TODO: these are likely area-dependent
        dock_number=1,
        area_number=0,
        load_connected_immediate=False,
    ))
    menu_dock.add_connection(State.MaxReached, Message.Increment, menu_dock)

    # Exit Menu
    # Layer Menu ScriptLayerController
    # Layer Menu Relay

    load_loader_layer = area.add_layer("Menu - Load Loader", active=True)

    # 13970320
    load_dock_layer = load_loader_layer.add_instance_with(ScriptLayerController(
        editor_properties=EditorProperties(name="Load Dock Layer", unknown=0),
        layer=LayerSwitch(
            area_id=area.id,
            layer_number=loader_layer.index,
        ),
        is_dynamic=True,
    ))
    load_dock_layer.add_connection(State.Arrived, Message.Play, load_dock_layer)
    load_dock_layer.add_connection(State.Arrived, Message.Decrement, load_dock_layer)

    # 13970321
    increment_load_loader = load_loader_layer.add_instance_with(SpecialFunction(
        editor_properties=EditorProperties(name="Increment Load Loader", unknown=0),
        function=Function.PlayerInAreaRelay,
    ))
    increment_load_loader.add_connection(State.Entered, Message.Increment, load_dock_layer)
    increment_load_loader.add_connection(State.Entered, Message.Deactivate, increment_load_loader)

    # 13970322
    disable_loading = load_loader_layer.add_instance_with(SpecialFunction(
        editor_properties=EditorProperties(name="Disable Loading", unknown=0),
        function=Function.AreaAutoLoadController,
    ))
    load_menu.add_connection(State.Open, Message.Stop, disable_loading)

    # 13970323
    door_to_menu_dock = load_loader_layer.add_instance_with(Door(
        editor_properties=EditorProperties(
            name="Disable Loading",
            transform=Transform(position=Vector(100000.0, 100000.0, 100000.0)),
        ),
        collision_box=Vector(0.35, 5.0, 4.0),
        collision_offset=(-0.175, 0.0, 2.0),
        vulnerability=resist_all_vuln,
        animation_information=AnimationParameters(ancs=0xceb091f7, initial_anim=0xffffffff),
        actor_information=ActorParameters(
            visor=VisorParameters(scan_through=True, visor_flags=VisorFlags(0)),
            unknown_0xcd4c81a1=True,
            force_render_unsorted=True,
            unknown_0xf07981e8=True,
            unknown_0x6df33845=True,
        ),
        is_open=False,
        close_delay=0.25,
    ))
    door_to_menu_dock.add_connection(State.Closed, Message.Decrement, menu_dock)
    door_to_menu_dock.add_connection(State.Open, Message.Increment, menu_dock)

    # 13970324 Switch Layer 2

    # 13970325
    is_layer_two_on = load_loader_layer.add_instance_with(Switch(
        editor_properties=EditorProperties(name="Is Layer 2 on?", unknown=0),
    ))


def add_menu_mod(editor: PatcherEditor) -> None:
    for asset_id in NAME_TO_ID_MLVL.values():
        mlvl = editor.get_mlvl(asset_id)
        for area in mlvl.areas:
            add_area_elements(area)
