import random

from retro_data_structures.enums.echoes import Message, ScanSpeed, State
from retro_data_structures.formats.scan import Scan
from retro_data_structures.formats.strg import Strg
from retro_data_structures.properties.echoes.objects.PointOfInterest import PointOfInterest
from retro_data_structures.properties.echoes.objects.ScannableObjectInfo import ScannableObjectInfo
from retro_data_structures.properties.echoes.objects.Sound import Sound
from retro_data_structures.properties.echoes.objects.Switch import Switch

from open_prime_rando.echoes.asset_ids.sanctuary_fortress import MAIN_GYRO_CHAMBER_MREA, SENTINELS_PATH_MREA
from open_prime_rando.echoes.asset_ids.temple_grounds import PROFANE_PATH_MREA
from open_prime_rando.echoes.asset_ids.world import SANCTUARY_FORTRESS_MLVL, TEMPLE_GROUNDS_MLVL
from open_prime_rando.patcher_editor import PatcherEditor

ECHO_LOCK_MREAS = [
    (SANCTUARY_FORTRESS_MLVL, MAIN_GYRO_CHAMBER_MREA),
    (SANCTUARY_FORTRESS_MLVL, SENTINELS_PATH_MREA),
    (TEMPLE_GROUNDS_MLVL, PROFANE_PATH_MREA)
]
ECHO_LOCK_STATES = [State.Zero, State.InternalState00, State.InternalState01, State.InternalState02]
ECHO_LOCK_SOUNDS = [1005, 1006, 1007]


def randomize_echo_locks(editor: PatcherEditor, rng: random.Random):
    # create key scan assets
    key_scan = editor.get_parsed_asset(0x2E7C4349, type_hint=Scan)
    scan_info = key_scan.scannable_object_info.get_properties_as(ScannableObjectInfo)
    key_strg = editor.get_parsed_asset(0x43894960, type_hint=Strg)

    key_scans = []
    for pitch in ["low", "medium", "high"]:
        key_strg.set_string(
            1,
            "Sonic detection gear needed to interface with this system."
            " Shoot the Echo Key Beam emitter with a sonic pulse to activate it."
            f" It will then fire a blast of &push;&main-color=#FF3333;{pitch}-pitched&pop; sound at an Echo Gate lock."
        )
        strg_id = editor.add_file(f"accessible_echo_lock_{pitch}.STRG", key_strg)

        scan_info.string = strg_id
        key_scan.scannable_object_info.set_properties(scan_info)
        key_scan.rebuild_dependencies()
        scan_id = editor.add_file(f"accessible_echo_lock_{pitch}.SCAN", key_scan)

        key_scans.append(scan_id)

    gate_scan = editor.get_parsed_asset(0x80A987AA, type_hint=Scan)
    gate_scan_info = gate_scan.scannable_object_info.get_properties_as(ScannableObjectInfo)
    gate_scan_info.scan_speed = ScanSpeed.Slow
    gate_strg = editor.get_parsed_asset(0x2820CC3D, type_hint=Strg)

    for mlvl_id, mrea_id in ECHO_LOCK_MREAS:
        area = editor.get_area(mlvl_id, mrea_id)
        solution = [rng.randint(0, 2) for _ in range(4)]

        counter = area.get_instance("Lock Solution Counter")
        gate_poi = area.get_instance("(Gate) Echo Gate Scan Point")
        correct_key_relays = [area.get_instance(f"[IN] Set Key {i} As Correct Choice") for i in range(3)]
        lock_tone_players = [area.get_instance(f"(Gate) Lock {i} Tone") for i in range(4)]
        key_switches = [area.get_instance(f"(Key {i}) Check Echo Key") for i in range(3)]
        key_scan_points = [area.get_instance(f"(Key {i}) Scan Point") for i in range(3)]

        for relay in correct_key_relays:
            counter.remove_connections_from(relay)

        # Update all scan posts to have the updated scan text
        for scan_point, key_scan in zip(key_scan_points, key_scans):
            with scan_point.edit_properties(PointOfInterest) as scan:
                scan.scan_info.scannable_info0 = key_scan

        for i, key in enumerate(solution):
            counter.add_connection(ECHO_LOCK_STATES[i], Message.SetToZero, correct_key_relays[key])

            with lock_tone_players[i].edit_properties(Sound) as tone:
                tone.sound = ECHO_LOCK_SOUNDS[key]

        for i, switch in enumerate(key_switches):
            with switch.edit_properties(Switch) as props:
                props.is_open = i == solution[0]

        # edit scan to indicate the solution
        solution_text = ("Sonic detection gear needed to interface with this system. "
                         "The combination of its sonic locks is:\n")
        solution_text += ", ".join(["Low", "Medium", "High"][key] for key in solution)
        gate_strg.set_string(1, solution_text)
        strg_id = editor.add_file(f"accessible_echo_gate_{mrea_id}.STRG", gate_strg)

        gate_scan_info.string = strg_id
        gate_scan.scannable_object_info.set_properties(gate_scan_info)
        scan_id = editor.add_file(f"accessible_echo_gate_{mrea_id}.SCAN", gate_scan)

        with gate_poi.edit_properties(PointOfInterest) as poi:
            poi.scan_info.scannable_info0 = scan_id

        area.update_all_dependencies()

