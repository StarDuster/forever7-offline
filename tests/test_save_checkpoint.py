#!/usr/bin/env python3
"""Static unit tests for save_checkpoint.py using synthetic fixtures only.

Run with:  python3 tests/test_save_checkpoint.py
These tests never read the live emulator, any pulled private files, or the
repository's analysis fixtures.
"""

from __future__ import annotations
import _paths  # noqa: E402,F401

import importlib.util
import json
import struct
import tempfile
import unittest
from unittest import mock
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE.parent / "offline" / "tools" / "save_checkpoint.py"
SPEC = importlib.util.spec_from_file_location("save_checkpoint", MODULE_PATH)
checkpoint = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checkpoint)

ACCOUNT = "offline_" + "ab" * 12
OTHER_ACCOUNT = "offline_" + "cd" * 12
NUMERIC_ID = 7
MANAGER_DEX = "1" * 64


# ---------------------------------------------------------------------------
# synthetic encoders
# ---------------------------------------------------------------------------


def _cstring(text: str) -> bytes:
    return text.encode("utf-8") + b"\x00"


def _bson_value(value):
    if isinstance(value, bool):
        return 0x08, bytes([1 if value else 0])
    if isinstance(value, int):
        if -(2**31) <= value < 2**31:
            return 0x10, struct.pack("<i", value)
        return 0x12, struct.pack("<q", value)
    if isinstance(value, float):
        return 0x01, struct.pack("<d", value)
    if isinstance(value, str):
        raw = value.encode("utf-8") + b"\x00"
        return 0x02, struct.pack("<i", len(raw)) + raw
    if value is None:
        return 0x0A, b""
    if isinstance(value, dict):
        return 0x03, bson_encode(value)
    if isinstance(value, list):
        return 0x04, bson_encode({str(index): item for index, item in enumerate(value)})
    if isinstance(value, bytes):
        return 0x05, struct.pack("<i", len(value)) + b"\x00" + value
    raise TypeError(type(value))


def bson_encode(document: dict) -> bytes:
    body = bytearray()
    for key, value in document.items():
        element_type, payload = _bson_value(value)
        body.append(element_type)
        body.extend(_cstring(key))
        body.extend(payload)
    body.append(0)
    return struct.pack("<i", len(body) + 4) + bytes(body)


def properties_text(values: dict[str, str], comment: str = "Project7 local event progress v2") -> bytes:
    lines = ["#" + comment]
    for key, value in values.items():
        lines.append(
            checkpoint.java_properties_escape(key, key=True)
            + "="
            + checkpoint.java_properties_escape(value)
        )
    return ("\n".join(lines) + "\n").encode("latin-1")


def progress_values(**overrides) -> dict[str, str]:
    values = {
        "schemaVersion": "2",
        "availableEvents": "",
        "processingEvents": "",
        "completedEvents": "1000",
        "initPrologue": "true",
        "processingNewbees": "",
        "finishedNewbees": "10,90,93,94",
        "inEmergency": "false",
        "status": "city",
        "scene": "1",
        "patrol.count": "0",
        "patrol.area": "0",
        "patrol.day": "0:0",
        "patrol.actions": "-1",
        "patrol.sandglass": "-1",
        "economy.commit": "",
        "week.commit": "",
        "week.index": "0",
        "patrol.favor": "0",
        "patrol.rewardPending": "false",
        "patrol.heroes": "",
        "patrol.events": "",
        "patrol.replays": "",
        "event.completed.1000": "1",
        "event.day.1000": "0:0",
        "condition.dialog": "1000",
    }
    values.update(overrides)
    return values


def profile_document(account: str = ACCOUNT, uid: int = NUMERIC_ID, **overrides) -> dict:
    document = {
        "account": account,
        "an": account,
        "uid": uid,
        "sv": 1,
        "level": 1,
        "weeknum": {"w": 0, "d": 0, "c": {}, "l": {}},
        "heromgr": {"hrs": [[2, {"i": 2}]], "es": [10001]},
        "inv": {"items": [], "mc": 0},
        "q7Battle": {},
    }
    document.update(overrides)
    return document


