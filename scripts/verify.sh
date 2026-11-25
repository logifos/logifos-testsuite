#!/usr/bin/env bash
# Verifies the stage definitions: re-emits every corpus render per grading
# font with the local logifos-rs checkout and compares each case's SVG and
# metrics against the pinned YAML outcomes. Requires the corpora and the
# grading fonts to be fetched (see logifos-rs/corpus) and LOGIFOS_RS_DIR to
# point at the checkout.
set -euo pipefail
cd "$(dirname "$0")/.."
rs_dir=${LOGIFOS_RS_DIR:?set LOGIFOS_RS_DIR to the logifos-rs checkout}
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
(cd "$rs_dir" && cargo run --quiet -p logifos-corpus -- --desired "$tmp/emitted") \
  > "$tmp/manifest.json"
python3 scripts/verify.py --emitted "$tmp/emitted" --manifest "$tmp/manifest.json"
