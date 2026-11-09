# Readonly draw data compiler and selector

This isolated component compiles fixed official 640 public tables. It does not
modify the build, original engine, player BSON, pending slots or source archive.
It does not grant rewards or implement server sequence/pity policy.

Maintainer reproduction (requires pinned extracted marshal files and existing
xdis toolchain, never executes decoded code):

```sh
.venv/bin/python -m tools.project7_draw_ir.produce \
  --source-dir analysis/android640-scripts/com/data/cdata \
  --output /absolute/new-directory
.venv/bin/python -m tools.project7_draw_ir.audit_classes \
  --source-dir analysis/android640-scripts/com/data/cdata \
  --output /absolute/new-rank-audit.json
.venv/bin/python -m unittest tests.test_project7_draw_ir tests.test_project7_draw_ir_closure
```

Consumer (Python standard library only, no analysis inputs or network):

```python
from tools.project7_draw_ir.consumer import load
from tools.project7_draw_ir.closure import select_bundle
from tools.project7_draw_ir import untyped
ir = load()  # fixed contract, exact artifact SHA/size
selected = select_bundle(ir, ordinal=13,
                         outer_ticket=(0, 1000000), inner_ticket=(0, 1000000))
whole_common_bundle = untyped(selected['bundle'])
```

Caller supplies an explicit ordinal and two exact rational points in [0,1).
This API does not choose when to advance/reset ordinal or count six future
reveals. It returns the entire common reward record, including unknown fields;
there is no grant API and unsupported grant semantics must not be treated as
success. Metadata such as tradeType and itemsNum stays attached to its bundle.
Do not reroll existing or pending stock slots using this selector.

`closure-v2/public-source-tables.json` is a lossless typed projection of all four
source tables. `$dict` preserves typed keys, `$tuple` and `$list` distinguish
sequences, `$float` stores exact hexadecimal float values. Canonical UTF-8 JSON
pins are specific to this encoding; different projection encodings have different
hashes. Three independent AST literal projections match normal/default/common
exactly in these canonical bytes. Random comes from the pinned static decoder.

`closure-v2/t1-reward-ir.json` has all positive base t1 branches, reachable
reward_random rows, common reward bundles and explicit default overrides. Missing
or zero weights are excluded; negative/nonfinite weights, missing references,
duplicate IDs, ambiguous multi-ID outer references and nested award_pool fail.
This does not assert multi-ID semantics for other pools. The full four-table
projection preserves those opaque original rows for later work.

`closure-v2/rank-audit.json` binds hero/item_data sources and checks initial rank and
memoryFrag IDs without inferring class from names. Base mass is conditional on
using the normal weighted rows. It is not effective odds after ordinal overrides,
pity, exclusion, wish or any other stateful policy. Eight default pool overrides
are data, while ordinal lifecycle remains unproven. This is host/static evidence,
not Android/native/gameplay verification.

Correction: the earlier closure-v1 and android-catalog-v1 are withdrawn under `withdrawn-v1/`.
`chouka_default.pool` points to a chouka_normal row, whose random_reward points
to the RR table. These two IDs are stored independently. Correct t1 closure is
15 RR pools / 888 unique common records; its 13 positive base rows cover 868.
Eight ordinal overrides reference seven unique normal rows. Explicit source-table
oracles in tests prevent confusing row 360 with RR360 (actual RR is 5069).

The canonical implementation-audit.json and data/audit-v2.json describe current
v2. `python -m tools.project7_draw_ir --output <newfile>` exports the current
verified ordinary-t1 outer graph without analysis inputs. Other historical
default resolver semantics are not claimed. All withdrawn v1 evidence resides
under withdrawn-v1/; no default consumer references that archive.
