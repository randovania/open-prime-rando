import uuid
from typing import Annotated

from annotated_types import Interval
from open_prime_rando_practice_mod import PracticeModMode
from pydantic import BaseModel, Field, StringConstraints

from open_prime_rando.dol_patching.echoes.beam_cost import BeamConfiguration
from open_prime_rando.dol_patching.echoes.game_options import GameOptionsDefaults
from open_prime_rando.echoes.asset_ids.temple_grounds import LANDING_SITE_MREA
from open_prime_rando.echoes.asset_ids.world import TEMPLE_GROUNDS_MLVL
from open_prime_rando.echoes.damage_changes import DamageChanges
from open_prime_rando.echoes.dock_lock_rando import DockTypeChange
from open_prime_rando.echoes.pickups.schema import PickupModification
from open_prime_rando.echoes.starting_items import StartingItemConfig
from open_prime_rando.echoes.suit_cosmetics import SuitMapping
from open_prime_rando.echoes.translator_gates import TranslatorGateModification

AssetId = Annotated[int, Interval(ge=0, le=0xFFFFFFFF)]


class AreaReference(BaseModel):
    mlvl_id: AssetId
    mrea_id: AssetId


class AreaChange(BaseModel):
    """Contains changes for a given MREA."""

    mrea_id: AssetId
    """The asset id of the MREA for this change."""

    pickups: list[PickupModification] = Field(default_factory=list)
    """Either a modification for an existing pickup in this area, or a new pickup to add."""

    translator_gates: list[TranslatorGateModification] = Field(default_factory=list)
    """A modification for an existing translator gate in this area."""

    door_locks: list[DockTypeChange] = Field(default_factory=list)
    """A modification for a door lock in this area."""


class WorldChange(BaseModel):
    """Contains changes for a given MLVL."""

    mlvl_id: AssetId
    """The asset id of the MLVL for this change."""

    area_changes: list[AreaChange]
    """The changes to apply to a MREA that belongs to this MLVL."""


class MapVisibility(BaseModel):
    """Configures how the map will be tweaked."""

    reveal_map_at_start: bool = False
    """Whether or not the map will be revealed at the start of the game."""

    areas_to_never_reveal: list[AssetId] = Field(default_factory=list)
    """Which areas are not revealed, even when `reveal_map_at_start` is True."""

    unvisited_room_names: bool = True
    """When true, unvisited rooms in the map show their name."""


class StringChange(BaseModel):
    """Contains a new list of strings to use for a given STRG."""

    strg_id: AssetId
    strings: list[str]


class RandoConfiguration(BaseModel):
    """
    Configuration for randomizing Metroid Prime 2: Echoes.
    """

    game_title: Annotated[str, StringConstraints(max_length=64)]
    """The new title of the game, listed in the ISO/Banner."""

    title_screen_text: str
    """Text to be displayed in the title screen."""

    seed: int
    """Seed number of a random number generator. Used for small changes."""

    world_uuid: uuid.UUID = uuid.UUID("00000000-0000-1111-0000-000000000000")
    """An UUID to uniquely identify this export. Can be fetched from the in-game memory."""

    starting_area: AreaReference = AreaReference(mlvl_id=TEMPLE_GROUNDS_MLVL, mrea_id=LANDING_SITE_MREA)
    """The game will start at the given area. When not set, starts at Landing Site."""

    starting_items: list[StartingItemConfig]
    """What is the starting inventory. Any item not listed will be set to 0."""

    map_visibility: MapVisibility = Field(default_factory=MapVisibility)
    """Settings for configuring the Map visibility."""

    beam_configuration: BeamConfiguration = Field(default_factory=BeamConfiguration)
    """Changing how much ammo each beam take for each kind of shot, as well which ammo."""

    game_options_defaults: GameOptionsDefaults = Field(default_factory=GameOptionsDefaults)
    """Overrides for the in-game options defaults."""

    practice_mod: PracticeModMode = PracticeModMode.disabled
    """How accessible is the Practice Mod."""

    auto_enabled_elevators: bool = False
    """Makes the elevators to different areas to be pre-scanned."""

    inverted_mode: bool = False
    """Whether or not to use inverted mode, where Light and Dark Aether is inverted."""

    world_changes: list[WorldChange]
    """A list of World (and Area) specific changes."""

    suit_replacement: SuitMapping = Field(default_factory=SuitMapping)
    """Changes each of the three suit textures to one prepared custom texture set."""

    string_changes: list[StringChange] = Field(default_factory=list)
    """A list of changes to make to existing STRG files."""

    damage_changes: DamageChanges = Field(default_factory=DamageChanges)
    """Set of changes related to damage and health."""
