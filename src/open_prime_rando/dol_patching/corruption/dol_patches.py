import dataclasses

from open_prime_rando.dol_patching.all_prime_dol_patches import BasePrimeDolVersion


@dataclasses.dataclass(frozen=True)
class CorruptionDolVersion(BasePrimeDolVersion):
    pass
