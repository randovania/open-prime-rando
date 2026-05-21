from __future__ import annotations

import dataclasses
import typing

from retro_data_structures.enums.echoes import InventorySlotEnum, Message, PlayerItemEnum, State
from retro_data_structures.formats import Strg

from open_prime_rando.echoes.logbook.new_entry import (
    NewCategoryEntry,
    NewHierarchyEntry,
    NewInventoryEntry,
    NewScanEntry,
)

if typing.TYPE_CHECKING:
    from retro_data_structures.formats.hier import HierEntry
    from retro_data_structures.formats.script_object import ScriptInstance
    from retro_data_structures.formats.tree import Tree

    from open_prime_rando.dol_patching.echoes.dol_patches import EchoesDolVersion
    from open_prime_rando.echoes.rando_configuration import RandoConfiguration
    from open_prime_rando.patcher_editor import PatcherEditor


@dataclasses.dataclass(frozen=True)
class HierarchyPatch:
    node: int | NewHierarchyEntry
    rename: str | None
    connections: tuple[int | HierarchyPatch, ...] = ()

    node_id: int | None = dataclasses.field(init=False, repr=False, hash=False, compare=False, default=None)

    def apply(
        self, editor: PatcherEditor, tree: Tree, hierarchy_entries: list[HierEntry], dol_version: EchoesDolVersion
    ) -> ScriptInstance:
        """
        Apply this patch to the matching entry.
        Renames if needed, changes parent of the connections and recurses as needed.
        """
        if isinstance(self.node, int):
            node = tree.get_node_by_id(self.node)
        else:
            node = self.node.apply(editor, tree, hierarchy_entries, dol_version)

        node.connections = []

        if self.rename is not None:
            entry = hierarchy_entries[node.id]
            editor.get_file(entry.string_table_id, Strg).set_single_string_by_name(entry.name, self.rename)

        for new_conn in self.connections:
            if isinstance(new_conn, HierarchyPatch):
                the_id = new_conn.apply(editor, tree, hierarchy_entries, dol_version).id
            else:
                the_id = new_conn

            node.add_connection(State.Connect, Message.Attach, the_id)
            hierarchy_entries[the_id] = dataclasses.replace(hierarchy_entries[the_id], parent_id=node.id)

        return node


