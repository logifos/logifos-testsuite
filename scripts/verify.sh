#!/usr/bin/env bash
# Verifies the desired renders: re-emits every corpus render with the
# local logifos-rs checkout and diffs it byte for byte against the pinned
# tree. Requires the corpora and grading font to be fetched (see
# logifos-rs/corpus/reference) and LOGIFOS_RS_DIR to point at the checkout.
set -euo pipefail
cd "$(dirname "$0")/.."
rs_dir=${LOGIFOS_RS_DIR:?set LOGIFOS_RS_DIR to the logifos-rs checkout}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
(cd "$rs_dir" && cargo run --quiet -p logifos-corpus -- --desired "$tmp/emitted" >/dev/null)
if ! diff -r "$tmp/emitted" desired/ >/dev/null; then
  echo "the emitted renders differ from the pinned desired/ tree" >&2
  diff -rq "$tmp/emitted" desired/ | head -20 >&2
  exit 1
fi
python3 - "$tmp/emitted" <<'EOF'
import hashlib, json, sys, pathlib
root = pathlib.Path(sys.argv[1])
manifest = json.loads(pathlib.Path("manifest.json").read_text())
files = sorted(p for p in root.rglob("*.svg"))
mismatch = 0
for path in files:
    key = f"{path.parent.name}/{path.name}"
    expected = manifest["sha256"].get(key)
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if expected != actual:
        print(f"checksum mismatch: {key}")
        mismatch += 1
missing = set(manifest["sha256"]) - {f"{p.parent.name}/{p.name}" for p in files}
if missing:
    print(f"manifest entries without files: {sorted(missing)[:10]}")
    mismatch += len(missing)
assert not mismatch, f"{mismatch} checksum mismatches"
print(f"checksums verified: {len(files)} renders")
EOF
echo "the desired renders verify byte for byte"
