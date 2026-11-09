# Ordinary t=1 policy hooks

`com.project7.localmanager.CoreDrawPolicy` keeps original BSON/Store transactions,
fees, reveal grants, UUID generation, callbacks and animations. It owns only an
immutable public catalog. `prepare(Context)` verifies the complete fixed asset
before publishing it and retains no Context/profile. Consumer preparation uses
Android32 and `compile_stubs` only; the translated manager JAR is host evidence,
not an end-user build dependency. Compile stubs are never runtime classes.

Asset source: `tools/project7_draw_ir/data/android-catalog-v2.tsv`, staged by the
parent preparer as `project7_draw_policy/catalog-v2.tsv`. SHA256:
`e250ace8d74eaf87769a709532e5a4e1ae69eb2d1acfedf520b79e0323136319`.
The adjacent fixed contract binds the corrected t1 IR and item/design tables.
Earlier v1 catalog/IR are withdrawn because default.pool denotes a normal-table
row, not an RR ID. Current closure is 15 RR / 888 common (steady base 868).

Four static interfaces, all returning byte[]:

- `makeFile(LocalResourceCatalog, Random, boolean, byte[] state)`
- `tutorialCandidate(int, byte[] candidate)`
- `stateForSave(byte[] state, int t)`
- `reveal(LocalResourceEngine.Result, LocalResourceCatalog, byte[] card)`

Only the new tutorial synthetic bridge is needed. `reveal` invokes the unchanged
package-visible original reveal once. New cards carry version/hash/policy,
normal source row ID, RR ID, common ID, ordinal and reservation end. Integer
sampling retains both weighted layers. Missing/unsupported catalog/leaf fails;
there is no uniform fallback. Checked validation/interruption failures become
IllegalArgumentException for the original engine catch. Original IAE/arithmetic
exceptions retain their type. Errors are not caught. `prepare` remains checked.

The explicitly offline `normal-ordinal-reserve-on-group-v1` starts at max(stored
cursor, ct+1), reserves six on successful original save, never advances ct on
creation and never refunds abandoned slots. Save merges max(cursor,end) rather
than adding six again. Overflow/inconsistent groups fail. Old unmarked groups
stay unmarked; opened replay never resolves/grants again. Stored cards do not
need the current catalog to rediscover their outcome.

Hero and fragment handling, duplicate conversion and treasure/design grant stay
inside original reveal. Design is an actual BSON tr document, without template
UUID. Only the missing summonCoin primary-card projection is added: after one
original grant, its local +count delta is checked and top-level item=[[90,count]]
is attached. Primary rewards are never copied to activityReward or other_reward.item;
these remain reserved for original true extras. This avoids generic settlement
repeating the stock main-card animation. No RPC or UI calls occur in the helper.

Host verification:

```sh
.venv/bin/python runtime/android_draw_policy/verify_host.py
.venv/bin/python runtime/android_draw_policy/verify_patched_host.py
.venv/bin/python runtime/android_draw_policy/verify_abi.py
.venv/bin/python runtime/android_draw_policy/host_tests/verify_p7_consumer_bodies.py
```

Host execution uses original verified translated methods, synthetic BSON and
explicit inert platform/UI/transport probes. The patched proof uses the actual
four-seam manager JAR, excludes every compile stub at runtime, exercises original
Store/writeAtomic/typed replies, and runs original selected CLIENT_STUB decorator,
argument conversion/defaults and sender callbacks. It is not ART, native rendering,
scene initialization, networking, or full game acceptance. No original templates,
actual user BSON, credentials or signing materials are read.

On minimally shaped synthetic profiles, the stock Store can normalize daily and
achievement fields even after a rejected draw. That existing normalization is
not rewritten. The failure-byte-preservation test starts from stock-normalized
profiles and separately verifies no debit/grant/card/cursor business change.
