import unittest
from pathlib import Path


class MakeShareCommandTest(unittest.TestCase):
    def test_makefile_exposes_share_command(self):
        makefile = Path("Makefile")
        self.assertTrue(makefile.is_file(), "Makefile must exist")
        content = makefile.read_text(encoding="utf-8")

        self.assertIn(".PHONY: share share-linux serve serve-linux stop-funnel", content)
        self.assertIn("LINUX_PYTHON = .venv/bin/python", content)
        self.assertIn("LINUX_STAMP = .venv/.linux-requirements-installed", content)
        self.assertIn("$(LINUX_STAMP): requirements.txt", content)
        self.assertIn("test -x $(LINUX_PYTHON) || $(SYSTEM_PYTHON) -m venv .venv", content)
        self.assertIn("$(LINUX_PYTHON) -m pip install -r requirements.txt", content)
        self.assertIn("touch $(LINUX_STAMP)", content)
        self.assertIn("share:", content)
        self.assertIn("share-linux: $(LINUX_STAMP)", content)
        self.assertIn("scripts/share.ps1", content)
        self.assertIn("share-linux:", content)
        self.assertIn("bash scripts/share.sh", content)
        self.assertIn("serve-linux: $(LINUX_STAMP)", content)
        self.assertIn("$(LINUX_PYTHON) -m streamlit run app.py", content)
        self.assertIn("--server.headless true", content)
        self.assertIn("--browser.gatherUsageStats false", content)
        self.assertIn("stop-funnel:", content)
        self.assertIn("tailscale funnel --https=443 off", content)

    def test_share_script_starts_streamlit_and_tailscale_funnel(self):
        script = Path("scripts/share.ps1")
        self.assertTrue(script.is_file(), "scripts/share.ps1 must exist")
        content = script.read_text(encoding="utf-8")

        required = [
            '"-m"',
            '"streamlit"',
            '"run"',
            '"app.py"',
            "--server.address",
            '"127.0.0.1"',
            "--server.port",
            "8501",
            "--server.enableCORS",
            "--server.enableXsrfProtection",
            "--server.headless",
            '"true"',
            "Port $Port is already in use",
            'tailscale funnel --bg "localhost:$Port"',
        ]
        for text in required:
            with self.subTest(text=text):
                self.assertIn(text, content)
        self.assertNotIn('"--server.enableCORS", "false"', content)
        self.assertNotIn('"--server.enableXsrfProtection", "false"', content)
        self.assertNotIn("tailscale funnel --bg localhost:8501", content)
        self.assertNotIn("Reusing the existing local server", content)

    def test_linux_share_script_starts_streamlit_and_tailscale_funnel(self):
        script = Path("scripts/share.sh")
        self.assertTrue(script.is_file(), "scripts/share.sh must exist")
        content = script.read_text(encoding="utf-8")

        required = [
            "#!/usr/bin/env bash",
            "set -euo pipefail",
            ".venv/bin/python",
            "-m streamlit run app.py",
            "--server.address",
            "127.0.0.1",
            "--server.port",
            "8501",
            "--server.enableCORS true",
            "--server.enableXsrfProtection true",
            "--server.headless true",
            "Port ${PORT} is already in use",
            "tailscale funnel --bg",
            "localhost:${PORT}",
        ]
        for text in required:
            with self.subTest(text=text):
                self.assertIn(text, content)
        self.assertNotIn("--server.enableCORS false", content)
        self.assertNotIn("--server.enableXsrfProtection false", content)
        self.assertNotIn("Reusing the existing local server", content)


if __name__ == "__main__":
    unittest.main()
