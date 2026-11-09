# Private save checkpoints for the single-APK build

This directory is ignored by Git (`/local-checkpoints/` in `.gitignore`). It contains a
private, offline helper for exporting, verifying and restoring one Project7 (single-APK)
save at the "hospital / menu arrival" milestone. It never invokes adb, an emulator, a
gateway, or any Android API.

```
tools/save_checkpoint.py       executable helper + library
tests/test_save_checkpoint.py synthetic-fixture unit tests
local-checkpoints/store/       created on demand; ignored private checkpoints only
```

Run the tests with:

```sh
python3 tests/test_save_checkpoint.py
```

## 1. Actual save contract

The single APK (`com.netease.qrzd` in the current build) keeps the manager's stock
persistence under its app-private `files/` directory. The checkpoint reads the following
layout, exactly as written by the stock stores:

| Path under `files/` | Writer | Role |
| --- | --- | --- |
| `profiles/<account>.bson` | `LocalProfileStore.writeAtomic` | profile (authoritative game state) |
| `tutorials/<account>.properties` | `LocalTutorialStore.save` | `Progress` schema 2 (story flags) |
| `accounts.properties` | `LocalAccountStore` | account registry (credential record) |
| `account-ids.properties` | `LocalAccountStore` | account -> numeric id |
| `p7-bootstrap/identity.properties` | `StableIdentityBootstrap` | bootstrap journal and identity binding |
| `save-transactions/<uuid>/pending.properties` | `LocalAccountArchive` | unfinished import journal (transient) |

Only `profiles/<account>.bson` and `tutorials/<account>.properties` are copied into a
checkpoint. The registry and the bootstrap journal are **read only** for identity
binding; the registry value contains credential material and is deliberately not
copied. `save-transactions` is a transient recovery journal: a pending journal or a
leftover `*.tmp` file is treated as an inconsistent source and export/restore refuses.

The game client's SharedPreferences (`neox_config`, resource verification caches) and
`Android/data/.../Documents` downloads are not part of the save contract: story state is
the manager's profile + Progress pair. They are therefore not checkpointed. Gateway
session state (`claimSession`, the active client socket, thread/lastServer fields) is
in-memory only and has no persisted file; it is re-created on each launch. The legacy
`runtime/offline*` Python JSON backend is not used by the single APK and is not part of
this contract.

A stale `save-transactions` journal and any `*.tmp` sibling are treated as an
inconsistent source/target. The checkpoint never includes the account registry or the
bootstrap journal, because the registry record is credential material; those files are
only read for identity binding.

### Profile (`*.bson`)

A strict BSON document (the helper uses a stdlib decoder with length, UTF-8, array-key
and duplicate-key validation). The checkpoint requires:

* `account` and `an` are strings equal to the account name;
* `uid` is an int equal to the numeric id in `account-ids.properties`;
* `weeknum` is a document with int `w` and `d` (non-negative);
* `q7Battle` is absent or an empty document (no battle is in flight);
* optional `q7WeekTransition`: `id` (24-hex), `week` (int), `method` (string),
  `route` (int), `progress` (a Progress property map with all 23 required keys as
  strings). Its `progress.week.commit` must equal `id` and
  `progress.week.index` must equal `week`;
* optional `q7EconomyCommit`: `id` is 24-hex;
* optional `q7FullCollectionReceiptV1`: schema, policy and three SHA-256 values, recorded
  as provenance metadata.

The BSON length field must equal the file length; payload size must be 1 byte .. 32 MiB.

### Progress (`*.properties`)

A `java.util.Properties` file written by `Progress.toProperties()`:
`schemaVersion=2` plus all 23 keys required by
`StableIdentityBootstrap.preflight`: `availableEvents`, `processingEvents`,
`completedEvents`, `initPrologue`, `processingNewbees`, `finishedNewbees`,
`inEmergency`, `status`, `scene`, `patrol.count`, `patrol.area`, `patrol.day`,
`patrol.actions`, `patrol.sandglass`, `economy.commit`, `week.commit`, `week.index`,
`patrol.favor`, `patrol.rewardPending`, `patrol.heroes`, `patrol.events`,
`patrol.replays`.

Dynamic keys follow the stock writer: `event.completed.<id>` (positive int),
`event.day.<id>` (`w:d`), `condition.<kind>` (comma-separated ints),
`patrol.fatigue.<hero>`, `patrol.friendly.<hero>`, `patrol.bonus.<hero>` (ints).

Validation includes Java `Properties` unescaping (`\:`, `\=`, `\uXXXX`, continuations),
canonical decimal integers, `true`/`false` booleans, non-empty/duplicate-free id sets,
sorted sets except `completedEvents` (order preserved by the stock codec), 24-hex
commit ids, and `inEmergency == (status == "emergency")`. Unknown keys are refused so a
silent schema drift cannot be checkpointed as if it were Progress v2.

