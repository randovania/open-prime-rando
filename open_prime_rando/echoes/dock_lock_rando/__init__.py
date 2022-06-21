from retro_data_structures.enums import echoes
from retro_data_structures.formats.script_object import ScriptInstanceHelper
from retro_data_structures.properties.echoes.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.echoes.archetypes.WeaponVulnerability import WeaponVulnerability
from retro_data_structures.properties.echoes.objects.Door import Door

from open_prime_rando.echoes.asset_ids.temple_grounds import HIVE_ACCESS_TUNNEL_MREA

from open_prime_rando.patcher_editor import PatcherEditor

def change_door_to_light(door: ScriptInstanceHelper):
    door_props: Door = door.get_properties()
    door_props.shell_color.r = 1.0
    door_props.shell_color.g = 1.0
    door_props.shell_color.b = 1.0

    v = door_props.vulnerability
    types = ["power", "dark", "annihilator", "bomb", "power_bomb", "missile", "power_charge", "entangler",
             "sonic_boom", "super_missle", "black_hole", "imploder"]
    for t in types:
        dmg_vuln: WeaponVulnerability = getattr(v, t)
        dmg_vuln.damage_multiplier = 0.0
        dmg_vuln.effect = echoes.Effect.Reflect

    for t in ["light", "light_blast", "sunburst"]:
        dmg_vuln: WeaponVulnerability = getattr(v, t)
        dmg_vuln.damage_multiplier = 100.0
        dmg_vuln.effect = echoes.Effect.Normal

    door.set_properties(door_props)


def apply_door_rando(editor: PatcherEditor, door_rando_configuration: list[dict]):
    access_tunnel = editor.get_mrea(HIVE_ACCESS_TUNNEL_MREA)

    docks = {}
    doors = {}

    for script_layer in access_tunnel.script_layers:
        for instance in script_layer.instances:
            # try:
            #     print("{}: {}".format(instance, instance.name))
            #     # print(instance.get_properties())
            # except Exception as e:
            #     print("{}: {} --- {}".format(instance, e, instance._raw.instance.base_property.hex()))
            #     continue

            if instance.type == "DOCK":
                docks[instance.id] = instance

            if instance.type == "DOOR":
                doors[instance.id] = instance

    for door in doors.values():
        change_door_to_light(door)