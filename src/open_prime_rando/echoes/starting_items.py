from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

import pydantic
from retro_data_structures.enums.echoes import PlayerItemEnum
from retro_data_structures.properties.echoes.objects import SpawnPoint

if TYPE_CHECKING:
    from retro_data_structures.formats.mrea import Area
    from retro_data_structures.formats.script_object import ScriptInstance
    from retro_data_structures.properties.field_reflection import FieldReflection

    from open_prime_rando.echoes.rando_configuration import AreaReference
    from open_prime_rando.patcher_editor import PatcherEditor

# 0x161898dc and 0x32f5e918 are assigned to no items at all

_property_to_enum: dict[int, PlayerItemEnum] = {
    0x9ACA45BC: PlayerItemEnum.PowerBeam,
    0x92BB94B7: PlayerItemEnum.DarkBeam,
    0x6BE340BA: PlayerItemEnum.LightBeam,
    0xC73B2C90: PlayerItemEnum.AnnihilatorBeam,
    0xEFD4DABE: PlayerItemEnum.SuperMissile,
    0x9B06BD3C: PlayerItemEnum.Darkburst,
    0x6D7172BF: PlayerItemEnum.Sunburst,
    0x16D89ACC: PlayerItemEnum.SonicBoom,
    0xEA86A2B9: PlayerItemEnum.ChargeCombo,
    0x26A5E3C1: PlayerItemEnum.CombatVisor,
    0x9DE8731D: PlayerItemEnum.ScanVisor,
    0x3B0AB10B: PlayerItemEnum.DarkVisor,
    0x95A30488: PlayerItemEnum.EchoVisor,
    0x0AB603F7: PlayerItemEnum.VariaSuit,
    0x4DA55282: PlayerItemEnum.DarkSuit,
    0xB4FD868F: PlayerItemEnum.LightSuit,
    0x3EC5A9F5: PlayerItemEnum.MorphBall,
    0x8C98247D: PlayerItemEnum.BoostBall,
    0xBD8B547C: PlayerItemEnum.SpiderBall,
    0x53387689: PlayerItemEnum.MorphBallBomb,
    0x57EB9E8B: PlayerItemEnum.LightBomb,
    0xAEB34A86: PlayerItemEnum.DarkBomb,
    0xFB33F2A1: PlayerItemEnum.AnnihilatorBomb,
    0x4B15EB9A: PlayerItemEnum.ChargeBeam,
    0x44FBB19C: PlayerItemEnum.GrappleBeam,
    0xF55BE12C: PlayerItemEnum.SpaceJumpBoots,
    0xBC25CAED: PlayerItemEnum.GravityBoost,
    0x0A6B376F: PlayerItemEnum.SeekerLauncher,
    0xD8A9BBCB: PlayerItemEnum.ScrewAttack,
    0x7D1C9685: PlayerItemEnum.EnergyTransferModulePickup,
    0x8F6CDCF9: PlayerItemEnum.SkyTempleKey1,
    0x9DD97317: PlayerItemEnum.SkyTempleKey2,
    0x25651472: PlayerItemEnum.SkyTempleKey3,
    0xB8B22CCB: PlayerItemEnum.SkyTempleKey4,
    0x000E4BAE: PlayerItemEnum.SkyTempleKey5,
    0x12BBE440: PlayerItemEnum.SkyTempleKey6,
    0xAA078325: PlayerItemEnum.SkyTempleKey7,
    0xF2649373: PlayerItemEnum.SkyTempleKey8,
    0x4AD8F416: PlayerItemEnum.SkyTempleKey9,
    0xC271CFBC: PlayerItemEnum.DarkAgonKey1,
    0xD0C46052: PlayerItemEnum.DarkAgonKey2,
    0x68780737: PlayerItemEnum.DarkAgonKey3,
    0x6EFFCF82: PlayerItemEnum.DarkTorvusKey1,
    0x7C4A606C: PlayerItemEnum.DarkTorvusKey2,
    0xC4F60709: PlayerItemEnum.DarkTorvusKey3,
    0xC20D622B: PlayerItemEnum.IngHiveKey1,
    0xD0B8CDC5: PlayerItemEnum.IngHiveKey2,
    0x6804AAA0: PlayerItemEnum.IngHiveKey3,
    0x01C397F0: PlayerItemEnum.HealthRefill,
    0xFC6F860C: PlayerItemEnum.EnergyTank,
    0xA6C29B8D: PlayerItemEnum.PowerBomb,
    0xEC7FB0EF: PlayerItemEnum.Missile,
    0xFCECF744: PlayerItemEnum.DarkAmmo,
    0x32052F91: PlayerItemEnum.LightAmmo,
    0x6E4038AB: PlayerItemEnum.ItemPercentage,
    0x14387AAB: PlayerItemEnum.NumPlayersJoined,
    0x068DD545: PlayerItemEnum.NumPlayersInOptionsMenu,
    0xBE31B220: PlayerItemEnum.MiscCounter3,
    0x23E68A99: PlayerItemEnum.MiscCounter4,
    0x8ECB6665: PlayerItemEnum.SwitchWeaponPower,
    0x92C402AB: PlayerItemEnum.SwitchWeaponDark,
    0x7FE26363: PlayerItemEnum.SwitchWeaponLight,
    0xD7F8586A: PlayerItemEnum.SwitchWeaponAnnihilator,
    0x27D254AF: PlayerItemEnum.MultiChargeUpgrade,
    0x19926420: PlayerItemEnum.Invisibility,
    0xCE284C09: PlayerItemEnum.AmpDamage,
    0xDEC999C3: PlayerItemEnum.Invincibility,
    0x66AE338E: PlayerItemEnum.UnknownItem60,
    0x210E495E: PlayerItemEnum.UnknownItem61,
    0x1C6E60EE: PlayerItemEnum.UnknownItem62,
    0xAE4EBCFE: PlayerItemEnum.UnknownItem63,
    0x5351DBA5: PlayerItemEnum.FragCount,
    0x02DB9A0A: PlayerItemEnum.DiedCount,
    0x7B980651: PlayerItemEnum.ArchenemyCount,
    0xE9861C49: PlayerItemEnum.PersistentCounter1,
    0xFB33B3A7: PlayerItemEnum.PersistentCounter2,
    0x438FD4C2: PlayerItemEnum.PersistentCounter3,
    0xDE58EC7B: PlayerItemEnum.PersistentCounter4,
    0x66E48B1E: PlayerItemEnum.PersistentCounter5,
    0x745124F0: PlayerItemEnum.PersistentCounter6,
    0xCCED4395: PlayerItemEnum.PersistentCounter7,
    0x948E53C3: PlayerItemEnum.PersistentCounter8,
    0xD438F8E4: PlayerItemEnum.SwitchVisorCombat,
    0x89E950C4: PlayerItemEnum.SwitchVisorScan,
    0x2F0B92D2: PlayerItemEnum.SwitchVisorDark,
    0x81A22751: PlayerItemEnum.SwitchVisorEcho,
    0xDB8F0E87: PlayerItemEnum.CoinAmplifier,
    0xAF6F361A: PlayerItemEnum.CoinCounter,
    0xAE8DEE81: PlayerItemEnum.UnlimitedMissiles,
    0xD1FFB49F: PlayerItemEnum.UnlimitedBeamAmmo,
    0xBC51DE4B: PlayerItemEnum.DarkShield,
    0x88414F93: PlayerItemEnum.LightShield,
    0xFBE21590: PlayerItemEnum.AbsorbAttack,
    0xD0B6A007: PlayerItemEnum.DeathBall,
    0xC45848FE: PlayerItemEnum.ScanVirus,
    0x92B916D7: PlayerItemEnum.VisorStatic,
    0xA6257CD8: PlayerItemEnum.DisableBeamAmmo,
    0x6BF24C24: PlayerItemEnum.DisableMissiles,
    0x1CE95541: PlayerItemEnum.DisableBall,
    0x5DD9004D: PlayerItemEnum.DisableSpaceJump,
    0xF64F1DBD: PlayerItemEnum.UnknownItem94,
    0x76000D1E: PlayerItemEnum.HackedEffect,
    0x85AB52BC: PlayerItemEnum.CannonBall,
    0x711C150F: PlayerItemEnum.VioletTranslator,
    0x63A9BAE1: PlayerItemEnum.AmberTranslator,
    0xDB15DD84: PlayerItemEnum.EmeraldTranslator,
    0x46C2E53D: PlayerItemEnum.CobaltTranslator,
}


