#!/bin/bash
cd "$(dirname "$0")"
echo "=== nsdi-egress run starting at $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
echo "Working dir: $(pwd)"
echo ""
../../venv/bin/python nsdi_egress.py 2>&1 | tee "run-$(date +%Y-%m-%d).log"
echo ""
echo "=== Done at $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
echo "Press any key to close..."
read -n 1