### Account identity binding

`StableIdentityBootstrap.accountFingerprint` hashes the **unescaped** registry value:

```
accountRecordSha256 = sha256(unescape(accounts.properties[account])).hexdigest()
```

The bootstrap journal must have `schema=1`, `backend=project7`,
`phase=READY`, `step=PROFILE_SAVED`, an `offline_<24 lowercase hex>` account, a
`numericId` equal to `account-ids.properties[account]` and to the profile `uid`, and the
same `accountRecordSha256`. Export refuses template accounts (`tencolors`,
`hakopania`), old test accounts (`codextest`, ...) and any account that is not the
generated bootstrap form. Restore requires the target registry/identity to bind to the
same account, the same numeric id and the same record hash; it never writes those files.

### Consistency checks (refusals)

Hard refusals, all re-derived from the checkpoint bytes at verify/restore time:

* profile `account`/`an`/`uid` vs the manifest account/numeric id;
* `Progress.week.index == profile.weeknum.w`;
* if a week receipt exists: `id == week.commit` and `week == weeknum.w`; an absent
  receipt with a non-empty commit is accepted (the stock `recover` no-ops);
* if an economy receipt exists: `id == economy.commit`;
* `completedEvents ∩ processingEvents == ∅`;
* `processingNewbees ∩ finishedNewbees == ∅`;
* every positive `event.completed.<id>` counter refers to a member of
  `completedEvents`;
* the profile and tutorial file signatures (device/inode/size/mtime) are unchanged
  across export reads, so a concurrently writing app is refused
  (`SOURCE_CHANGED_DURING_READ`);
* no pending `save-transactions` journal and no stale `*.tmp` for the selected files.

Recorded warnings (not fatal): `availableEvents ∩ completedEvents` overlap and
`event.day.<id>` entries outside `completedEvents`.

### Milestones

`hospital-menu-v1` (default) requires:

* event `1000` (the hospital prologue) is **engaged**: either it is in
  `completedEvents` or it is in `processingEvents`;
* `status` is `city` or `emergency` (consistent with `inEmergency`);
* `week.index == 0` and `profile.weeknum.w == 0`, with no week receipt/commit;
* empty `q7Battle`, no stale temp and no pending import journal.

An in-flight event is allowed, because arrival at the hospital can be captured while
the prologue is still processing. Such a checkpoint records `"quiescent": false` and
restores the exact in-flight sets; it never moves a processing event to
`completedEvents`. A pre-hospital fresh save has `1000` only in `availableEvents` and is
therefore not a `hospital-menu-v1` checkpoint.

`login-v1` is the pre-hospital/bootstrap state:

* event `1000` is in `availableEvents`;
* `completedEvents`, `processingEvents` and `processingNewbees` are empty,
  `patrol.rewardPending == false`;
* `week.index == 0`, `profile.weeknum.w == 0`, no week receipt/commit;
* `status` `emergency` or `city`, empty `q7Battle`.

A checkpoint cannot encode a new week, a receipt/commit disagreement, an event that is
both processing and completed, a completion counter without its completed event, or a
status/inEmergency contradiction. Those are the "incomplete story flags" refusals. The
helper never edits event sets; restore copies the exact bytes and re-derives the story
digest.

## 2. Manifest and hashes

`store/<label>/manifest.json` records:

* manifest schema `project7-save-checkpoint/v1`, label, UTC creation time, milestone;
* `account`: name, numeric id, `record_sha256`, and the non-secret bootstrap journal
  fields (`phase`, `step`, `manager_dex`, `post_profile_policy`);
* `files`: the two relative paths with exact byte size and SHA-256;
* `profile`: identity, week, battle state, receipt metadata, aggregate counts;
* `progress`: schema, commits, ints/bools/strings, counts and per-set SHA-256;
* `story`: full story-relevant sets and counters, quiescence, plus a SHA-256 digest over
  the canonical story JSON;
* `consistency`: the booleans and warnings above.

Exact inventory is enforced: `verify` refuses any extra file (including a copied
identity/registry), any missing file, any symlink, and any size/hash mismatch. Required
files are:

```
<label>/manifest.json
<label>/files/profiles/<account>.bson
<label>/files/tutorials/<account>.properties
```

`verify` re-parses the two files, rebuilds every derived block and requires exact
equality with the manifest plus the recomputed story digest. With `--binding <files-dir>`
it additionally re-checks the account record hash and numeric id of a source/target
registry.

## 3. Commands