def write_registry(root: Path, account: str, record: str, numeric_id: int) -> str:
    digest = checkpoint.account_record_digest(record)
    (root / "accounts.properties").write_bytes(
        properties_text({account: record}, "Project7 local accounts")
    )
    (root / "account-ids.properties").write_bytes(
        properties_text({account: str(numeric_id)}, "Project7 stable account IDs")
    )
    identity = {
        "schema": "1",
        "backend": "project7",
        "phase": "READY",
        "step": "PROFILE_SAVED",
        "account": account,
        "numericId": str(numeric_id),
        "managerDex": MANAGER_DEX,
        "accountRecordSha256": digest,
        "postProfilePolicy": "p7-full-collection-v1",
        "secret": "2" * 64,
    }
    (root / "p7-bootstrap").mkdir(parents=True, exist_ok=True)
    (root / "p7-bootstrap" / "identity.properties").write_bytes(
        properties_text(identity, "App-private bootstrap identity; do not export")
    )
    return digest


def make_files_root(parent: Path, account: str = ACCOUNT, numeric_id: int = NUMERIC_ID,
                    record: str = "120000:abc:def", profile: dict | None = None,
                    values: dict[str, str] | None = None) -> tuple[Path, str]:
    root = parent
    root.mkdir(parents=True, exist_ok=True)
    digest = write_registry(root, account, record, numeric_id)
    (root / "profiles").mkdir(exist_ok=True)
    (root / "tutorials").mkdir(exist_ok=True)
    if profile is not None:
        (root / "profiles" / f"{account}.bson").write_bytes(bson_encode(profile))
    if values is not None:
        (root / "tutorials" / f"{account}.properties").write_bytes(properties_text(values))
    return root, digest


class CheckpointTestCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="p7-checkpoint-test-")
        self.base = Path(self.temp.name)
        self.source = self.base / "source"
        self.store = self.base / "store"
        self.target = self.base / "target"
        make_files_root(
            self.source,
            profile=profile_document(),
            values=progress_values(),
        )
        make_files_root(self.target)

    def tearDown(self):
        self.temp.cleanup()

    def export(self, label="hospital", milestone="hospital-menu-v1", source=None):
        return checkpoint.export_checkpoint(
            label,
            source or self.source,
            ACCOUNT,
            self.store,
            milestone,
        )

    def assert_refusal(self, code, function, *args, **kwargs):
        with self.assertRaises(checkpoint.Refusal) as context:
            function(*args, **kwargs)
        self.assertEqual(context.exception.code, code, str(context.exception))
        return context.exception


class PropertiesTests(unittest.TestCase):
    def test_escaped_key_and_continuation(self):
        data = (
            b"#comment\n"
            b"condition.client\\:101=101\n"
            b"long.value=abc\\\n"
            b"   def\n"
            b"unicode=line\\u0031\n"
        )
        parsed = checkpoint.parse_java_properties(data)
        self.assertEqual(parsed["condition.client:101"], "101")
        self.assertEqual(parsed["long.value"], "abcdef")
        self.assertEqual(parsed["unicode"], "line1")

    def test_duplicate_key_is_rejected(self):
        with self.assertRaises(checkpoint.Refusal) as context:
            checkpoint.parse_java_properties(b"a=1\na=2\n")
        self.assertEqual(context.exception.code, "PROPERTIES_PARSE")

    def test_escape_roundtrip(self):
        values = {"a.b:c": "x:y=z", "day": "0:0"}
        parsed = checkpoint.parse_java_properties(properties_text(values))
        self.assertEqual(parsed, values)


