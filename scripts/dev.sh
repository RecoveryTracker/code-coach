#!/usr/bin/env bash
# Start Code Coach IAE: API + web UI.
# Ports: API_PORT (default 8765) and UI_PORT (default 5173); if the default
# API port is taken, the next free one is picked automatically.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pip install -r requirements.txt
else
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

if [[ ! -d web/node_modules ]]; then
  (cd web && npm install)
fi

port_free() {
  ! lsof -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1
}

API_PORT="${API_PORT:-8765}"
UI_PORT="${UI_PORT:-5173}"

# Pick the next free API port if the default is busy (e.g. another instance).
if ! port_free "$API_PORT"; then
  for p in $(seq "$API_PORT" $((API_PORT + 20))); do
    if port_free "$p"; then API_PORT="$p"; break; fi
  done
fi

cleanup() {
  jobs -p | xargs -r kill 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "API  → http://127.0.0.1:${API_PORT}"
echo "UI   → http://localhost:${UI_PORT} (Vite bumps to the next port if busy)"
echo ""

uvicorn code_coach.api.server:app --reload --host 127.0.0.1 --port "$API_PORT" &
(cd web && VITE_API_PORT="$API_PORT" VITE_UI_PORT="$UI_PORT" npm run dev) &
wait