```sh
# Export exactly one explicitly named account from a pulled files directory.
python3 tools/save_checkpoint.py export arrival-20261106 \
  --from /tmp/p7-5560-pull --account offline_<24hex> \
  --milestone hospital-menu-v1

# Verify hashes, schema, account binding and story consistency.
python3 tools/save_checkpoint.py verify arrival-20261106 \
  --binding /tmp/p7-5560-pull

# Restore into a staging directory that already carries the same identity/account.
python3 tools/save_checkpoint.py restore arrival-20261106 \
  --to /tmp/p7-restore-target --dry-run
python3 tools/save_checkpoint.py restore arrival-20261106 \
  --to /tmp/p7-restore-target

# Machine-readable output (all three commands support --json).
python3 tools/save_checkpoint.py verify arrival-20261106 --json
```

`--from` / `--to` accept either the `files/` directory itself or a parent directory
containing `files/`. The default checkpoint root is `local-checkpoints/store`
(override with `--root`). `export` refuses an existing label unless `--replace` is
given. Restore writes both files through same-directory temporary files, fsyncs, and
renames; it refuses device-like targets (`/data/`, `/sdcard/`, `/storage/`, `/mnt/`,
`/system/`, `/vendor/`, `/product/`, `Android/data`), account/numeric-id mismatches,
a target profile belonging to another account, a tutorial without a profile, stale
temps and pending import journals. It prints the applied SHA-256 values and re-reads
both files plus the story block afterwards.

For a staging rehearsal, copy the *same install's* files tree first so the restored
target keeps the exact account registry and journal:

```sh
cp -a /tmp/p7-5560-pull/files /tmp/p7-restore-target
python3 tools/save_checkpoint.py restore hospital-menu-v1 \
  --to /tmp/p7-restore-target
```

Do not synthesize `accounts.properties`/`p7-bootstrap/identity.properties` and do not
copy them from another account: restore refuses a missing or different binding.

The two canonical files are committed by two renames, like the stock stores; they are
not a cross-file transaction. If the tutorial rename fails after the profile rename,
the helper reports `RESTORE_IO_FAILED`; stop, then rerun the restore after checking the
target. A checkpoint export with `--replace` keeps the previous checkpoint until the
new one is fully staged.

Restore deliberately does **not** create or copy an account. The target must already
contain the same generated `offline_<24hex>` identity, the same numeric id and the same
`accounts.properties` record hash; otherwise it refuses. Clearing app data or
uninstalling the APK removes that identity, and this helper will not reconstruct it
(that would be copying/recreating an account). A different `managerDex` or
`postProfilePolicy` in the target journal is reported as an `artifact_mismatch`
warning, because a rebuilt manager can change the collection-receipt catalog; verify
the receipt values in the manifest before using such a target.

Exit codes: `0` success, `2` usage error, `3` deliberate refusal with a stable code,
`1` unexpected error.

## 4. Deriving a checkpoint from the real 5560 files (not executed here)

The helper is offline only. Once the device owner stops the game and the manager
gateway and root permits a **read-only** pull, obtain the app-private directory without
writing to the repository:

```sh
# Example read-only pull; replace the package if the installed build differs.
adb -s emulator-5560 exec-out su 0 tar -C /data/data/com.netease.qrzd -cf - files \
  > /tmp/p7-5560-files.tar
mkdir -p /tmp/p7-5560-pull
tar -C /tmp/p7-5560-pull -xf /tmp/p7-5560-files.tar
```

(If the build is debuggable and `run-as` is permitted, use
`adb -s emulator-5560 exec-out run-as com.netease.qrzd tar -C /data/data/com.netease.qrzd -cf - files`
instead. Do not use `adb install`, `adb root`, or any emulator control from this helper.)

Before exporting:

1. Stop the game process and the manager gateway so no writer can race the pull; the
   real store's atomic renames are per-file and not a cross-file transaction.
2. Confirm `/tmp/p7-5560-pull/files` contains `accounts.properties`,
   `account-ids.properties`, `p7-bootstrap/identity.properties`,
   `profiles/<account>.bson` and `tutorials/<account>.properties`, with no
   `save-transactions/*/pending.properties` and no `*.tmp` siblings.
3. Read the account from `p7-bootstrap/identity.properties`
   (`account=offline_...`); pass that exact value to `--account`. Never select
   `tencolors`/`hakopania` or an old manager test account.
4. Export, verify, then restore into a **staging copy** first. To put the files back on
   the device, stop the app and preserve the current files; copy only the two restored
   files, then restore the original owner/mode and SELinux context (`chown`,
   `restorecon`) as appropriate. This helper does not perform device writes.

Keep the pulled tree and `local-checkpoints/store` outside Git; both are private.