class BSONTests(unittest.TestCase):
    def test_roundtrip_and_trailing_bytes(self):
        encoded = bson_encode(profile_document())
        decoded = checkpoint.bson_decode(encoded)
        self.assertEqual(decoded["account"], ACCOUNT)
        with self.assertRaises(checkpoint.BSONError):
            checkpoint.bson_decode(encoded + b"\x00")

    def test_declared_length_mismatch(self):
        encoded = bytearray(bson_encode({"a": 1}))
        encoded[0:4] = struct.pack("<i", 99)
        with self.assertRaises(checkpoint.BSONError):
            checkpoint.bson_decode(bytes(encoded))

    def test_int64_field_decodes_as_python_int(self):
        document = {"uid": 2**40}
        # Force int64 encoding by using a value outside int32.
        data = bson_encode(document)
        decoded = checkpoint.bson_decode(data)
        self.assertEqual(decoded["uid"], 2**40)
        self.assertIs(type(decoded["uid"]), int)
        with self.assertRaises(checkpoint.Refusal):
            checkpoint.inspect_profile(
                bson_encode(profile_document(uid=2**40)), ACCOUNT, 2**40
            )


class ExportVerifyRestoreTests(CheckpointTestCase):
    def test_export_verify_restore_and_repeat(self):
        exported = self.export()
        self.assertEqual(exported["milestone"], "hospital-menu-v1")
        self.assertEqual(exported["completed_events"], [1000])
        self.assertTrue((self.store / "hospital" / "manifest.json").is_file())

        verified = checkpoint.verify_checkpoint("hospital", self.store, binding=self.source)
        self.assertEqual(verified["account"], ACCOUNT)
        self.assertEqual(verified["numeric_id"], NUMERIC_ID)
        self.assertEqual(verified["binding"]["artifact_mismatch"], False)

        dry = checkpoint.restore_checkpoint("hospital", self.target, self.store, dry_run=True)
        self.assertTrue(dry["dry_run"])
        self.assertFalse((self.target / "profiles" / f"{ACCOUNT}.bson").exists())

        checkpoint.restore_checkpoint("hospital", self.target, self.store)
        restored_profile = (self.target / "profiles" / f"{ACCOUNT}.bson").read_bytes()
        restored_tutorial = (self.target / "tutorials" / f"{ACCOUNT}.properties").read_bytes()
        self.assertEqual(
            restored_profile,
            (self.source / "profiles" / f"{ACCOUNT}.bson").read_bytes(),
        )
        self.assertEqual(
            restored_tutorial,
            (self.source / "tutorials" / f"{ACCOUNT}.properties").read_bytes(),
        )

        # Restoring repeatedly must produce the exact same bytes and must not
        # touch the account registry or the bootstrap journal.
        registry_before = (self.target / "accounts.properties").read_bytes()
        identity_before = (self.target / "p7-bootstrap" / "identity.properties").read_bytes()
        checkpoint.restore_checkpoint("hospital", self.target, self.store)
        self.assertEqual(
            (self.target / "profiles" / f"{ACCOUNT}.bson").read_bytes(), restored_profile
        )
        self.assertEqual(
            (self.target / "tutorials" / f"{ACCOUNT}.properties").read_bytes(), restored_tutorial
        )
        self.assertEqual((self.target / "accounts.properties").read_bytes(), registry_before)
        self.assertEqual(
            (self.target / "p7-bootstrap" / "identity.properties").read_bytes(), identity_before
        )

    def test_collection_menu_milestone_preserves_bbs_city_progress(self):
        make_files_root(
            self.source,
            profile=profile_document(),
            values=progress_values(status="bbs", scene="1", completedEvents="1000"),
        )
        exported = self.export("collection", milestone="collection-menu-v1")
        self.assertEqual(exported["milestone"], "collection-menu-v1")
        self.assertEqual(exported["completed_events"], [1000])
        verified = checkpoint.verify_checkpoint("collection", self.store, binding=self.source)
        manifest = json.loads((self.store / "collection" / "manifest.json").read_text())
        self.assertEqual(manifest["story"]["status"], "bbs")
        checkpoint.restore_checkpoint("collection", self.target, self.store)
        self.assertEqual(
            (self.target / "tutorials" / f"{ACCOUNT}.properties").read_bytes(),
            (self.source / "tutorials" / f"{ACCOUNT}.properties").read_bytes(),
        )
        self.assertEqual(
            (self.target / "profiles" / f"{ACCOUNT}.bson").read_bytes(),
            (self.source / "profiles" / f"{ACCOUNT}.bson").read_bytes(),
        )

    def test_collection_menu_rejects_city_status(self):
        make_files_root(
            self.source,
            profile=profile_document(),
            values=progress_values(status="city", scene="1", completedEvents="1000"),
        )
        self.assert_refusal(
            "MILESTONE_UNMET",
            checkpoint.export_checkpoint,
            "collection-bad", self.source, ACCOUNT, self.store, "collection-menu-v1",
        )

    def test_login_milestone_exports_pre_hospital_state(self):
        values = progress_values(
            completedEvents="",
            availableEvents="1000",
            status="emergency",
            inEmergency="true",
            scene="",
        )
        values.pop("event.completed.1000")
        values.pop("event.day.1000")
        values.pop("condition.dialog")
        source = self.base / "pre-hospital"
        make_files_root(source, profile=profile_document(), values=values)
        exported = checkpoint.export_checkpoint(
            "login", source, ACCOUNT, self.store, "login-v1"
        )
        self.assertEqual(exported["completed_events"], [])
        checkpoint.verify_checkpoint("login", self.store)

    def test_default_milestone_refuses_pre_hospital_state(self):
        values = progress_values(
            completedEvents="",
            availableEvents="1000",
            status="emergency",
            inEmergency="true",
            scene="",
        )
        values.pop("event.completed.1000")
        values.pop("event.day.1000")
        values.pop("condition.dialog")
        source = self.base / "pre-hospital"
        make_files_root(source, profile=profile_document(), values=values)
        self.assert_refusal(
            "MILESTONE_UNMET",
            checkpoint.export_checkpoint,
            "login",
            source,
            ACCOUNT,
            self.store,
            "hospital-menu-v1",
        )

    def test_refuses_completion_counter_without_completed_event(self):
        values = progress_values(**{"event.completed.1002": "1"})
        source = self.base / "bad-counter"
        make_files_root(source, profile=profile_document(), values=values)
        self.assert_refusal(
            "STORY_INCONSISTENT",
            checkpoint.export_checkpoint,
            "bad", source, ACCOUNT, self.store, "hospital-menu-v1",
        )

    def test_refuses_event_both_completed_and_processing(self):
        values = progress_values(
            processingEvents="1002", completedEvents="1000,1002",
            **{"event.completed.1002": "1"},
        )
        source = self.base / "overlap"
        make_files_root(source, profile=profile_document(), values=values)
        self.assert_refusal(
            "STORY_INCONSISTENT",
            checkpoint.export_checkpoint,
            "bad", source, ACCOUNT, self.store, "hospital-menu-v1",
        )

    def test_hospital_milestone_allows_in_flight_hospital_dialogue(self):
        values = progress_values(
            completedEvents="",
            availableEvents="",
            processingEvents="1000",
            status="emergency",
            inEmergency="true",
            scene="",
        )
        for key in ("event.completed.1000", "event.day.1000", "condition.dialog"):
            values.pop(key)
        source = self.base / "hospital-dialogue"
        make_files_root(source, profile=profile_document(), values=values)
        exported = checkpoint.export_checkpoint(
            "arrival", source, ACCOUNT, self.store, "hospital-menu-v1"
        )
        self.assertEqual(exported["completed_events"], [])
        stored = json.loads((self.store / "arrival" / "manifest.json").read_text())
        self.assertFalse(stored["story"]["quiescent"])
        self.assertEqual(stored["story"]["processing_events"], [1000])
        checkpoint.verify_checkpoint("arrival", self.store)

    def test_hospital_milestone_allows_follow_up_processing(self):
        values = progress_values(processingEvents="1002")
        source = self.base / "processing"
        make_files_root(source, profile=profile_document(), values=values)
        exported = checkpoint.export_checkpoint(
            "follow-up", source, ACCOUNT, self.store, "hospital-menu-v1"
        )
        self.assertEqual(exported["completed_events"], [1000])

    def test_login_milestone_refuses_arrived_state(self):
        self.assert_refusal(
            "MILESTONE_UNMET",
            checkpoint.export_checkpoint,
            "login", self.source, ACCOUNT, self.store, "login-v1",
        )

    def test_refuses_incomplete_schema(self):
        values = progress_values()
        del values["week.commit"]
        source = self.base / "missing-key"
        make_files_root(source, profile=profile_document(), values=values)
        self.assert_refusal(
            "PROGRESS_SCHEMA",
            checkpoint.export_checkpoint,
            "bad", source, ACCOUNT, self.store, "hospital-menu-v1",
        )

    def test_refuses_profile_identity_mismatch(self):
        source = self.base / "wrong-account"
        make_files_root(
            source,
            profile=profile_document(account=OTHER_ACCOUNT, uid=NUMERIC_ID),
            values=progress_values(),
        )
        self.assert_refusal(
            "PROFILE_IDENTITY_MISMATCH",
            checkpoint.export_checkpoint,
            "bad", source, ACCOUNT, self.store, "hospital-menu-v1",
        )

    def test_refuses_template_account(self):
        self.assert_refusal(
            "TEMPLATE_ACCOUNT_REFUSED",
            checkpoint.export_checkpoint,
            "bad", self.source, "tencolors", self.store, "hospital-menu-v1",
        )

    def test_refuses_unbound_account(self):
        self.assert_refusal(
            "ACCOUNT_INVALID",
            checkpoint.export_checkpoint,
            "bad", self.source, "codextest", self.store, "hospital-menu-v1",
        )

    def test_refuses_week_receipt_mismatch(self):
        receipt = {
            "id": "a" * 24,
            "week": 0,
            "method": "requestEnterStory",
            "route": 1,
            "progress": {key: "" for key in checkpoint.REQUIRED_PROGRESS_KEYS},
        }
        receipt["progress"]["schemaVersion"] = "2"
        receipt["progress"]["week.commit"] = receipt["id"]
        receipt["progress"]["week.index"] = "0"
        receipt["progress"]["availableEvents"] = ""
        source = self.base / "week-receipt"
        make_files_root(
            source,
            profile=profile_document(q7WeekTransition=receipt),
            values=progress_values(),
        )
        self.assert_refusal(
            "CONSISTENCY_WEEK_RECEIPT",
            checkpoint.export_checkpoint,
            "bad", source, ACCOUNT, self.store, "hospital-menu-v1",
        )

    def test_refuses_economy_receipt_mismatch(self):
        source = self.base / "economy-receipt"
        make_files_root(
            source,
            profile=profile_document(q7EconomyCommit={"id": "b" * 24}),
            values=progress_values(**{"economy.commit": "c" * 24}),
        )
        self.assert_refusal(
            "CONSISTENCY_ECONOMY_RECEIPT",
            checkpoint.export_checkpoint,
            "bad", source, ACCOUNT, self.store, "hospital-menu-v1",
        )

    def test_refuses_stale_temp_and_pending_transaction(self):
        source = self.base / "stale"
        make_files_root(source, profile=profile_document(), values=progress_values())
        (source / "profiles" / f"{ACCOUNT}.bson.tmp").write_bytes(b"x")
        self.assert_refusal(
            "STALE_TEMP_FILE",
            checkpoint.export_checkpoint,
            "bad", source, ACCOUNT, self.store, "hospital-menu-v1",
        )
        (source / "profiles" / f"{ACCOUNT}.bson.tmp").unlink()
        journal = source / "save-transactions" / "1234"
        journal.mkdir(parents=True)
        (journal / "pending.properties").write_bytes(b"target=x\n")
        self.assert_refusal(
            "PENDING_SAVE_TRANSACTION",
            checkpoint.export_checkpoint,
            "bad", source, ACCOUNT, self.store, "hospital-menu-v1",
        )

    def test_refuses_identity_not_ready(self):
        identity_path = self.source / "p7-bootstrap" / "identity.properties"
        identity = checkpoint.parse_java_properties(identity_path.read_bytes())
        identity["phase"] = "PREPARING"
        identity["step"] = "PROFILE_STARTED"
        identity_path.write_bytes(properties_text(identity))
        self.assert_refusal(
            "IDENTITY_NOT_READY",
            checkpoint.export_checkpoint,
            "bad", self.source, ACCOUNT, self.store, "hospital-menu-v1",
        )

    def test_refuses_existing_label_without_replace(self):
        self.export()
        self.assert_refusal("CHECKPOINT_EXISTS", self.export)
        checkpoint.export_checkpoint(
            "hospital", self.source, ACCOUNT, self.store, "hospital-menu-v1", replace=True
        )

    def test_verify_detects_tampered_profile(self):
        self.export()
        profile_path = self.store / "hospital" / "files" / "profiles" / f"{ACCOUNT}.bson"
        data = bytearray(profile_path.read_bytes())
        data[-1] ^= 0x01
        profile_path.write_bytes(bytes(data))
        self.assert_refusal(
            "MANIFEST_HASH_MISMATCH",
            checkpoint.verify_checkpoint,
            "hospital",
            self.store,
        )

    def test_verify_detects_tampered_story(self):
        self.export()
        manifest_path = self.store / "hospital" / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["story"]["completed_events"] = []
        manifest_path.write_text(json.dumps(manifest))
        self.assert_refusal(
            "MANIFEST_STORY_MISMATCH",
            checkpoint.verify_checkpoint,
            "hospital",
            self.store,
        )

    def test_valid_week_receipt_matches_commit(self):
        receipt_id = "d" * 24
        receipt_progress = {key: "" for key in checkpoint.REQUIRED_PROGRESS_KEYS}
        receipt_progress.update(
            {
                "schemaVersion": "2",
                "week.commit": receipt_id,
                "week.index": "0",
                "availableEvents": "",
            }
        )
        receipt = {
            "id": receipt_id,
            "week": 0,
            "method": "requestEnterStory",
            "route": 1,
            "progress": receipt_progress,
        }
        profile_data = bson_encode(profile_document(q7WeekTransition=receipt))
        profile = checkpoint.inspect_profile(profile_data, ACCOUNT, NUMERIC_ID)
        self.assertEqual(profile["week_receipt"]["id"], receipt_id)
        # A week transition cannot satisfy the first-run milestones, but the
        # receipt/commit consistency itself must pass.
        progress = checkpoint.inspect_progress(
            properties_text(progress_values(**{"week.commit": receipt_id}))
        )
        consistency = checkpoint.build_consistency(profile, progress)
        self.assertTrue(consistency["week_receipt_matches"])

    def test_export_from_parent_with_files_subdir(self):
        pull = self.base / "pull"
        (pull / "files").mkdir(parents=True)
        make_files_root(pull / "files", profile=profile_document(), values=progress_values())
        exported = checkpoint.export_checkpoint(
            "nested", pull, ACCOUNT, self.store, "hospital-menu-v1"
        )
        self.assertEqual(exported["account"], ACCOUNT)
        checkpoint.verify_checkpoint("nested", self.store)

    def test_refuses_status_emergency_flag_mismatch(self):
        source = self.base / "flag-mismatch"
        make_files_root(
            source,
            profile=profile_document(),
            values=progress_values(status="emergency", inEmergency="false"),
        )
        self.assert_refusal(
            "STORY_INCONSISTENT",
            checkpoint.export_checkpoint,
            "bad", source, ACCOUNT, self.store, "hospital-menu-v1",
        )

    def test_refuses_unknown_progress_key(self):
        values = progress_values(**{"future.flag": "1"})
        source = self.base / "unknown-key"
        make_files_root(source, profile=profile_document(), values=values)
        self.assert_refusal(
            "PROGRESS_SCHEMA",
            checkpoint.export_checkpoint,
            "bad", source, ACCOUNT, self.store, "hospital-menu-v1",
        )

    def test_refuses_symlinked_profile(self):
        source = self.base / "symlink"
        make_files_root(source, profile=profile_document(), values=progress_values())
        profile_path = source / "profiles" / f"{ACCOUNT}.bson"
        real_path = source / "profiles" / "real.bson"
        profile_path.rename(real_path)
        profile_path.symlink_to(real_path)
        self.assert_refusal(
            "PROFILE_INVALID",
            checkpoint.export_checkpoint,
            "bad", source, ACCOUNT, self.store, "hospital-menu-v1",
        )

    def test_verify_detects_extra_file(self):
        self.export()
        (self.store / "hospital" / "identity.properties").write_text("secret=1\n")
        self.assert_refusal(
            "CHECKPOINT_FILE_EXTRA",
            checkpoint.verify_checkpoint,
            "hospital",
            self.store,
        )

    def test_verify_binding_detects_account_record_change(self):
        self.export()
        checkpoint.verify_checkpoint("hospital", self.store, binding=self.source)
        (self.source / "accounts.properties").write_bytes(
            properties_text({ACCOUNT: "120000:different:value"})
        )
        self.assert_refusal(
            "IDENTITY_MISMATCH",
            checkpoint.verify_checkpoint,
            "hospital",
            self.store,
            self.source,
        )

    def test_restore_first_replace_failure_preserves_old_pair(self):
        self.export()
        old_profile = bson_encode(profile_document(level=2))
        old_progress = properties_text(progress_values(completedEvents="1000"))
        (self.target / "profiles" / f"{ACCOUNT}.bson").write_bytes(old_profile)
        (self.target / "tutorials" / f"{ACCOUNT}.properties").write_bytes(old_progress)
        real_replace = checkpoint.os.replace
        calls = {"n": 0}

        def fail_first(src, dst):
            calls["n"] += 1
            if calls["n"] == 1:
                raise OSError("injected first replace failure")
            return real_replace(src, dst)

        with mock.patch.object(checkpoint.os, "replace", side_effect=fail_first):
            self.assert_refusal(
                "RESTORE_IO_ROLLED_BACK",
                checkpoint.restore_checkpoint,
                "hospital", self.target, self.store,
            )
        self.assertEqual((self.target / "profiles" / f"{ACCOUNT}.bson").read_bytes(), old_profile)
        self.assertEqual((self.target / "tutorials" / f"{ACCOUNT}.properties").read_bytes(), old_progress)
        self.assertEqual(list(self.target.glob(".p7-restore-*")), [])

    def test_successful_restore_removes_transaction_marker(self):
        self.export()
        checkpoint.restore_checkpoint("hospital", self.target, self.store)
        self.assertEqual(list(self.target.glob(".p7-restore-*")), [])

    def test_restore_second_replace_failure_rolls_back_pair(self):
        self.export()
        old_profile = bson_encode(profile_document(level=2))
        old_progress = properties_text(progress_values(completedEvents="1000"))
        (self.target / "profiles" / f"{ACCOUNT}.bson").write_bytes(old_profile)
        (self.target / "tutorials" / f"{ACCOUNT}.properties").write_bytes(old_progress)
        real_replace = checkpoint.os.replace
        calls = {"n": 0}

        def fail_second(src, dst):
            calls["n"] += 1
            if calls["n"] == 2:
                raise OSError("injected second replace failure")
            return real_replace(src, dst)

        with mock.patch.object(checkpoint.os, "replace", side_effect=fail_second):
            self.assert_refusal(
                "RESTORE_IO_ROLLED_BACK",
                checkpoint.restore_checkpoint,
                "hospital", self.target, self.store,
            )
        self.assertEqual((self.target / "profiles" / f"{ACCOUNT}.bson").read_bytes(), old_profile)
        self.assertEqual((self.target / "tutorials" / f"{ACCOUNT}.properties").read_bytes(), old_progress)
        self.assertEqual(list(self.target.glob(".p7-restore-*")), [])

    def test_restore_rollback_failure_leaves_pending_marker(self):
        self.export()
        old_profile = bson_encode(profile_document(level=2))
        old_progress = properties_text(progress_values(completedEvents="1000"))
        (self.target / "profiles" / f"{ACCOUNT}.bson").write_bytes(old_profile)
        (self.target / "tutorials" / f"{ACCOUNT}.properties").write_bytes(old_progress)
        real_replace = checkpoint.os.replace
        calls = {"n": 0}

        def fail_after_first(src, dst):
            calls["n"] += 1
            if calls["n"] >= 2:
                raise OSError("injected replace/rollback failure")
            return real_replace(src, dst)

        with mock.patch.object(checkpoint.os, "replace", side_effect=fail_after_first):
            self.assert_refusal(
                "RESTORE_MIXED",
                checkpoint.restore_checkpoint,
                "hospital", self.target, self.store,
            )
        self.assertTrue(list(self.target.glob(".p7-restore-*.journal")))
        self.assert_refusal(
            "PENDING_RESTORE",
            checkpoint.restore_checkpoint,
            "hospital", self.target, self.store,
        )

    def test_restore_refuses_target_record_mismatch(self):
        self.export()
        record = "120000:different:value"
        (self.target / "accounts.properties").write_bytes(
            properties_text({ACCOUNT: record})
        )
        identity_path = self.target / "p7-bootstrap" / "identity.properties"
        identity = checkpoint.parse_java_properties(identity_path.read_bytes())
        identity["accountRecordSha256"] = checkpoint.account_record_digest(record)
        identity_path.write_bytes(properties_text(identity))
        self.assert_refusal(
            "TARGET_ACCOUNT_RECORD_MISMATCH",
            checkpoint.restore_checkpoint,
            "hospital", self.target, self.store,
        )

    def test_restore_refuses_target_numeric_id_mismatch(self):
        self.export()
        (self.target / "account-ids.properties").write_bytes(
            properties_text({ACCOUNT: str(NUMERIC_ID + 1)})
        )
        identity_path = self.target / "p7-bootstrap" / "identity.properties"
        identity = checkpoint.parse_java_properties(identity_path.read_bytes())
        identity["numericId"] = str(NUMERIC_ID + 1)
        identity_path.write_bytes(properties_text(identity))
        self.assert_refusal(
            "TARGET_NUMERIC_ID_MISMATCH",
            checkpoint.restore_checkpoint,
            "hospital", self.target, self.store,
        )

    def test_restore_refuses_target_profile_of_other_account(self):
        self.export()
        (self.target / "profiles" / f"{ACCOUNT}.bson").write_bytes(
            bson_encode(profile_document(account=OTHER_ACCOUNT, uid=NUMERIC_ID))
        )
        self.assert_refusal(
            "TARGET_PROFILE_ACCOUNT_MISMATCH",
            checkpoint.restore_checkpoint,
            "hospital", self.target, self.store,
        )

    def test_restore_refuses_progress_without_profile(self):
        self.export()
        (self.target / "tutorials" / f"{ACCOUNT}.properties").write_bytes(
            properties_text(progress_values())
        )
        self.assert_refusal(
            "TARGET_PROGRESS_WITHOUT_PROFILE",
            checkpoint.restore_checkpoint,
            "hospital", self.target, self.store,
        )

    def test_restore_refuses_device_path(self):
        self.export()
        self.assert_refusal(
            "DEVICE_PATH_REFUSED",
            checkpoint.restore_checkpoint,
            "hospital", Path("/data/data/com.netease.qrzd/files"), self.store,
        )

    def test_restore_refuses_stale_temp(self):
        self.export()
        (self.target / "tutorials" / f"{ACCOUNT}.properties.tmp").write_bytes(b"x")
        self.assert_refusal(
            "STALE_TEMP_FILE",
            checkpoint.restore_checkpoint,
            "hospital", self.target, self.store,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
