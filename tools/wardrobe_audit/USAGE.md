# Original-UI read-only wardrobe audit

This tool is **not yet native-accepted**. Only the sole native actor may execute
it, after other device work finishes. It never grants heroes/skins, equips, dyes,
changes awakening/pendants, patches runtime methods, suppresses RPC/save, or
restores a save. Do not combine it with another model probe or user input.

`native_probe.py` is standalone ASCII Python 2.7 source delivered through the
existing opt-in development probe. No production runtime/allowlist change is
required. The host CLI requires the existing project `.venv` and ADB only when
`--execute` is explicit. Physical-device serials are refused.

## Inspect plans without any device access

From the repository root:

```sh
.venv/bin/python tools/audit_wardrobe_readonly.py --heroes 99 --skins 10080 --limit 2 --out-dir reports/actor-wardrobe-99
.venv/bin/python tools/audit_wardrobe_readonly.py --out-dir reports/actor-wardrobe-full
```

Default invocation only parses the original hero/skin tables and writes a plan.
It does not invoke subprocess/ADB. The full plan has **634 jobs: 140 current-hero
baselines plus 494 distinct skin appearances, including 99 dye rows**. 395 model
IDs are not substituted for appearance coverage. Hero46/125 and their skin rows
are separate original-no-model exclusions, never passing renders. A skin filter
still retains its selected hero's current-appearance baseline.

Existing plans/checkpoints are never overwritten. Use a new output directory or
`--resume`. The checked-in delivery dry-run examples are
`reports/wardrobe-readonly-{full,hero99}-dry-run/plan.json`; they contain no native
captures or passing rows.

## Sole native actor: first two-job exercise

1. Finish the active device task. Confirm the actual APK/script/GPU environment;
   keep its renderer/backend evidence. If an effective loose script override
   exists, identify that exact device path. Otherwise the tool hashes the
   installed APK's actual `assets/script.npk` stream, without extracting/repacking
   the APK. APK hash, script hash, hardware, resolution and SurfaceFlinger renderer
   lines are captured again on every resume. The actor-supplied GPU information
   remains explicitly identified as such; missing renderer readback is recorded.
2. Through the **original UI**, open the visible hero list, choose its ordinary
   All/no-search filter, and stop interacting. Do not change owned skins, dye,
   awakening, permanent wear, or inventory to manufacture eligibility. The app
   must already have its opt-in `offline_development.flag` and original local
   development transport. This tool does not create that flag or install an app.
3. Write a local GPU provenance JSON with actual values, for example:

```json
{"renderer":"<actual renderer>","backend":"<actual backend>","device":"<actual device/GPU>"}
```

4. Only the actor now runs the previously reviewed two-job plan:

```sh
.venv/bin/python tools/audit_wardrobe_readonly.py --resume --execute --serial emulator-5554 --gpu-provenance /absolute/path/gpu.json --out-dir reports/actor-wardrobe-99
```

For an actual effective loose script resource, additionally pass
`--device-script /absolute/device/path/to/script.npk`. Do not pass an unrelated
local build hash or the APK as a substitute script identity. The actor must
resolve an unavailable `unzip -p` or script provenance before continuing; errors
pause rather than invent identity. A custom ADB executable can be supplied with
`--adb /absolute/path/adb`.

5. Inspect both full-resolution PNGs, metadata before/after the screenshot,
   `checkpoint.jsonl`, RPC log slices, `inventory{,-final}.json` and the summary.
   Loaded rows are **loaded_unreviewed**, not material passes. Check missing
   textures/black surfaces, mesh/clipping, face/hair, dye colors, and actual
   awakening/pendant/artifact context. The tool deliberately accepts original
   owned-route `hero_model.skin_id=None`; expected model ID/filename, UUID,
   ownership and scene epoch still must agree.

Only after this exercise is accepted should the actor execute the full plan.

## Routes and fences

- Original hero-list `on_hero_click` -> original hero scene ->
  `hero_common.on_tab_click('wardrobe', instant=True)`. The original wardrobe tab
  deliberately hides `hero_common` itself; the tool requires its valid identity
  and `tab_now='wardrobe'`, and visible valid wardrobe/model panels.
- Owned exact UUID with exactly one eligible visible component:
  `select_skin(uuid, notify=True)`. Multiple owned instances are chosen by sorted
  UUID and recorded; this does not cover every instance's custom dye.
- Owned `isInvisibleAwakeSkin` uses the original explicit `select_skin` branch;
  current canonical awakening stage/style are recorded and never changed.
