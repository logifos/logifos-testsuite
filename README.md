# logifos-testsuite

Shared conformance fixtures for the [logifos](https://github.com/logifos)
math renderer: the pinned reference corpora, the **desired renders** (the
deterministic SVG logifos produces for every row it covers), and the
verification flow that keeps both honest.

## Layout

```
desired/mathml/<corpus>/<case>.svg   the desired render, one file per covered row
manifest.json                        engine version, corpus revisions, per-file sha256
scripts/verify.sh                    re-emits the renders and diffs them byte for byte
```

## The corpora

The graded inputs live in third-party repositories, pinned in logifos-rs's
`corpus/reference/sources.json` and fetched on demand — this repository pins
the same revisions in `manifest.json` and never redistributes their bytes.
The corpora: the plurimath-testsuite mathml stage (the primary
parse/transform rows), lasem fixtures (the incumbent's corpus), KaTeX's
screenshotter data, MathJax-test, JEuclid and WebKit MathML.

## Desired renders

`desired/` holds logifos's own deterministic SVG for every case its
pipeline currently covers end to end (parse → transform → write →
round-trip → layout → emit). The renders are byte-stable: the same engine
version, corpus revisions and grading font always produce identical bytes.

Regenerating and verifying, from a logifos-rs checkout with the corpora
and the grading font fetched:

```
cargo run -p logifos-corpus -- --desired /tmp/desired
./scripts/verify.sh /tmp/desired
```

`verify.sh` exits 0 when the freshly emitted tree is byte-identical to the
pinned `desired/` tree and the checksums in `manifest.json` match. A diff
means the engine's rendering changed: update `desired/` deliberately, with
the engine change that justifies the diff, in a reviewed pull request.

## Provenance

`manifest.json` records the engine version, every corpus revision and a
sha256 per desired render. Rows stop being covered when the engine's
capabilities change; the scoreboard in logifos-rs's committed
`corpus/reference/report.json` is the companion capability report.
