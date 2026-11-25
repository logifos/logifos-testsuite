#!/usr/bin/env python3
"""Verifies a fresh logifos-rs emission against the pinned stage YAML.

Every payload's digest must match provenance.yaml (no hand edits), every
case outcome's SVG must match the freshly emitted bytes for its font, and
every emitted render must be represented in the YAML — nothing stale, and
nothing missing.

Usage:
  verify.py --emitted /tmp/emitted --manifest /tmp/manifest.json
"""

import argparse
import hashlib
import json
import pathlib
import sys

import yaml

STAGES = pathlib.Path("stages") / "mathml"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emitted", required=True, type=pathlib.Path)
    parser.add_argument("--manifest", required=True, type=pathlib.Path,
                        help="the fresh emission's manifest.json")
    args = parser.parse_args()

    generation = STAGES / "generations" / "000001"
    provenance = yaml.safe_load((generation / "provenance.yaml").read_text())
    mismatches = []

    for name, expected in sorted(provenance["sha256"].items()):
        path = generation / name
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != expected:
            mismatches.append(f"payload digest drift: {name}")

    manifest = json.loads(args.manifest.read_text())
    emitted_keys = set(manifest["sha256"])
    checked = set()
    rows = 0
    outcomes = 0
    fonts = set()
    for payload_path in sorted((generation / "payloads").glob("*.yaml")):
        document = yaml.safe_load(payload_path.read_text())
        corpus = document["group"].split("/", 1)[0]
        for case in document["cases"]:
            rows += 1
            flattened = f"{case['id'].replace('/', '__')}.svg"
            for outcome in case["outcomes"]:
                outcomes += 1
                fonts.add(outcome["font"])
                key = f"{outcome['font']}/{corpus}/{flattened}"
                emitted = args.emitted / outcome["font"] / corpus / flattened
                if not emitted.is_file():
                    mismatches.append(f"missing emission: {key}")
                    continue
                checked.add(key)
                if emitted.read_text() != outcome["svg"]:
                    mismatches.append(f"svg drift: {key}")
                if manifest["metrics"][key] != outcome["metrics"]:
                    mismatches.append(f"metrics drift: {key}")
    for key in sorted(emitted_keys - checked):
        mismatches.append(f"emission without a stage outcome: {key}")

    if mismatches:
        for mismatch in mismatches[:20]:
            print(mismatch, file=sys.stderr)
        sys.exit(f"{len(mismatches)} verification mismatches")

    engine = provenance["engine"]["version"]
    print(
        f"verified: {rows} rows, {outcomes} per-font outcomes "
        f"({len(fonts)} fonts: {', '.join(sorted(fonts))}), engine {engine}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
