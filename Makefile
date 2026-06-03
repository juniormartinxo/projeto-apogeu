.PHONY: share share-linux serve serve-linux stop-funnel test

share:
	pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/share.ps1

share-linux:
	bash scripts/share.sh

serve:
	.venv/Scripts/python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.enableCORS true --server.enableXsrfProtection true

serve-linux:
	.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.enableCORS true --server.enableXsrfProtection true

stop-funnel:
	tailscale funnel --https=443 off

test:
	.venv/Scripts/python.exe -m unittest discover -s tests
