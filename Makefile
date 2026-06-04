.PHONY: share share-linux serve serve-linux stop-funnel test

LINUX_PYTHON = .venv/bin/python
LINUX_STAMP = .venv/.linux-requirements-installed
WINDOWS_PYTHON = .venv/Scripts/python.exe
WINDOWS_STAMP = .venv/.windows-requirements-installed
SYSTEM_PYTHON ?= python3

$(LINUX_STAMP): requirements.txt
	test -x $(LINUX_PYTHON) || $(SYSTEM_PYTHON) -m venv .venv
	$(LINUX_PYTHON) -m pip install -r requirements.txt
	touch $(LINUX_STAMP)

$(WINDOWS_STAMP): requirements.txt
	python -m venv .venv
	$(WINDOWS_PYTHON) -m pip install -r requirements.txt
	$(WINDOWS_PYTHON) -c "from pathlib import Path; Path(r'$(WINDOWS_STAMP)').touch()"

share: $(WINDOWS_STAMP)
	pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/share.ps1

share-linux: $(LINUX_STAMP)
	bash scripts/share.sh

serve: $(WINDOWS_STAMP)
	$(WINDOWS_PYTHON) -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.enableCORS true --server.enableXsrfProtection true --server.headless true --browser.gatherUsageStats false

serve-linux: $(LINUX_STAMP)
	$(LINUX_PYTHON) -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.enableCORS true --server.enableXsrfProtection true --server.headless true --browser.gatherUsageStats false

stop-funnel:
	tailscale funnel --https=443 off

test: $(WINDOWS_STAMP)
	$(WINDOWS_PYTHON) -m unittest discover -s tests
