from pathlib import Path
import tomllib

import pytest

from stock_copilot.theme import DARK, LIGHT, theme_styles


def luminance(color):
    rgb = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [value / 12.92 if value <= .04045 else ((value + .055) / 1.055) ** 2.4 for value in rgb]
    return sum(value * weight for value, weight in zip(linear, [.2126, .7152, .0722]))


@pytest.mark.parametrize("palette", [LIGHT, DARK])
def test_theme_text_and_status_colors_have_readable_contrast(palette):
    for foreground, background in [
        ("text", "surface"), ("muted", "inset"), ("accent", "accent-bg"),
        ("on-accent", "accent"), ("positive-text", "positive-bg"), ("negative-text", "negative-bg"),
        ("attention-text", "attention-bg"),
    ]:
        low, high = sorted([luminance(palette[foreground]), luminance(palette[background])])
        assert (high + .05) / (low + .05) >= 4.5, (foreground, background)


def test_only_system_mode_uses_os_preference():
    assert "prefers-color-scheme:dark" in theme_styles("system")
    assert "prefers-color-scheme" not in theme_styles("light")
    assert "prefers-color-scheme" not in theme_styles("dark")
    with pytest.raises(ValueError):
        theme_styles("unknown")
    with pytest.raises(ValueError):
        theme_styles("system", "unknown")


@pytest.mark.parametrize("mode", ["light", "dark"])
def test_color_convention_swaps_gain_loss_without_changing_other_meanings(mode):
    def tokens(convention):
        return dict(item.split(":", 1) for item in theme_styles(mode, convention).split("}", 1)[0].split(";") if item.startswith("--sc-"))

    normal, inverse = tokens("green_up"), tokens("red_up")
    for suffix in ["text", "bg", "border"]:
        assert normal[f"--sc-positive-{suffix}"] == inverse[f"--sc-negative-{suffix}"]
        assert normal[f"--sc-negative-{suffix}"] == inverse[f"--sc-positive-{suffix}"]
    for name in ["accent", "text", "muted", "attention-bg", "attention-text", "pending-bg"]:
        assert normal[f"--sc-{name}"] == inverse[f"--sc-{name}"]


def test_native_startup_palette_matches_application_palette():
    path = Path(__file__).resolve().parents[1] / ".streamlit" / "config.toml"
    config = tomllib.loads(path.read_text())
    for name, palette in [("light", LIGHT), ("dark", DARK)]:
        assert config["theme"][name]["backgroundColor"] == palette["bg"]
        assert config["theme"][name]["textColor"] == palette["text"]
        assert config["theme"][name]["primaryColor"] == palette["accent"]
