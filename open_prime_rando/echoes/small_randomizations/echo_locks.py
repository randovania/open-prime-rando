import random
from open_prime_rando.echoes.asset_ids.sanctuary_fortress import MAIN_GYRO_CHAMBER_MREA, SENTINELS_PATH_MREA
from open_prime_rando.echoes.asset_ids.temple_grounds import PROFANE_PATH_MREA
from open_prime_rando.patcher_editor import PatcherEditor

from retro_data_structures.properties.echoes.objects.Sound import Sound
from retro_data_structures.properties.echoes.objects.Switch import Switch
from retro_data_structures.properties.echoes.objects.PointOfInterest import PointOfInterest
from retro_data_structures.properties.echoes.objects.ScannableObjectInfo import ScannableObjectInfo
from retro_data_structures.enums.echoes import ScanSpeed

from retro_data_structures.crc import crc32

from retro_data_structures.formats.scan import Scan
from retro_data_structures.formats.strg import Strg

ECHO_LOCK_MREAS = [MAIN_GYRO_CHAMBER_MREA, SENTINELS_PATH_MREA, PROFANE_PATH_MREA]
ECHO_LOCK_STATES = ["ZERO", "IS00", "IS01", "IS02"]
ECHO_LOCK_SOUNDS = [1005, 1006, 1007]


def randomize_echo_locks(editor: PatcherEditor, rng: random.Random):
    # create key scan assets
    key_scan = editor.get_parsed_asset(0x2E7C4349, type_hint=Scan)
    scan_info: ScannableObjectInfo = key_scan.scannable_object_info.get_properties()
    key_strg = editor.get_parsed_asset(0x43894960, type_hint=Strg)
    
    all_paks = set()
    for mrea in ECHO_LOCK_MREAS:
        all_paks.update(editor.find_paks(mrea))
    
    key_scans = []
    for pitch in ["low", "medium", "high"]:
        key_strg.set_string(1, f"Sonic detection gear needed to interface with this system. Shoot the Echo Key Beam emitter with a sonic pulse to activate it. It will then fire a blast of &push;&main-color=#FF3333;{pitch}-pitched&pop; sound at an Echo Gate lock.")
        strg_id = editor.add_file(f"accessible_echo_lock_{pitch}.STRG", key_strg, all_paks)

        scan_info.string = strg_id
        key_scan.scannable_object_info.set_properties(scan_info)
        scan_id = editor.add_file(f"accessible_echo_lock_{pitch}.SCAN", key_scan, all_paks)

        key_scans.append(scan_id)
    
    gate_scan = editor.get_parsed_asset(0x80A987AA, type_hint=Scan)
    gate_scan_info: ScannableObjectInfo = gate_scan.scannable_object_info.get_properties()
    gate_scan_info.scan_speed = ScanSpeed.Slow
    gate_strg = editor.get_parsed_asset(0x2820CC3D, type_hint=Strg)

    for asset_id in ECHO_LOCK_MREAS:
        mrea = editor.get_mrea(asset_id)
        solution = [rng.randint(0, 2) for _ in range(4)]

        counter = mrea.get_instance_by_name("Lock Solution Counter")
        gate_poi = mrea.get_instance_by_name("(Gate) Echo Gate Scan Point")
        correct_key_relays = [mrea.get_instance_by_name(f"[IN] Set Key {i} As Correct Choice") for i in range(3)]
        lock_tone_players = [mrea.get_instance_by_name(f"(Gate) Lock {i} Tone") for i in range(4)]
        key_switches = [mrea.get_instance_by_name(f"(Key {i}) Check Echo Key") for i in range(3)]
        key_scan_points = [mrea.get_instance_by_name(f"(Key {i}) Scan Point") for i in range(3)]

        for relay in correct_key_relays:
            counter.remove_connections(relay)
        
        for i, key in enumerate(solution):
            counter.add_connection(ECHO_LOCK_STATES[i], "ZERO", correct_key_relays[key])
            
            tone: Sound = lock_tone_players[i].get_properties()
            tone.sound = ECHO_LOCK_SOUNDS[key]
            lock_tone_players[i].set_properties(tone)

            scan: PointOfInterest = key_scan_points[key].get_properties()
            scan.scan_info.scannable_info0 = key_scans[key]
            key_scan_points[key].set_properties(scan)
        
        for i, switch in enumerate(key_switches):
            props: Switch = switch.get_properties()
            props.is_open = i == solution[0]
            switch.set_properties(props)
        
        # edit scan to indicate the solution
        solution_text = "Sonic detection gear needed to interface with this system. The combination of its sonic locks is:\n"
        solution_text += ", ".join((["Low", "Medium", "High"][key] for key in solution))
        gate_strg.set_string(1, solution_text)
        strg_id = editor.add_file(f"accessible_echo_gate_{asset_id}.STRG", gate_strg, all_paks)

        gate_scan_info.string = strg_id
        gate_scan.scannable_object_info.set_properties(gate_scan_info)
        scan_id = editor.add_file(f"accessible_echo_gate_{asset_id}.SCAN", gate_scan, all_paks)

        poi: PointOfInterest = gate_poi.get_properties()
        poi.scan_info.scannable_info0 = scan_id
        gate_poi.set_properties(poi)
