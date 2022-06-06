import dataclasses

from retro_data_structures.base_resource import AssetId
from retro_data_structures.enums import echoes
from retro_data_structures.properties.echoes.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.echoes.archetypes.WeaponVulnerability import WeaponVulnerability
from retro_data_structures.properties.echoes.core.Color import Color




@dataclasses.dataclass(frozen=True)
class DockType:
    vulnerability: DamageVulnerability
    shell_model: AssetId
    shell_color: Color