def get_hierarchy_patches(configuration: RandoConfiguration) -> list[HierarchyPatch]:
    """"""

    massive_damage_config = configuration.custom_items.massive_damage_config
    massive_damage_scan_text = (
        f"The Massive Damage increases your damage by {massive_damage_config.damage_multiplier * 100:.0f}% "
        f"for every copy you find, up to {massive_damage_config.max_count}"
    )
    if massive_damage_config.max_count == 1:
        massive_damage_scan_text += " time."
    else:
        massive_damage_scan_text += " times."

    return [
        # # For reference
        # HierarchyPatch(
        #     188,  # Inventory
        #     None,
        #     (
        #         135, # Armor
        #         168, # Morph Ball Systems
        #         320, # Visors
        #         335, # Movement Systems
        #         361, # Weapon Systems
        #         360, # Miscellaneous
        #     ),
        # ),
        HierarchyPatch(
            25,  # Inventory -> Miscellaneous -> Dark Temple Keys -> Sky Temple Keys
            None,
            (
                HierarchyPatch(81, "Keys 1, 2, 3", (148, 151, 156)),
                HierarchyPatch(166, "Keys 4, 5, 6", (45, 303, 317)),
                HierarchyPatch(195, "Keys 7, 8, 9", (159, 221, 231)),
            ),
        ),
        HierarchyPatch(
            320,  # Inventory -> Visors
            None,
            (
                26,  # Dark Visor
                139,  # Echo Visor
                172,  # Scan Visor
                237,  # Combat Visor
                HierarchyPatch(
                    NewCategoryEntry("Translators"),
                    "Translators",
                    (
                        HierarchyPatch(
                            NewInventoryEntry(
                                name_string_name="VioletTranslator",
                                model_name="VioletTranslator",
                                scan_text="The &push;&main-color=#784784;Violet Translator&pop; allows you to access"
                                " devices and doors coded with &push;&main-color=#784784;Violet&pop; holograms.",
                                slot_index=InventorySlotEnum.DarkBomb,
                                item_index=PlayerItemEnum.VioletTranslator,
                            ),
                            "Violet Translator",
                        ),
                        HierarchyPatch(
                            NewInventoryEntry(
                                name_string_name="AmberTranslator",
                                model_name="AmberTranslator",
                                scan_text="The &push;&main-color=#A45600;Amber Translator&pop; allows you to access"
                                " devices and doors coded with &push;&main-color=#A45600;Amber&pop; holograms.",
                                slot_index=InventorySlotEnum.LightBomb,
                                item_index=PlayerItemEnum.AmberTranslator,
                            ),
                            "Amber Translator",
                        ),
                        HierarchyPatch(
                            NewInventoryEntry(
                                name_string_name="EmeraldTranslator",
                                model_name="EmeraldTranslator",
                                scan_text="The &push;&main-color=#4E9761;Emerald Translator&pop; allows you to access"
                                " devices and doors coded with &push;&main-color=#4E9761;Emerald&pop; holograms.",
                                slot_index=InventorySlotEnum.AnnihilatorBomb,
                                item_index=PlayerItemEnum.EmeraldTranslator,
                            ),
                            "Emerald Translator",
                        ),
                        HierarchyPatch(
                            NewInventoryEntry(
                                name_string_name="CobaltTranslator",
                                model_name="CobaltTranslator",
                                scan_text="The &push;&main-color=#56789D;Cobalt Translator&pop; allows you to access"
                                " devices and doors coded with &push;&main-color=#56789D;Cobalt&pop; holograms.",
                                slot_index=InventorySlotEnum.BeamCombo,
                                item_index=PlayerItemEnum.CobaltTranslator,
                            ),
                            "Cobalt Translator",
                        ),
                    ),
                ),
            ),
        ),
        HierarchyPatch(
            361,  # Inventory -> Weapon Systems
            None,
            (
                10,  # Charge Combos
                225,  # Beam Weapons
                337,  # Missile Systems
                HierarchyPatch(
                    NewInventoryEntry(
                        name_string_name="MassiveDamage",
                        model_name="MassiveDamage",
                        scan_text=massive_damage_scan_text,
                        slot_index=InventorySlotEnum(53),
                        item_index=PlayerItemEnum.AmpDamage,
                    ),
                    "Massive Damage",
                ),
            ),
        ),
        HierarchyPatch(
            318,  # Logbook -> Lore
            None,
            (
                HierarchyPatch(
                    119,
                    "Hints",
                    (
                        HierarchyPatch(
                            60,
                            "Lore Hints",
                            (
                                HierarchyPatch(
                                    38,
                                    "Violet",
                                    (
                                        HierarchyPatch(4, "Agon Gate"),
                                        HierarchyPatch(33, "Meeting Grounds"),
                                        HierarchyPatch(120, "Path of Eyes"),
                                        HierarchyPatch(251, "&line-spacing=75;Fortress\nTransport\nAccess"),
                                        HierarchyPatch(364, "&line-spacing=75;Main Energy\nController"),
                                    ),
                                ),
                                HierarchyPatch(
                                    74,
                                    "Amber",
                                    (
                                        HierarchyPatch(59, "&line-spacing=75;Agon Energy\nController"),
                                        HierarchyPatch(75, "Mining Station A"),
                                        HierarchyPatch(82, "Mining Station B"),
                                        HierarchyPatch(102, "Portal Terminal"),
                                        HierarchyPatch(260, "Mining Plaza"),
                                    ),
                                ),
                                HierarchyPatch(
                                    154,
                                    "Emerald",
                                    (
                                        HierarchyPatch(169, "Underground Tunnel"),
                                        HierarchyPatch(200, "Training Chamber"),
                                        HierarchyPatch(228, "&line-spacing=75;Torvus Energy\nController"),
                                        HierarchyPatch(243, "Catacombs"),
                                        HierarchyPatch(312, "Path of Roots"),
                                        HierarchyPatch(342, "Gathering Hall"),
                                    ),
                                ),
                                HierarchyPatch(
                                    196,
                                    "Cobalt",
                                    (
                                        HierarchyPatch(17, "&line-spacing=75;Sanctuary\nEnergy\nController"),
                                        HierarchyPatch(19, "Main Gyro Chamber"),
                                        HierarchyPatch(23, "Sanctuary Entrance"),
                                        HierarchyPatch(162, "&line-spacing=75;Hall of Combat\nMastery"),
                                        HierarchyPatch(183, "Watch Station"),
                                        HierarchyPatch(379, "Main Research"),
                                    ),
                                ),
                            ),
                        ),
                        HierarchyPatch(
                            254,
                            "&line-spacing=75;Sky Temple\nKey Hints",
                            (
                                HierarchyPatch(
                                    129,
                                    "Keys 1, 2, 3",
                                    (
                                        HierarchyPatch(367, "Sky Temple Key 1"),
                                        HierarchyPatch(29, "Sky Temple Key 2"),
                                        HierarchyPatch(118, "Sky Temple Key 3"),
                                    ),
                                ),
                                HierarchyPatch(
                                    233,
                                    "Keys 4, 5, 6",
                                    (
                                        HierarchyPatch(58, "Sky Temple Key 4"),
                                        HierarchyPatch(191, "Sky Temple Key 5"),
                                        HierarchyPatch(373, "Sky Temple Key 6"),
                                    ),
                                ),
                                HierarchyPatch(
                                    319,
                                    "Keys 7, 8, 9",
                                    (
                                        HierarchyPatch(329, "Sky Temple Key 7"),
                                        HierarchyPatch(289, "Sky Temple Key 8"),
                                        HierarchyPatch(52, "Sky Temple Key 9"),
                                    ),
                                ),
                            ),
                        ),
                        HierarchyPatch(
                            NewCategoryEntry("DarkTempleKeyHints"),
                            "&line-spacing=75;Dark Temple\nKey Hints",
                            (
                                HierarchyPatch(
                                    NewScanEntry("DarkAgonKeyHints", 0xA9B11356),
                                    "Dark Agon Temple",
                                ),
                                HierarchyPatch(
                                    NewScanEntry("DarkTorvusKeyHints", 0x8C669B58),
                                    "Dark Torvus Temple",
                                ),
                                HierarchyPatch(
                                    NewScanEntry("IngHiveKeyHints", 0x813068D5),
                                    "Hive Temple",
                                ),
                            ),
                        ),
                        HierarchyPatch(
                            326,
                            "&line-spacing=75;Flying Ing\nCache Hints",
                            (
                                HierarchyPatch(
                                    124,
                                    "Temple Grounds",
                                    (
                                        HierarchyPatch(35, "Landing Site"),
                                        HierarchyPatch(152, "Storage Cavern A"),
                                        HierarchyPatch(355, "Industrial Site"),
                                    ),
                                ),
                                HierarchyPatch(
                                    194,
                                    "Agon Wastes",
                                    (
                                        HierarchyPatch(1, "&line-spacing=75;Central\nMining\nStation"),
                                        HierarchyPatch(6, "Main Reactor"),
                                    ),
                                ),
                                HierarchyPatch(
                                    241,
                                    "Torvus Bog",
                                    (
                                        HierarchyPatch(223, "Catacombs"),
                                        HierarchyPatch(284, "Torvus Lagoon"),
                                    ),
                                ),
                                HierarchyPatch(
                                    327,
                                    "Sanctuary Fortress",
                                    (
                                        HierarchyPatch(46, "Sanctuary Entrance"),
                                        HierarchyPatch(275, "Dynamo Works"),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
                216,  # Pirate Logs
                HierarchyPatch(277, "Champions of Aether"),
                343,  # Trooper Logs
            ),
        ),
    ]
