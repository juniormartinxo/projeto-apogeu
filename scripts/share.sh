#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8501}"
HOST_ADDRESS="${HOST_ADDRESS:-127.0.0.1}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

PYTHON="${PYTHON:-${REPO_ROOT}/.venv/bin/python}"
if [[ ! -x "${PYTHON}" ]]; then
  echo "Virtualenv not found. Run: python -m venv .venv && .venv/bin/python -m pip install -r requirements.txt" >&2
  exit 1
fi

if ! command -v tailscale >/dev/null 2>&1; then
  echo "tailscale CLI not found. Install Tailscale and log in before running make share-linux." >&2
  exit 1
fi

http_ready() {
  "${PYTHON}" - "$1" <<'PY'
import sys
import urllib.request

try:
    with urllib.request.urlopen(sys.argv[1], timeout=2) as response:
        raise SystemExit(0 if response.status == 200 else 1)
except Exception:
    raise SystemExit(1)
PY
}

port_open() {
  "${PYTHON}" - "$1" "$2" <<'PY'
import socket
import sys

host = sys.argv[1]
port = int(sys.argv[2])
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.settimeout(0.5)
    raise SystemExit(0 if sock.connect_ex((host, port)) == 0 else 1)
PY
}

if port_open "127.0.0.1" "${PORT}"; then
  echo "Port ${PORT} is already in use. Stop that process or set PORT to a free port before opening Funnel." >&2
  exit 1
fi

echo "Starting Protocolo Apogeu on http://localhost:${PORT} ..."
nohup "${PYTHON}" -m streamlit run app.py \
  --server.address "${HOST_ADDRESS}" \
  --server.port "${PORT}" \
  --server.enableCORS true \
  --server.enableXsrfProtection true \
  --browser.gatherUsageStats false \
  >/tmp/protocolo-apogeu-streamlit-"${PORT}".log 2>&1 &

ready=0
for _ in $(seq 1 30); do
  if http_ready "http://localhost:${PORT}"; then
    ready=1
    break
  fi
  sleep 1
done

if [[ "${ready}" != "1" ]]; then
  echo "Streamlit did not respond on http://localhost:${PORT}." >&2
  echo "Check log: /tmp/protocolo-apogeu-streamlit-${PORT}.log" >&2
  exit 1
fi

echo "Opening Tailscale Funnel for http://localhost:${PORT} ..."
tailscale funnel --bg "localhost:${PORT}"

echo
echo "Public URL:"
tailscale funnel status
