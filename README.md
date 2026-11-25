# logifos-testsuite

Shared conformance fixtures for the [logifos](https://github.com/logifos)
math renderer: YAML case definitions carrying each row's **input and
desired outcomes inline** — per grading font, the deterministic SVG and
the laid-out measurements — and the verification flow that keeps them
honest.

## Layout

```
stages/mathml/generations/<n>/payloads/<corpus>__<group>.yaml   case definitions
stages/mathml/generations/<n>/provenance.yaml                   engine, fonts, digests
scripts/generate-stage.py                                       regenerates the stage
scripts/verify.sh                                               re-emits and compares
```

## The corpora

The graded inputs live in third-party repositories, pinned in logifos-rs's
`corpus/reference/sources.json` and fetched on demand — this repository
never redistributes their bytes. The corpora: the plurimath-testsuite
mathml stage (the primary parse/transform rows), lasem fixtures (the
incumbent's corpus), KaTeX's screenshotter data, MathJax-test, JEuclid and
WebKit MathML.

## Case definitions

Each payload follows the plurimath-testsuite pattern: cases carry the row's
input plus its desired outcomes inline. The SVG is one outcome, not the
only one — every case records, per grading font, the deterministic SVG and
the laid-out metrics (width, height, depth in CSS pixels):

```yaml
schema: logifos-testsuite/render/2
cases:
  - id: data/mathml/bugs/666974-mfenced-mo.mml
    input: |
      <math xmlns="...">...</math>
    outcomes:
      - font: cambria-math
        metrics: [50.77, 43.57, 33.28]
        svg: |
          <svg ...>...</svg>
      - font: stix-two-math
        ...
```

A case lists an outcome for every grading font that renders it: fonts
cover different glyph sets, and the coverage gap is itself recorded. The
grading fonts (Cambria Math, STIX Two Math) are pinned by sha256 and face
index in each generation's `provenance.yaml`.

Regenerating, from a logifos-rs checkout with the corpora and grading
fonts fetched:

```
(cd ../logifos-rs && cargo run -p logifos-corpus -- --desired /tmp/desired) \
  > /tmp/desired-manifest.json
python3 scripts/generate-stage.py --rs-dir ../logifos-rs \
  --emitted /tmp/desired --manifest /tmp/desired-manifest.json
```

## Verification

`scripts/verify.sh` exits 0 when the freshly emitted tree matches the
pinned YAML outcomes byte for byte — SVG and metrics per font — and every
emitted render is represented in the stage definitions. A diff means the
engine's rendering changed: update the stage deliberately, with the engine
change that justifies the diff, in a reviewed pull request.

```
LOGIFOS_RS_DIR=../logifos-rs ./scripts/verify.sh
```

## Provenance

Each generation's `provenance.yaml` records the engine version, every
corpus revision, the grading fonts' pinned hashes and a sha256 per payload
file. Rows stop being covered when the engine's capabilities change; the
scoreboard in logifos-rs's committed `corpus/reference/report.json` is the
companion capability report.
