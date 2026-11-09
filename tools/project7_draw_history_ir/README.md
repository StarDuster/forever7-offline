# Historical draw readonly IR

This independent package contains fixed official640 public data, not player
state or pool handlers. Nothing is connected to the build/startup/DEX/runtime.
Normal draw policy and 354 production code remain frozen.

Consumer (standard library only, no analysis inputs, network, game modules or
xdis):

```python
from tools.project7_draw_history_ir.consumer import load, lookup
ir = load()                       # fixed contract + compressed/uncompressed SHA/size
pool = lookup(ir, 484)             # explicit wire t; unknown/zero never falls back
assert pool['epoch_utc'] == 2074057200
assert pool['runtime_enabled_by_this_component'] is False
```

```sh
.venv/bin/python -m tools.project7_draw_history_ir --wire 484
.venv/bin/python -m unittest tests.test_project7_draw_history_ir
```

The authoritative bundle is data/history-v1/{contract.json,history-ir.json.gz,
capabilities.json}. Intermediate drafts/v1,v2,v3 are development snapshots and are
not default consumer inputs. The compressed IR contains every literal row of all
13 pinned source tables, plus normalized metadata for all 485 chouka_info rows,
referenced positive RR/common graphs, exact rational bundle-signature masses,
unknown field inventories and independent friend/furniture dependency audits.
The manually appended friend wire99 is separate from those 485 rows.

Key UI metadata comes from the real card_tab contract: table key is the wire t,
all 485 drawType values match it; poolType is a category, not the wire t. Sort
falls back to99 exactly as the source UI does; levels remain original explicit
values. Epoch/begin/end are UTC timegm of the original tuples, without changing
any process clock. Full original fields, restrictions and unknown metadata stay
in typed raw tables. All 41 furniture rows are excluded from the six-card tab
and retain their independent family; the 17 furniture_delivery rows do not prove
rotation open_range or protocol behavior.

Default.pool is a chouka_normal row ID, then random_reward is the RR ID. Missing
normal rows remain unresolved even if an RR happens to have the same number.
Absent/zero weights are excluded from positive distributions; negative or
nonfinite weights fail. Multiple outer RR references are retained and marked
unresolved, never split uniformly. Duplicate inner targets retain separate edge
indices/masses. Common records stay atomic, including unknown fields and extra
components; signature probabilities classify the whole bundle, not mutually
exclusive individual components. Actual fixed source weights are all integers
(including integer-valued floats); Fraction also preserves exact binary values
for any noninteger toy float.

Memory metadata retains source item -> hero/piece plus original hero/file rows.
Design metadata retains the full source row/dumps_info and its tr document,
without manufacturing inventory instances or template UUIDs. Type8/subtype61–67
virtual items carry mechanism tags and require selection policy. Global
hero_self_choose_info is a hero-to-show/fragment mapping; it is not treated as a
per-pool S/A candidate list. All six self_choose pools explicitly retain an
unresolved candidate source. Other unknown reward fields, nested award_pool,
missing references and dynamic hints are reported, never granted.

Capabilities are data classifications. `static_hierarchy_closed` means the
represented base/default dependency graph and supported field shapes close;
it does not prove server guarantees, costs, reset rules, gameplay safety or an
engine seam. Dynamic hints require policy review. Friendship99/131 and furniture
have independent RPC-family requirements, not fake six-slot compatibility.
New 354 groups remain disabled. Every pool has runtime_enabled=false.

Maintainer reproduction (only pinned public marshal literals; no decoded game
code is run):

```sh
.venv/bin/python -m tools.project7_draw_history_ir.produce \
  --source-dir analysis/android640-scripts/com/data/cdata \
  --output /absolute/fresh-output-directory
```

The maintainer reuses the existing strict static literal decoder and xdis; the
consumer imports only this package's standard-library codec/compiler/reader.
Each source marshal SHA/size and host-literal projection SHA is recorded. The
host projection distinguishes tuples/lists, typed dictionary keys and exact
float hex; original Python2 str versus unicode identity is not independently
represented. Consumer decompression is bounded and rejects trailing members,
truncation, wrong hash/size, duplicate JSON keys and unsupported schemas. Output
production refuses existing paths and publishes a complete directory.

execution-capabilities.json additionally separates base-graph closure from
actual grant/runtime readiness and lists virtual subtype10/13 review needs.
Static-selector-ready still means grant/runtime unimplemented by this component.
Friend99 is returned as a manual independent-family record with unresolved
constant/UI metadata, never as a normal pool.
