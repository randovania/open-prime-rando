import pytest
from retro_data_structures.properties.echoes.core import Color
from retro_data_structures.properties.echoes.objects import TweakGuiColors

from open_prime_rando.echoes import hud_color
from open_prime_rando.patcher_editor import PatcherEditor


@pytest.mark.parametrize("change_text_color", [False, True])
@pytest.mark.parametrize("change_beam_visor", [False, True])
def test_edit_hud_color(prime2_editor: PatcherEditor, change_text_color, change_beam_visor) -> None:
    config = hud_color.HudColorConfiguration(
        main_color=(0.0, 1.0, 0.0),
        change_text_color=change_text_color,
        change_beam_visor_select_color=change_beam_visor,
    )
    hud_color.edit_hud_color(prime2_editor, config)

    main_color = Color(0.0, 1.0, 0.0, 1.0)

    with prime2_editor.edit_tweak(TweakGuiColors) as tweak:
        assert tweak.combat_hud_color_scheme.hud_hue == main_color
        assert tweak.ball_hud.energy_bar_filled_color == Color(g=0.8823530077934265, b=0.037206146866083145, a=1.0)
        assert tweak.ball_hud.energy_bar_shadow_color == Color(g=0.6392160058021545, b=0.027878550812602043, a=1.0)
        assert tweak.misc.energy_bar_low_empty_color == Color(g=0.37254899740219116, b=0.01431406568735838, a=1.0)

        assert (tweak.misc.hud_memo_text_foreground_color == main_color) == change_text_color

        expected_beam_visor = Color(g=0.784313976764679, b=0.07148205488920212, a=1.0)
        assert (tweak.misc.selected_visor_beam_color == expected_beam_visor) == change_beam_visor
