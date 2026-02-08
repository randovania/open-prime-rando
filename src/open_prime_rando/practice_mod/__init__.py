import logging
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

import elftools.elf.elffile
from ppc_asm.assembler import ppc
from ppc_asm.dol_file import DolEditor

from open_prime_rando.dol_patching import ppc_helper

if TYPE_CHECKING:
    from elftools.elf.sections import SymbolTableSection


def patch_dol(dol: DolEditor, mod_path: Path) -> None:
    def get_symbol(name: str) -> int:
        return symbol_section.get_symbol_by_name(name)[0].entry["st_value"]

    # First, add the new sections
    with mod_path.open("rb") as f:
        elf_file = elftools.elf.elffile.ELFFile(f)
        symbol_section: SymbolTableSection | None = elf_file.get_section_by_name(".symtab")
        if not symbol_section:
            raise ValueError("Unable to find symbol table")

        patcher_config = tomllib.loads(elf_file.get_section_by_name(".patcher_config").data().decode())

        link_end = get_symbol("_LINK_END")
        patch_arena_lo_1 = get_symbol("_PATCH_ARENA_LO_1")
        patch_arena_lo_2 = get_symbol("_PATCH_ARENA_LO_2")
        hook_addr = get_symbol(patcher_config["entry_point_symbol"])

        # print(f"linking from 0x{link_start:08x} to 0x{link_end:08x} {link_size} bytes")

        entry_addr = elf_file.header["e_entry"]

        for segment in elf_file.iter_segments("PT_LOAD"):
            data = segment.data()
            if len(data) == 0:
                continue
            addr = segment.header["p_paddr"]

            segment_start = len(dol.dol_file.getbuffer())
            dol._seek_and_write(segment_start, data)
            dol.add_section(addr, segment_start, len(data))
            # print(f"Data: {len(data)} @ 0x{addr:08x}-{(addr + len(data)):08x}")

        # Ok now patch the areanalo calls
        ppc_helper.load_32bit_int(
            dol,
            ppc.r3,
            link_end,
            patch_arena_lo_1,
            patch_arena_lo_1 + 4,
        )
        ppc_helper.load_32bit_int(
            dol,
            ppc.r3,
            link_end,
            patch_arena_lo_2,
            patch_arena_lo_2 + 4,
        )
        dol.write_instructions(
            hook_addr,
            [
                ppc.b(entry_addr),
            ],
        )

        for branch_patch in patcher_config.get("branch_patches", []):
            dol.write_instructions(
                get_symbol(branch_patch["branch_from_symbol"]),
                [
                    ppc.b(get_symbol(branch_patch["to_symbol"])),
                ],
            )
    logging.info("Practice mod from %s applied", mod_path)
