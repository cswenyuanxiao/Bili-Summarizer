#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://localhost:7860}"

echo "Preflight check: ${BASE_URL}"

check_url() {
  local url="$1"
  local expect="$2"
  local code=""
  local attempts=20
  local delay=1

  for _ in $(seq 1 "${attempts}"); do
    code="$(curl -s -o /dev/null -w "%{http_code}" "${url}")"
    if [[ "${code}" == "${expect}" ]]; then
      echo "OK   ${url} -> ${code}"
      return 0
    fi
    sleep "${delay}"
  done

  echo "FAIL ${url} -> ${code} (expected ${expect})"
  exit 1
}

# Backend health endpoint
check_url "${BASE_URL}/health" "200"

# Root should serve SPA index in production or API root in dev; accept 200.
check_url "${BASE_URL}/" "200"

echo "Preflight check passed."
