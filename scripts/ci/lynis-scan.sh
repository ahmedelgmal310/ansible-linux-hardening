#!/usr/bin/env bash
# Run a Lynis system audit inside the Molecule container and save the report.
#
#   lynis-scan.sh <container> <label> <lynis-dir> <out-dir>
#
# Lynis is copied in from a verified git checkout on the runner, so nothing is
# installed through the package manager and the scan does not change the
# system under test.
set -euo pipefail

container="$1"
label="$2"
lynis_dir="$3"
out_dir="$4"

mkdir -p "$out_dir"

docker exec "$container" rm -rf /opt/lynis-ci
docker cp "$lynis_dir" "$container:/opt/lynis-ci"
docker exec "$container" chown -R root:root /opt/lynis-ci

# Lynis exits non-zero when it finds warnings; the report is what matters.
docker exec -w /opt/lynis-ci "$container" \
  ./lynis audit system --quick --no-colors \
  --report-file "/root/lynis-${label}.dat" \
  --log-file "/root/lynis-${label}.log" >"$out_dir/lynis-${label}.txt" 2>&1 || true

docker cp "$container:/root/lynis-${label}.dat" "$out_dir/lynis-${label}.dat"
docker exec "$container" rm -rf /opt/lynis-ci

index="$(grep -m1 '^hardening_index=' "$out_dir/lynis-${label}.dat" | cut -d= -f2)"
if [[ -z "$index" ]]; then
  echo "Lynis did not produce a hardening index" >&2
  tail -n 50 "$out_dir/lynis-${label}.txt" >&2
  exit 1
fi
echo "Lynis hardening index (${label}): ${index}"
