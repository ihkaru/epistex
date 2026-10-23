#!/usr/bin/env bash
# ============================================================
# Epistex Pre-Stop Verification Gate (.agents/hooks/pre_stop.sh)
# Runs the 4-gate gauntlet before an AI coding agent may stop.
# Exit 0 = all gates pass (agent may stop).
# Exit 1 = gate failed (agent is hard-blocked; must remediate).
# ============================================================
set -euo pipefail

PASS="[PASS]"
FAIL="[FAIL]"
ERRORS=0

echo ""
echo "========================================"
echo "  Epistex Agent Verification Gauntlet"
echo "========================================"
echo ""

# ── Gate 1: Unit & Integration Tests ──────────────────────
echo "Gate 1: Running unit & integration tests..."
if python3 -m unittest discover -s tests -q 2>&1 | tail -3; then
  echo "$PASS Gate 1: All tests pass."
else
  echo "$FAIL Gate 1: Tests failed. Fix all failures before stopping."
  ERRORS=$((ERRORS + 1))
fi
echo ""

# ── Gate 2: SRP Static Analyzer (only if script available) ─
SRP_SCRIPT="$HOME/.gemini/config/skills/craftsman-coder/scripts/static_srp_analyzer.py"
echo "Gate 2: Running SRP & abstraction static analysis..."
if [ -f "$SRP_SCRIPT" ]; then
  if python3 "$SRP_SCRIPT" . --strict 2>&1 | tail -5; then
    echo "$PASS Gate 2: No SRP violations detected."
  else
    echo "$FAIL Gate 2: SRP violations found. Decompose violating modules."
    ERRORS=$((ERRORS + 1))
  fi
else
  echo "[SKIP] Gate 2: SRP analyzer not found at $SRP_SCRIPT — skipped."
fi
echo ""

# ── Gate 3: Zero-Mock Detector ────────────────────────────
echo "Gate 3: Running zero-mock static detector..."
if command -v detect-mocks &>/dev/null; then
  if detect-mocks . 2>&1 | tail -5; then
    echo "$PASS Gate 3: No mock leakage in production paths."
  else
    echo "$FAIL Gate 3: Mock code detected in production paths. Remove before stopping."
    ERRORS=$((ERRORS + 1))
  fi
else
  echo "[SKIP] Gate 3: detect-mocks not available — skipped."
fi
echo ""

# ── Gate 4: Repository Health Audit ──────────────────────
echo "Gate 4: Running end-to-end repository health audit..."
if ./bin/gx doctor --json 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
status = data.get('status', 'unknown')
total_issues = data.get('total_issues', len(data.get('issues', [])))
if status in ('ok', 'healthy') and total_issues == 0:
    print('Repository status: healthy (0 issues)')
    sys.exit(0)
else:
    issues = data.get('issues', [])
    print(f'Repository status: {status} ({total_issues} issue(s))')
    for issue in issues:
        print(f'  - {issue}')
    sys.exit(1)
"; then
  echo "$PASS Gate 4: Repository is healthy."
else
  echo "$FAIL Gate 4: Repository health check failed. Inspect gx doctor output."
  ERRORS=$((ERRORS + 1))
fi
echo ""

# ── Summary ───────────────────────────────────────────────
echo "========================================"
if [ "$ERRORS" -eq 0 ]; then
  echo "  ALL GATES PASSED — Agent may stop."
  echo "========================================"
  exit 0
else
  echo "  $ERRORS GATE(S) FAILED — Agent MUST remediate before stopping."
  echo "========================================"
  exit 1
fi
