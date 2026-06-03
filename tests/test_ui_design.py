import unittest
from pathlib import Path


class GameFirstDesignTest(unittest.TestCase):
    def test_ui_has_game_shell_and_no_side_stripe_callouts(self):
        ui_source = Path("src/ui_components.py").read_text(encoding="utf-8")
        app_source = Path("app.py").read_text(encoding="utf-8")
        combined = ui_source + app_source

        required_tokens = [
            "command-shell",
            "mission-briefing",
            "pilot-hud",
            "campaign-map",
            "battle-arena",
            "combat-question",
            "enemy-dossier",
            "mentor-comms",
        ]

        for token in required_tokens:
            with self.subTest(token=token):
                self.assertIn(token, combined)

        self.assertIn("oklch(", ui_source)
        self.assertNotIn("border-left: 3px", ui_source)
        self.assertNotIn("border-right: 3px", ui_source)

    def test_molock_uses_project_raster_asset_instead_of_svg_placeholder(self):
        ui_source = Path("src/ui_components.py").read_text(encoding="utf-8")

        self.assertTrue(Path("assets/molock-boss.png").is_file())
        self.assertIn("assets/molock-boss.png", ui_source)
        self.assertIn("st.image", ui_source)
        self.assertNotIn("<svg class=\"ap-svg\"", ui_source)
        self.assertNotIn(">MOLOCK</text>", ui_source)


if __name__ == "__main__":
    unittest.main()
