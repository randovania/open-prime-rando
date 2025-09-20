from retro_data_structures.formats import Strg

from open_prime_rando.patcher_editor import PatcherEditor


def apply_corrupted_memory_card_change(editor: PatcherEditor):
    # STRG_MemoryCard_0
    table = editor.get_file(0x88E242D6, Strg)

    table.set_single_string(
        table.raw.name_table["CorruptedFile"],
        """The save file was created using a different
Randomizer ISO and must be deleted.""",
    )
    table.set_single_string(table.raw.name_table["ChoiceDeleteCorruptedFile"], "Delete Incompatible File")
