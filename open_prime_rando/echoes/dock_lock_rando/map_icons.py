from enum import IntEnum
import struct
from typing import NamedTuple


class DoorIconColors(NamedTuple):
    surface_color: int
    outline_color: int | None = None # unused


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
        if self == DoorMapIcon.Normal:
            return DoorIconColors(0x3379bfff)
        if self == DoorMapIcon.Missile:
            return DoorIconColors(0xd63333ff)
        if self == DoorMapIcon.Dark:
            return DoorIconColors(0x000000ff, 0x898989ff)
        if self == DoorMapIcon.Annihilator:
            return DoorIconColors(0x4b4b4bff)
        if self == DoorMapIcon.Light:
            return DoorIconColors(0xffffffff)
        if self == DoorMapIcon.SuperMissile:
            return DoorIconColors(0x50a148ff)
        if self == DoorMapIcon.SeekerMissile:
            return DoorIconColors(0x794f77ff)
        if self == DoorMapIcon.PowerBomb:
            return DoorIconColors(0xeae50bff)
        
        if self == DoorMapIcon.AgonEnergy:
            return DoorIconColors(0xa45600ff)
        if self == DoorMapIcon.TorvusEnergy:
            return DoorIconColors(0x4e9761ff)
        if self == DoorMapIcon.SanctuaryEnergy:
            return DoorIconColors(0x56789dff)
        
        if self == DoorMapIcon.ScanVisor:
            return DoorIconColors(0x007f7fff)
        if self == DoorMapIcon.DarkVisor:
            return DoorIconColors(0x660000ff)
        # if self == DoorMapIcon.EchoVisor:
        #     return 
        
        if self == DoorMapIcon.Disabled:
            return DoorIconColors(0x202020ff)
        # if self == DoorMapIcon.ScrewAttack:
        #     return
        # if self == DoorMapIcon.Bomb:
        #     return
        # if self == DoorMapIcon.Boost:
        #     return
        # if self == DoorMapIcon.Grapple:
        #     return
        
        return DoorIconColors(0xff00ffff)
    
    @staticmethod
    def get_surface_colors_as_bytes() -> bytes:
        colors = [icon.colors.surface_color for icon in sorted(DoorMapIcon)]
        return struct.pack(">" + "L"*len(colors), *colors)
    
    @staticmethod
    def get_door_index_bounds() -> tuple[int, int]:
        return min(*DoorMapIcon), max(*DoorMapIcon)
