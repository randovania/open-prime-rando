import struct
from enum import IntEnum
from typing import NamedTuple


class DoorIconColors(NamedTuple):
    surface_color: int
    outline_color: int | None = None  # unused


class DoorMapIcon(IntEnum):
    # vanilla
    Normal = 0
    Missile = 1
    Dark = 2
    Annihilator = 3
    Light = 4
    SuperMissile = 5
    SeekerMissile = 6
    PowerBomb = 7

    # planetary energy
    AgonEnergy = -1
    TorvusEnergy = -2
    SanctuaryEnergy = -3

    # visors
    ScanVisor = -4
    DarkVisor = -5
    EchoVisor = -6

    # misc
    Disabled = -7
    ScrewAttack = -8
    Bomb = -9
    Boost = -10
    Grapple = -11

    @property
    def colors(self) -> DoorIconColors:
        return _ALL_COLORS.get(self, DoorIconColors(0xff00ffff))

    @staticmethod
    def get_surface_colors_as_bytes() -> bytes:
        colors = [icon.colors.surface_color for icon in sorted(DoorMapIcon)]
        return struct.pack(">" + "L" * len(colors), *colors)

    @staticmethod
    def get_door_index_bounds() -> tuple[int, int]:
        return min(*DoorMapIcon), max(*DoorMapIcon)


_ALL_COLORS = {
    DoorMapIcon.Normal: DoorIconColors(0x3379bfff),
    DoorMapIcon.Missile: DoorIconColors(0xd63333ff),
    DoorMapIcon.Dark: DoorIconColors(0x000000ff, 0x898989ff),
    DoorMapIcon.Annihilator: DoorIconColors(0x4b4b4bff),
    DoorMapIcon.Light: DoorIconColors(0xffffffff),
    DoorMapIcon.SuperMissile: DoorIconColors(0x50a148ff),
    DoorMapIcon.SeekerMissile: DoorIconColors(0x794f77ff),
    DoorMapIcon.PowerBomb: DoorIconColors(0xeae50bff),

    DoorMapIcon.AgonEnergy: DoorIconColors(0xa45600ff),
    DoorMapIcon.TorvusEnergy: DoorIconColors(0x4e9761ff),
    DoorMapIcon.SanctuaryEnergy: DoorIconColors(0x56789dff),

    DoorMapIcon.ScanVisor: DoorIconColors(0x007f7fff),
    DoorMapIcon.DarkVisor: DoorIconColors(0x660000ff),
    DoorMapIcon.EchoVisor: DoorIconColors(0xcc7a00ff),

    DoorMapIcon.ScrewAttack: DoorIconColors(0xed94d4ff),
    DoorMapIcon.Bomb: DoorIconColors(0x55557fff),
    DoorMapIcon.Boost: DoorIconColors(0xff5500ff),
    # DoorMapIcon.Grapple: None,

    DoorMapIcon.Disabled: DoorIconColors(0x202020ff),
}