- Filtered/non-owned catalog skins: `enter_buy`, only an actual visible offered
  catalog component (or its exact displayed `dye_skin` pair), then
  `ue_explor_skin`. No inferred `ori_skin` alias. Missing original entry means
  `original_UI_unreachable`. Cleanup uses original `exit_buy`.
- No `ue_skin_click`, wear/buy/sell, dye/awakening/pendant mutation, direct model
  swap, timer/lock/task cancellation or collection injection is used.

One job is outstanding. Three identical semantic readiness samples, each at
least 500ms apart, precede a token/generation/model-epoch screenshot handshake.
PNG chunk checksums and full display dimensions are checked. Hair/SFX pixels are
not required to freeze. Selection, owner/proxy, scene, panel, model epoch or
permanent state changes stop that job. Every transport command has a fresh nonce,
so a retry cannot consume a previous same-job idle status.

Read-only checks hash the raw canonical proxy profile, exact raw native
wear/awake/pendant/skin dye fields, and the **actual OfflineSaveStore envelope's
payload.profile**. Dict and JSON-string payloads are parsed; absent/corrupt
profiles fail. Existing checksum/revision and whole-file hash are recorded, not
re-encoded or written back. Whole-save changes outside profile (such as original
seen bookkeeping) are evidence, not automatically inventory changes. Known
seen/read/heartbeat RPCs are recorded separately. Forbidden **or unclassified**
outgoing RPCs pause the batch; actor review is required, never silent approval.

## Failure, resume, and visual review

On a normal load/settle failure, a clean original UI return and drained/settled
original task queues are required before a single retry. Two attempts total per
job apply across resume. Persistent failure is recorded and the queue can
continue only after safe cleanup. Any late task, user navigation, mutation or
transport uncertainty pauses the batch. `fatal.json` and `active-job.json` retain
host failures. Nothing restores a prior save, clears original tasks, or forges a
successful result.

For a paused run, the actor first returns using original Back to the visible hero
list. `--resume --execute` can recover audit-only state only if the same owner,
proxy, permanent baseline and drained old task queues are revalidated. If that
cannot be proven, it refuses; investigate/restart normally and re-read package,
GPU and inventory identity. Do not edit a save or force tasks to zero. Completed
job checkpoints are skipped only for the same run, catalog plan, probe hash,
package/resource/GPU identity and inventory signature.

Visual review is a separate offline operation, with no ADB:

```json
[{"job_id":"skin-10080","frame_sha256":"<exact PNG hash>","reviewer":"<name>","verdict":"pass","notes":"<actual material/dye observations>"}]
```

```sh
.venv/bin/python tools/audit_wardrobe_readonly.py --review /absolute/path/reviews.json --out-dir reports/actor-wardrobe-99
```

Only an explicit reviewer verdict bound to a successfully loaded frame hash
produces `rendered_and_visually_reviewed`; a failed material review is
`visual_failed`. Review after the final execution/resume, retaining the separate
review ledger. Hero baselines and skin appearances have separate summary
coverage counts. The audit does not cover every animation, combat combination,
or hypothetical awakening/dye configuration.

## Offline verification

```sh
.venv/bin/python -m unittest discover -s tests -p 'test_wardrobe_readonly_audit.py' -q
```

Tests execute the host loop against a fake transport and a deterministic original
UI simulator, including real command-source parsing, nonces, screenshot
handshake, original cleanup, profile-envelope changes and identity fences. Mock
PNG frames and fake renderer values are test fixtures, never native evidence.

## Retry evidence and verified cleanup RPCs

Each job has a total budget of two attempts across resumes. An exclusive
`.reserved` file is created before native dispatch; existing checkpoints or
PNG/log/reservation files consume that slot, including interrupted attempts.
PNG/log creation is exclusive and never overwrites evidence. Exhausted runs
pause; use a new directory for a deliberately new batch. Keep the failed ledger.

The reliable wrapper is decoded as JSON or a literal Python dictionary. Only
exact `w={m:pullEvents,p:{},r:<integer>}` with optional outer `_cbid_` is allowed:
this is `derived_event_refresh`, since the original handler can save derived
available-event state. Permanent-profile guards still apply. Unknown/malformed
wrappers and inner writes pause. The exact original listener call
`regist_chat_channel_listener {cn:1,scn:1}` and its immediately matching
`UNIMPLEMENTED` diagnostic are verified local no-ops; other chat calls pause.