class StartingItemConfig(pydantic.BaseModel):
    item: PlayerItemEnum
    """The item to configure for."""

    capacity: int
    """The capacity you'll start with."""

    amount: int | None = None
    """The amount you'll start with. Defaults to capacity."""


def _get_first_spawn(area: Area) -> tuple[ScriptInstance, SpawnPoint]:
    """
    Gets the script object that is a SpawnPoint with first_spawn set that belongs to an active layer.
    Raises if none found.
    """

    for layer in area.layers:
        if layer.active:
            for instance in layer.instances:
                if instance.script_type == SpawnPoint:
                    prop = instance.get_properties_as(SpawnPoint)
                    if prop.first_spawn:
                        return instance, prop

    raise RuntimeError(f"No first spawn found in {area}")


def edit_starting_items(
    editor: PatcherEditor,
    starting_area: AreaReference,
    items_config: list[StartingItemConfig],
) -> None:
    """
    Changes the SpawnPoint in the given area to start with the given items.
    """
    mlvl = editor.get_mlvl(starting_area.mlvl_id)
    area = mlvl.get_area(starting_area.mrea_id)

    capacity_by_enum = {}
    amount_by_enum = {}

    for entry in items_config:
        capacity_by_enum[entry.item] = entry.capacity
        amount_by_enum[entry.item] = entry.amount or entry.capacity

    # FIXME: Landing Site is not working properly
    instance, prop = _get_first_spawn(area)

    for field in dataclasses.fields(prop.capacity):
        reflection: FieldReflection[int] = field.metadata["reflection"]

        if reflection.id in _property_to_enum:
            e = _property_to_enum[reflection.id]
            capacity = capacity_by_enum.get(e, 0)
            amount = amount_by_enum.get(e, 0)
        else:
            amount, capacity = 0, 0

        setattr(prop.capacity, field.name, capacity)
        setattr(prop.amount, field.name, amount)

    instance.set_properties(prop)
