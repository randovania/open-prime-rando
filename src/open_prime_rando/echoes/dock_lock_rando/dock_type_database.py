import dataclasses

from retro_data_structures.enums.echoes import VisorFlags
from retro_data_structures.properties.echoes.core.Color import Color
from retro_data_structures.properties.echoes.core.Vector import Vector

from open_prime_rando.echoes.dock_lock_rando import dock_type
from open_prime_rando.echoes.dock_lock_rando.map_icons import DoorMapIcon
from open_prime_rando.echoes.vulnerabilities import normal_vuln, resist_all_vuln, vulnerable, vulnerable_no_splash

normal_door_model = 0x6B78FD92
dark_door_model = 0xbbcf134d
annihilator_door_model = 0xa50c7238

blast_collision_box = Vector(0.35, 5.0, 4.0)
blast_collision_offset = Vector(-2 / 3, 0, 2.0)

DOCK_TYPES: dict[str, dock_type.DoorType] = {
    "Normal": dock_type.NormalDoorType(
        name="Normal",
        vulnerability=normal_vuln,
        shell_color=Color(0, 1, 1, 1),
        map_icon=DoorMapIcon.Normal,
    ),
    "Dark": dock_type.NormalDoorType(
        name="Dark",
        vulnerability=dataclasses.replace(resist_all_vuln, dark=vulnerable, entangler=vulnerable,
                                          black_hole=vulnerable),
        shell_model=dark_door_model,
        shell_color=Color(1, 1, 1, 1),
        scan_text=(
            "There is a Blast Shield on the door blocking access. ",
            "Analysis indicates that the Blast Shield is invulnerable to most weapons. Dark energy may damage it."
        ),
        map_icon=DoorMapIcon.Dark
    ),
    "Light": dock_type.NormalDoorType(
        name="Light",
        vulnerability=dataclasses.replace(resist_all_vuln, light=vulnerable, light_blast=vulnerable,
                                          sunburst=vulnerable),
        shell_color=Color(1, 1, 1, 1),
        scan_text=(
            "There is a Blast Shield on the door blocking access. ",
            "Analysis indicates that the Blast Shield is invulnerable to most weapons. Light energy may damage it."
        ),
        map_icon=DoorMapIcon.Light
    ),
    "Annihilator": dock_type.NormalDoorType(
        name="Annihilator",
        vulnerability=dataclasses.replace(resist_all_vuln, annihilator=vulnerable, sonic_boom=vulnerable,
                                          imploder=vulnerable),
        shell_model=annihilator_door_model,
        shell_color=Color(1, 1, 1, 1),
        scan_text=(
            "There is a Blast Shield on the door blocking access. ",
            "Analysis indicates that the Blast Shield is invulnerable to most weapons. "
            "A mix of light and dark energy may damage it."
        ),
        map_icon=DoorMapIcon.Annihilator
    ),
    "Disabled": dock_type.NormalDoorType(
        name="Disabled",
        vulnerability=resist_all_vuln,
        shell_color=Color(0, 0, 0, 0),
        scan_text=(
            "Door system access denied.",
            "Unable to bypass security codes. Seek an alternate exit."
        ),
        map_icon=DoorMapIcon.Disabled
    ),
    "Missile": dock_type.VanillaBlastShieldDoorType(
        name="Missile",
        vulnerability=dataclasses.replace(resist_all_vuln, missile=vulnerable),
        shell_color=Color(1, 0, 0, 1),
        scan_text=(
            "There is a Blast Shield on the door blocking access. ",
            "Analysis indicates that the Blast Shield is invulnerable to most weapons. A Missile blast may damage it."
        ),
        map_icon=DoorMapIcon.Missile,
        shield_model=0xBFB4A8EE,
    ),
    "SuperMissile": dock_type.VanillaBlastShieldDoorType(
        name="SuperMissile",
        vulnerability=dataclasses.replace(resist_all_vuln, super_missle=vulnerable),
        shell_color=Color(0, 1, 0, 1),
        scan_text=(
            "There is a Blast Shield on the door blocking access. ",
            "Analysis indicates that the Blast Shield is invulnerable to most weapons. "
            "A Super Missile blast may damage it."
        ),
        map_icon=DoorMapIcon.SuperMissile,
        shield_model=0xF115F575,
    ),
    "PowerBomb": dock_type.VanillaBlastShieldDoorType(
        name="PowerBomb",
        vulnerability=dataclasses.replace(resist_all_vuln, power_bomb=vulnerable),
        shell_color=Color(1, 0.94, 0, 1),
        scan_text=(
            "There is a Blast Shield on the door blocking access. ",
            "Analysis indicates that the Blast Shield is invulnerable to most weapons. A Power Bomb may damage it."
        ),
        map_icon=DoorMapIcon.PowerBomb,
        shield_model=0xC2E4F075,
    ),
    "SeekerMissile": dock_type.SeekerBlastShieldDoorType(
        name="SeekerMissile",
        vulnerability=dataclasses.replace(resist_all_vuln, missile=vulnerable),
        shell_color=Color(0.5, 0, 0.64, 1),
        scan_text=(
            "There is a Blast Shield on the door blocking access. ",
            "Analysis indicates that the Blast Shield is invulnerable to most weapons. "
            "Five simultaneous Missile blasts may damage it."
        ),
        map_icon=DoorMapIcon.SeekerMissile,
        shield_model=0x56F4208B,
    ),
    "ScrewAttack": dock_type.BlastShieldDoorType(
        name="ScrewAttack",
        vulnerability=dataclasses.replace(resist_all_vuln, screw_attack=vulnerable),
        shell_model=normal_door_model,
        shell_color=Color(0.93, 0.58, 0.83, 1),
        scan_text=(
            "There is a Blast Shield on the door blocking access. ",
            "Analysis indicates that the Blast Shield is invulnerable to most weapons. The Screw Attack may damage it."
        ),
        map_icon=DoorMapIcon.ScrewAttack,
        shield_model="screw_attack",
    ),
    "Bomb": dock_type.BlastShieldDoorType(
        name="Bomb",
        vulnerability=dataclasses.replace(resist_all_vuln, bomb=vulnerable),
        shell_model=normal_door_model,
        shell_color=Color(1/3, 1/3, 0.5, 1),
        scan_text=(
            "There is a Blast Shield on the door blocking access. ",
            "Analysis indicates that the Blast Shield is invulnerable to most weapons. "
            "A Morph Ball Bomb blast may damage it."
        ),
        map_icon=DoorMapIcon.Bomb,
        shield_model="morph_ball_bombs",
    ),
    "Boost": dock_type.BlastShieldDoorType(
        name="Boost",
        vulnerability=dataclasses.replace(
            resist_all_vuln,
            boost_ball=vulnerable,
            cannon_ball=vulnerable_no_splash
        ),
        shell_model=normal_door_model,
        shell_color=Color(1, 1/3, 0, 1),
        scan_text=(
            "There is a Blast Shield on the door blocking access. ",
            "Analysis indicates that the Blast Shield is invulnerable to most weapons. The Boost Ball may damage it."
        ),
        map_icon=DoorMapIcon.Boost,
        shield_model="boost_ball",
    ),
    "Grapple": dock_type.GrappleDoorType(
        name="Grapple",
        vulnerability=resist_all_vuln,
        shell_model=annihilator_door_model,
        shell_color=Color(1, 0, 0, 1),
        scan_text=(
            "There is a Blast Shield on the door blocking access. ",
            "Analysis indicates that the Blast Shield is invulnerable to weapon fire, but is weakly secured. "
            "The Grapple Beam may be able to remove it."
        ),
        map_icon=DoorMapIcon.Grapple,
        shield_model=0x56F4208B,
    ),
    "Darkburst": dock_type.BlastShieldDoorType(
        name="Darkburst",
        vulnerability=dataclasses.replace(resist_all_vuln, black_hole=vulnerable),
        shell_model=dark_door_model,
        shell_color=Color(1, 1, 1, 1),
        scan_text=(
            "There is a Blast Shield on the door blocking access. ",
            "Analysis indicates that the Blast Shield is invulnerable to most weapons. "
            "A massive burst of dark energy may damage it."
        ),
        map_icon=DoorMapIcon.Dark,
        shield_model="darkburst",
    ),
    "Sunburst": dock_type.BlastShieldDoorType(
        name="Sunburst",
        vulnerability=dataclasses.replace(resist_all_vuln, sunburst=vulnerable),
        shell_model=normal_door_model,
        shell_color=Color(1, 1, 1, 1),
        scan_text=(
            "There is a Blast Shield on the door blocking access. ",
            "Analysis indicates that the Blast Shield is invulnerable to most weapons. "
            "A massive burst of light energy may damage it."
        ),
        map_icon=DoorMapIcon.Light,
        shield_model="sunburst",
    ),
    "SonicBoom": dock_type.BlastShieldDoorType(
        name="SonicBoom",
        vulnerability=dataclasses.replace(resist_all_vuln, imploder=vulnerable),
        shell_model=annihilator_door_model,
        shell_color=Color(1, 1, 1, 1),
        scan_text=(
            "There is a Blast Shield on the door blocking access. ",
            "Analysis indicates that the Blast Shield is invulnerable to most weapons. "
            "A massive burst of light and dark energy may damage it."
        ),
        map_icon=DoorMapIcon.Annihilator,
        shield_model="sonic_boom",
    ),
    "AgonEnergy": dock_type.PlanetaryEnergyDoorType(
        name="AgonEnergy",
        vulnerability=resist_all_vuln,
        shell_color=Color(0.64, 0.34, 0, 1),
        scan_text=(
            "There is a Luminoth barrier on the door blocking access. ",
            "Analysis indicates that the barrier is linked to the energy of Agon. Return the energy to the Agon Temple."
        ),
        map_icon=DoorMapIcon.AgonEnergy,
        planetary_energy_item_id=-1  # TODO
    ),
    "TorvusEnergy": dock_type.PlanetaryEnergyDoorType(
        name="TorvusEnergy",
        vulnerability=resist_all_vuln,
        shell_color=Color(0.31, 0.59, 38, 1),
        scan_text=(
            "There is a Luminoth barrier on the door blocking access. ",
            "Analysis indicates that the barrier is linked to the energy of Torvus. "
            "Return the energy to the Torvus Temple."
        ),
        map_icon=DoorMapIcon.TorvusEnergy,
        planetary_energy_item_id=-1  # TODO
    ),
    "SanctuaryEnergy": dock_type.PlanetaryEnergyDoorType(
        name="SanctuaryEnergy",
        vulnerability=resist_all_vuln,
        shell_color=Color(0.64, 0.34, 0, 1),
        scan_text=(
            "There is a Luminoth barrier on the door blocking access. ",
            "Analysis indicates that the barrier is linked to the energy of Sanctuary. "
            "Return the energy to the Sanctuary Temple."
        ),
        map_icon=DoorMapIcon.AgonEnergy,
        planetary_energy_item_id=-1  # TODO
    ),
    "EchoVisor": dock_type.EchoVisorDoorType(
        name="EchoVisor",
        vulnerability=normal_vuln,
        shell_model=dark_door_model,
        shell_color=Color(1/16, 1/16, 1/16, 1),
        scan_text=(
            "There is a Blast Shield on the door blocking access. ",
            "Sonic detection gear needed to interface with this system. "
            "Neutralizing the control emitter may disable it."
        ),
        map_icon=DoorMapIcon.EchoVisor,
        shield_model="echo_visor",
        visor_flags=VisorFlags.Echo,
        player_controller_proxy=8,
    ),
    "DarkVisor": dock_type.DarkVisorDoorType(
        name="DarkVisor",
        vulnerability=normal_vuln,
        shell_model=dark_door_model,
        shell_color=Color(1, 0, 0, 1),
        scan_text=(
            "There is a Blast Shield on the door blocking access. ",
            "Scans indicate presence of a control system. "
            "Interface method unknown. Control units not present in the visible spectrum or current timespace. "
        ),
        map_icon=DoorMapIcon.DarkVisor,
        shield_model="dark_visor",
        visor_flags=VisorFlags.Dark,
        player_controller_proxy=7,
    ),
    "Cannon": dock_type.BlastShieldDoorType(
        name="Cannon",
        vulnerability=dataclasses.replace(
            resist_all_vuln,
            cannon_ball=vulnerable_no_splash
        ),
        shell_model=normal_door_model,
        shell_color=Color(1, 1/3, 0, 1),
        scan_text=(
            "There is a Blast Shield on the door blocking access. ",
            "Analysis indicates that the Blast Shield is invulnerable to most weapons. The Cannon Ball may damage it."
        ),
        map_icon=DoorMapIcon.Boost,
        shield_model="cannon_ball",
    ),
    "Charge": dock_type.BlastShieldDoorType(
        name="Charge",
        vulnerability=dataclasses.replace(
            resist_all_vuln,
            power_charge=vulnerable,
            entangler=vulnerable,
            light_blast=vulnerable,
            sonic_boom=vulnerable,
        ),
        shell_model=normal_door_model,
        shell_color=Color(0, 1, 1, 1),
        scan_text=(
            "There is a Blast Shield on the door blocing access. ",
            "Analysis indicates that the Blast Shield is invulnerable to normal beam fire. "
            "The Charge Beam may damage it."
        ),
        map_icon=DoorMapIcon.Normal,
        shield_model="charge_beam"
    ),
    "Power": dock_type.NormalDoorType(
        name="Power",
        vulnerability=dataclasses.replace(resist_all_vuln, power=vulnerable),
        shell_color=Color(1, 0.8, 0, 1),
        scan_text=(
            "There is a Blast Shield on the door blocking access. ",
            "Analysis indicates that the Blast Shield is invulnerable to light and dark energy. "
            "The Power Beam may damage it."
        ),
        map_icon=DoorMapIcon.PowerBomb # TODO: give it its own?
    )
}
