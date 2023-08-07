from retro_data_structures.enums.echoes import WorldLightingOptions
from retro_data_structures.properties.echoes.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.echoes.core.Color import Color
from retro_data_structures.properties.echoes.core.Vector import Vector

from open_prime_rando.echoes.pickups.models import ModelLighting, ModelTransform, PickupModel

PICKUP_MODELS = {
    "PowerBeam": PickupModel(
        # yellow annihilator
        model=0x6FE2E8A0,
        transform=ModelTransform(
            scale=Vector(1.75, 1.75, 1.75),
            rotation=Vector(0.0, 0.0, -78.7218),
        ),
        lighting=ModelLighting(
            ambient_color=Color(1.0, 1.0, 0.0, 0.75)
        ),
        auto_spin=True,
    ),
    "ChargeBeam": PickupModel(
        model=0x4F60CD5B,
        transform=ModelTransform(
            scale=Vector(5.0, 5.0, 5.0),
        ),
        auto_spin=True,
    ),
    "DarkBeam": PickupModel(
        model=0x97F5CAAE,
        animation=AnimationParameters(
            ancs=0x842C0BCB,
        ),
        transform=ModelTransform(
            scale=Vector(3.0, 3.0, 3.0),
        ),
    ),
    "LightBeam": PickupModel(
        model=0x0ADC164A,
        animation=AnimationParameters(
            ancs=0x6E571BEB,
        ),
        transform=ModelTransform(
            scale=Vector(4.0, 4.0, 4.0),
            orbit_offset=Vector(0.0, 0.0, 1.0),
        )
    ),
    "AnnihilatorBeam": PickupModel(
        model=0x6FE2E8A0,
        animation=AnimationParameters(
            ancs=0x4C4B3D9D,
        ),
        transform=ModelTransform(
            scale=Vector(1.75, 1.75, 1.75),
            rotation=Vector(0.0, 0.0, -78.7218),
        )
    ),
    "SuperMissile": PickupModel(
        model=0x546A6490,
        animation=AnimationParameters(
            ancs=0x1CA5927A,
        )
    ),
    "Darkburst": PickupModel(
        model=0xF6510F11,
        animation=AnimationParameters(
            ancs=0x2EFD9A18,
        )
    ),
    "Sunburst": PickupModel(
        model=0x43BB4262,
        animation=AnimationParameters(
            ancs=0x20BB6D93,
        )
    ),
    "SonicBoom": PickupModel(
        model=0xF1207641,
        animation=AnimationParameters(
            ancs=0x345E7936,
        )
    ),
    "CombatVisor": PickupModel(
        model=0x0B7E6CA9,
        animation=AnimationParameters(
            ancs=0x851B526E,
            character_index=1,
        ),
    ),
    "ScanVisor": PickupModel(
        model=0xAFC70004,
        animation=AnimationParameters(
            ancs=0x851B526E,
            character_index=2,
        ),
    ),
    "DarkVisor": PickupModel(
        model=0x23B83F21,
        animation=AnimationParameters(
            ancs=0x851B526E,
        ),
    ),
    "EchoVisor": PickupModel(
        model=0x2ED9AD89,
        animation=AnimationParameters(
            ancs=0x89E3C4E4,
        )
    ),
    "VariaSuit": PickupModel(
        model=0xCD995C16,
        animation=AnimationParameters(
            ancs=0xA3E787B7,
        ),
        transform=ModelTransform(
            scale=Vector(3.0, 3.0, 3.0),
        ),
        auto_spin=True,
    ),
    "DarkSuit": PickupModel(
        model=0x485CF5DE,
        animation=AnimationParameters(
            ancs=0xA3E787B7,
            character_index=1,
        ),
        transform=ModelTransform(
            scale=Vector(3.0, 3.0, 3.0),
        ),
    ),
    "LightSuit": PickupModel(
        model=0xA26A5FBC,
        animation=AnimationParameters(
            ancs=0xA3E787B7,
            character_index=3,
        ),
        transform=ModelTransform(
            scale=Vector(3.0, 3.0, 3.0),
        ),
    ),
    "MassiveDamage": PickupModel(
        model=0xCD995C16,
        animation=AnimationParameters(
            ancs=0xA3E787B7,
        ),
        transform=ModelTransform(
            scale=Vector(3.0, 3.0, 3.0),
        ),
        auto_spin=True,
        lighting=ModelLighting(
            unk_bool=False,
            ambient_color=Color(1.0, 0.0, 0.0, 1.0),
        ),
    ),
    "MorphBall": PickupModel(
        model=0xED3FCD53,
        animation=AnimationParameters(
            ancs=0x1965B86B,
        ),
        lighting=ModelLighting(
            cast_shadow=False,
            unk_bool=False,
        ),
    ),
    "BoostBall": PickupModel(
        model=0xED3FCD53,
        animation=AnimationParameters(
            ancs=0x1965B86B,
        ),
        transform=ModelTransform(
            scale=Vector(1.5, 1.5, 1.5),
        ),
        lighting=ModelLighting(
            cast_shadow=False,
            unk_bool=False,
        ),
    ),
    "CannonBall": PickupModel(
        model=0xED3FCD53,
        animation=AnimationParameters(
            ancs=0x1965B86B,
        ),
        transform=ModelTransform(
            scale=Vector(1.5, 1.5, 1.5),
        ),
        lighting=ModelLighting(
            cast_shadow=False,
            unk_bool=False,
            ambient_color=Color(1.0, 0.5, 0.0, 1.0),
        ),
    ),
    "SpiderBall": PickupModel(
        model=0x0303BA4C,
        animation=AnimationParameters(
            ancs=0x732E4CFF,
        ),
        lighting=ModelLighting(
            cast_shadow=False,
            unk_bool=False,
        ),
    ),
    "MorphBallBomb": PickupModel(
        model=0x2CF11C61,
        animation=AnimationParameters(
            ancs=0xC566DE95,
        ),
        transform=ModelTransform(
            scale=Vector(2.0, 2.0, 2.0),
        ),
    ),
    "PowerBomb": PickupModel(
        model=0xA42AE9AE,
        animation=AnimationParameters(
            ancs=0xD03D177C,
        ),
        transform=ModelTransform(
            scale=Vector(5.0, 5.0, 5.0),
        ),
    ),
    "PowerBombExpansion": PickupModel(
        model=0x5D17CE58,
        animation=AnimationParameters(
            ancs=0xEF3B8B2C,
        ),
        transform=ModelTransform(
            scale=Vector(1.5, 1.5, 1.5),
        )
    ),
    "MissileExpansion": PickupModel(
        model=0x5E3C8794,
        animation=AnimationParameters(
            ancs=0x19FA37B1,
        ),
        transform=ModelTransform(
            orbit_offset=Vector(0.0, 0.0, 1.5),
        ),
        lighting=ModelLighting(
            use_world_lighting=WorldLightingOptions.Unknown2,
            use_old_lighting=True,
        ),
    ),
    "MissileExpansionLarge": PickupModel(
        model=0x5E3C8794,
        animation=AnimationParameters(
            ancs=0x19FA37B1,
        ),
        transform=ModelTransform(
            orbit_offset=Vector(0.0, 0.0, 1.5),
            scale=Vector(2.0, 2.0, 2.0),
        ),
        lighting=ModelLighting(
            use_world_lighting=WorldLightingOptions.Unknown2,
            use_old_lighting=True,
        ),
    ),
    "MissileExpansionPrime1": PickupModel(
        model=0x2D7E6590,
        animation=AnimationParameters(
            ancs=0xA9B8E446,
        ),
        transform=ModelTransform(
            orbit_offset=Vector(0.0, 0.0, 1.5),
        ),
        lighting=ModelLighting(
            use_world_lighting=WorldLightingOptions.Unknown2,
            use_old_lighting=True,
        ),
    ),
    "MissileLauncher": PickupModel(
        model=0x2D7E6590,
        animation=AnimationParameters(
            ancs=0xA9B8E446,
        ),
        transform=ModelTransform(
            orbit_offset=Vector(0.0, 0.0, 1.0),
        ),
        lighting=ModelLighting(
            cast_shadow=False,
            unk_bool=False,
        ),
    ),
    "SeekerLauncher": PickupModel(
        model=0x780437B1,
        animation=AnimationParameters(
            ancs=0x157041D6,
        ),
        lighting=ModelLighting(
            cast_shadow=False,
            unk_bool=False,
        ),
    ),
    "UnlimitedMissiles": PickupModel(
        model=0x2D7E6590,
        animation=AnimationParameters(
            ancs=0xA9B8E446,
        ),
        transform=ModelTransform(
            orbit_offset=Vector(0.0, 0.0, 1.0),
            scale=Vector(1.4, 1.4, 1.4),
        ),
        lighting=ModelLighting(
            cast_shadow=False,
            unk_bool=False,
        ),
    ),
    "GrappleBeam": PickupModel(
        model=0xB95E4D08,
        animation=AnimationParameters(
            ancs=0xB3EED82D,
        ),
        transform=ModelTransform(
            scale=Vector(2.5, 2.5, 2.5),
        ),
    ),
    "SpaceJumpBoots": PickupModel(
        model=0xD47FE863,
        animation=AnimationParameters(
            ancs=0x9CF6CCDC,
        ),
        transform=ModelTransform(
            scale=Vector(4.0, 4.0, 4.0),
        ),
    ),
    "GravityBoost": PickupModel(
        model=0xB4568F1C,
        animation=AnimationParameters(
            ancs=0x94228333,
        ),
        transform=ModelTransform(
            scale=Vector(2.0, 2.0, 2.0),
        ),
    ),
    "ScrewAttack": PickupModel(
        model=0x2EB530B0,
        animation=AnimationParameters(
            ancs=0xF0562FF6,
        ),
        transform=ModelTransform(
            rotation=Vector(0.0, 0.0, 78.13),
            scale=Vector(2.0, 2.0, 2.0),
        ),
    ),
    "EnergyTransferModule": PickupModel(
        model=0xDE702243,
        scan_model=0xB82E8DBC,
        transform=ModelTransform(
            scale=Vector(0.2, 0.2, 0.2),
        ),
    ),
    "BeamAmmoExpansion": PickupModel(
        model=0x352C8B02,
        animation=AnimationParameters(
            ancs=0x4E00188C,
        ),
    ),
    "DarkBeamAmmoExpansion": PickupModel(
        model="dark_ammo_expansion.CMDL",
        animation=AnimationParameters(
            ancs="dark_ammo_expansion.ANCS",
        ),
    ),
    "LightBeamAmmoExpansion": PickupModel(
        model="light_ammo_expansion.CMDL",
        animation=AnimationParameters(
            ancs="light_ammo_expansion.ANCS",
        ),
    ),
    "UnlimitedBeamAmmo": PickupModel(
        model=0x352C8B02,
        animation=AnimationParameters(
            ancs=0x4E00188C,
        ),
        transform=ModelTransform(
            scale=Vector(1.6, 1.6, 1.6),
        ),
    ),
    "VioletTranslator": PickupModel(
        model="violet_translator.CMDL",
        animation=AnimationParameters(
            ancs=0x851B526E,
            character_index=3,
        ),
    ),
    "AmberTranslator": PickupModel(
        model="amber_translator.CMDL",
        animation=AnimationParameters(
            ancs=0x851B526E,
            character_index=4,
        ),
    ),
    "EmeraldTranslator": PickupModel(
        model="emerald_translator.CMDL",
        animation=AnimationParameters(
            ancs=0x851B526E,
            character_index=5,
        ),
    ),
    "CobaltTranslator": PickupModel(
        model="cobalt_translator.CMDL",
        animation=AnimationParameters(
            ancs=0x851B526E,
            character_index=6,
        ),
    ),
    "EnergyTank": PickupModel(
        model=0xAE3EC144,
        animation=AnimationParameters(
            ancs=0x43564B94,
        ),
    ),
    "EnergyTankSmall": PickupModel(
        model=0xAE3EC144,
        animation=AnimationParameters(
            ancs=0x43564B94,
        ),
        transform=ModelTransform(
            scale=Vector(0.5, 0.5, 0.5),
        )
    ),
    "DarkTempleKey": PickupModel(
        model=0x5C8C5F22,
        animation=AnimationParameters(
            ancs=0x41C2513F,
            character_index=1,
        ),
        transform=ModelTransform(
            rotation=Vector(0.0, 0.0, -90.0),
        ),
        lighting=ModelLighting(
            use_world_lighting=WorldLightingOptions.Unknown2,
            use_old_lighting=True,
        )
    ),
    "SkyTempleKey": PickupModel(
        model=0x5737A308,
        animation=AnimationParameters(
            ancs=0x41C2513F,
            character_index=0,
        ),
        transform=ModelTransform(
            rotation=Vector(0.0, 0.0, -90.0),
        ),
        lighting=ModelLighting(
            use_world_lighting=WorldLightingOptions.Unknown2,
            use_old_lighting=True,
        )
    ),
    "AgonTempleKey": PickupModel(
        model="agon_temple_key.CMDL",
        animation=AnimationParameters(
            ancs=0x41C2513F,
            character_index=2,
        ),
        transform=ModelTransform(
            rotation=Vector(0.0, 0.0, -90.0),
        ),
        lighting=ModelLighting(
            use_world_lighting=WorldLightingOptions.Unknown2,
            use_old_lighting=True,
        )
    ),
    "TorvusTempleKey": PickupModel(
        model="torvus_temple_key.CMDL",
        animation=AnimationParameters(
            ancs=0x41C2513F,
            character_index=3,
        ),
        transform=ModelTransform(
            rotation=Vector(0.0, 0.0, -90.0),
        ),
        lighting=ModelLighting(
            use_world_lighting=WorldLightingOptions.Unknown2,
            use_old_lighting=True,
        )
    ),
    "HiveTempleKey": PickupModel(
        model="hive_temple_key.CMDL",
        animation=AnimationParameters(
            ancs=0x41C2513F,
            character_index=4,
        ),
        transform=ModelTransform(
            rotation=Vector(0.0, 0.0, -90.0),
        ),
        lighting=ModelLighting(
            use_world_lighting=WorldLightingOptions.Unknown2,
            use_old_lighting=True,
        )
    ),
}
