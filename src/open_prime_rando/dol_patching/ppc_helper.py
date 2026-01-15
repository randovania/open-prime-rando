import struct

from ppc_asm.assembler import ppc
from ppc_asm.dol_file import DolEditor


def _split_int(value: int) -> tuple[int, int]:
    high = value >> 16
    low = struct.unpack("h", struct.pack("H", value & 0xFFFF))[0]

    if low < 0:
        # When low_value is considered negative, adding it will subtract the overflow bit
        # Add one to high_value to fix it
        high += 1

    return high, low


def load_32bit_int(
    dol: DolEditor, register: ppc.GeneralRegister, value: int, lis_address: int, addi_address: int
) -> None:
    """
    Patches the assembly instructions for loading a 32-bit int into a register, using two instructions.
    :return:
    """

    high_half, low_half = _split_int(value)

    # SetMLvlId argument
    dol.write_instructions(lis_address, [ppc.lis(register, high_half)])
    dol.write_instructions(addi_address, [ppc.addi(register, register, low_half)])
