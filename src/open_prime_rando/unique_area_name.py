from retro_data_structures.formats.mrea import Area

CUSTOM_AREA_NAMES = {
    0xF3EE585F: "Portal Chamber (Light)",
    0xAE1E1339: "Portal Chamber (Dark)",
}


def get_name_for_area(area: Area) -> str:
    return CUSTOM_AREA_NAMES.get(area.mrea_asset_id, area.name)
