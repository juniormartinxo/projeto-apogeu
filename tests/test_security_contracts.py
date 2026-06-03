import unittest
from pathlib import Path


class SecurityContractsTest(unittest.TestCase):
    def test_battle_history_escapes_html_before_rendering(self):
        content = Path("app.py").read_text(encoding="utf-8")

        self.assertIn("import html", content)
        self.assertIn("safe_item = html.escape(str(item))", content)
        self.assertIn('<div class=\'history-line\'>{safe_item}</div>', content)
        self.assertNotIn('<div class=\'history-line\'>{item}</div>', content)
        self.assertNotIn('<div class="history-line">{item}</div>', content)


if __name__ == "__main__":
    unittest.main()
