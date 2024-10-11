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
        return _ALL_COLORS.get(self, DoorIconColors(0xFF00FFFF))

    @staticmethod
    def get_surface_colors_as_bytes() -> bytes:
        colors = [icon.colors.surface_color for icon in sorted(DoorMapIcon)]
        return struct.pack(">" + "L" * len(colors), *colors)

    @staticmethod
    def get_door_index_bounds() -> tuple[int, int]:
        return min(*DoorMapIcon), max(*DoorMapIcon)


_ALL_COLORS = {
    DoorMapIcon.Normal: DoorIconColors(0x3379BFFF),
    DoorMapIcon.Missile: DoorIconColors(0xD63333FF),
    DoorMapIcon.Dark: DoorIconColors(0x000000FF, 0x898989FF),
    DoorMapIcon.Annihilator: DoorIconColors(0x4B4B4BFF),
    DoorMapIcon.Light: DoorIconColors(0xFFFFFFFF),
    DoorMapIcon.SuperMissile: DoorIconColors(0x50A148FF),
    DoorMapIcon.SeekerMissile: DoorIconColors(0x794F77FF),
    DoorMapIcon.PowerBomb: DoorIconColors(0xEAE50BFF),
    DoorMapIcon.AgonEnergy: DoorIconColors(0xA45600FF),
    DoorMapIcon.TorvusEnergy: DoorIconColors(0x4E9761FF),
    DoorMapIcon.SanctuaryEnergy: DoorIconColors(0x56789DFF),
    DoorMapIcon.ScanVisor: DoorIconColors(0x007F7FFF),
    DoorMapIcon.DarkVisor: DoorIconColors(0x660000FF),
    DoorMapIcon.EchoVisor: DoorIconColors(0xCC7A00FF),
    DoorMapIcon.ScrewAttack: DoorIconColors(0xED94D4FF),
    DoorMapIcon.Bomb: DoorIconColors(0x55557FFF),
    DoorMapIcon.Boost: DoorIconColors(0xFF5500FF),
    # DoorMapIcon.Grapple: None,
    DoorMapIcon.Disabled: DoorIconColors(0x202020FF),
}
