#!/bin/zsh
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

if [[ ! -x .venv/bin/python ]]; then
  print -u2 "Project environment not found. Create it first with: python3.11 -m venv .venv"
  exit 1
fi

# This workspace can mark downloaded Qt plugins hidden, which makes Qt fail
# to discover the macOS Cocoa platform plugin. Clear that flag before launch.
/usr/bin/chflags -R nohidden "$PROJECT_ROOT/.venv"
export PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
exec "$PROJECT_ROOT/.venv/bin/python" -m dss
