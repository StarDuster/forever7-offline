"""Pinned puzzle-room-4 delta, merge builder, and real-consumer boundary."""
import _paths  # noqa: E402,F401
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'offline' / 'current' / 'tools'))
sys.path.insert(0, str(ROOT / 'runtime'))
import project7_story_city_puzzle as puzzle
import story_city_virtual as virtual

EXTRA = ROOT / 'offline/current/data/project7_story_city_catalog/puzzle-extra.tsv'
BUILD = ROOT / 'runtime/build/project7_story_city_puzzle_room4'
DRIVER = ROOT / 'offline/current/java/android_story_city/puzzle_verify.py'


def setUpModule():
    puzzle.produce(BUILD)


class PuzzleRoom4AssetTests(unittest.TestCase):
    def test_delta_uses_only_parser_directives(self):
        rows = puzzle.data_rows(EXTRA.read_bytes())
        self.assertEqual(rows, [puzzle.PUZZLE_ROOM, *puzzle.PUZZLE_CLUES])
        self.assertEqual([row.split('\t')[0] for row in rows],
                         ['@puzzleRoom'] + ['@puzzleClue'] * 5)
        self.assertEqual(len(puzzle.PUZZLE_ROOM.split('\t')), 7)
        for row in puzzle.PUZZLE_CLUES:
            self.assertEqual(len(row.split('\t')), 4)

    def test_published_extra_is_pinned_and_merges_append_only(self):
        contract = puzzle.check(BUILD)
        self.assertEqual(contract['extra']['sha256'], puzzle.sha_bytes(EXTRA.read_bytes()))
        base = puzzle.BASE.read_bytes()
        merged = puzzle.merged_bytes(base, EXTRA.read_bytes())
        self.assertTrue(merged.startswith(base))
        self.assertEqual(merged, BUILD.joinpath('event_graph.tsv').read_bytes())
        self.assertEqual(len(puzzle.data_rows(merged)) - len(puzzle.data_rows(base)), 6)

    def test_contract_records_accepted_consumer(self):
        contract = puzzle.check(BUILD)
        consumer = contract['consumer']
        self.assertEqual(consumer['consumer'], 'com.project7.localmanager.LocalEventCatalog')
        self.assertEqual(consumer['class'], 'com.project7.localmanager.LocalPuzzleEngine$Room')
        self.assertEqual((consumer['bound'], consumer['required']), (4, 4))
        self.assertEqual(consumer['status'], 'accepted')
        self.assertEqual(consumer['clue_class'], 'com.project7.localmanager.LocalPuzzleEngine$Clue')
        self.assertEqual(consumer['clue_bound'], 4)

    def test_duplicate_rows_are_rejected(self):
        base = puzzle.BASE.read_bytes()
        extra = EXTRA.read_bytes() + puzzle.PUZZLE_ROOM.encode() + b'\n'
        with self.assertRaisesRegex(ValueError, 'duplicate extra row'):
            puzzle.merged_bytes(base, extra)

    def test_extra_row_duplicating_base_is_rejected(self):
        base = puzzle.BASE.read_bytes()
        extra = b'@puzzleClue\t1\t1\t0\n'
        base_rows = puzzle.directive_keys(puzzle.data_rows(base))
        with self.assertRaisesRegex(ValueError, 'duplicate base row'):
            puzzle.validate_extra(extra, base_rows)

    def test_missing_source_pin_is_rejected(self):
        base = puzzle.BASE.read_bytes().replace(
            puzzle.SOURCE_ROWS['trigger_3437'].encode() + b'\n', b'')
        with self.assertRaisesRegex(ValueError, 'fixed event_graph.tsv pin changed'):
            puzzle.merged_bytes(base, EXTRA.read_bytes())
        with self.assertRaisesRegex(ValueError, 'missing source pin trigger_3437'):
            puzzle.validate_base(base, pin=None)

    def test_virtual_camera_or_tip_drift_is_rejected(self):
        document = json.loads(puzzle.VIRTUAL.read_bytes())
        document['puzzle_room']['cameras'][0]['camera_id'] = 99
        with self.assertRaisesRegex(ValueError, 'virtual data pin changed'):
            puzzle.validate_virtual(json.dumps(document).encode())
        document = json.loads(puzzle.VIRTUAL.read_bytes())
        document['puzzle_room']['route']['tip']['row']['day'] = 6
        with self.assertRaisesRegex(ValueError, 'virtual data pin changed'):
            puzzle.validate_virtual(json.dumps(document).encode())


class PuzzleRoom4RuntimeTests(unittest.TestCase):
    def test_handler_path_exposes_clues_and_cameras(self):
        room = virtual.puzzle_room(4)
        self.assertEqual(room['room']['id'], 4)
        self.assertEqual(room['room']['row']['clear_event'], 3444)
        self.assertEqual(room['room']['row']['not_clear_event'], 3455)
        self.assertEqual([row['id'] for row in room['clues']], [17, 18, 19, 20, 21])
        self.assertEqual([row['id'] for row in room['cameras']], [9, 10, 11, 12, 13])
        self.assertEqual({row['id']: row['camera_name'] for row in room['clues']},
                         {17: 'jtwj_02', 18: 'jtwj_03', 19: 'jtwj_04', 20: 'jtwj_01', 21: 'jtwj_05'})

    def test_route_tip_is_the_pinned_27_2_day5_row(self):
        room = virtual.puzzle_room(4)
        tip = room['route']['tip']
        self.assertEqual(tip['key'], ['27-2', 5])
        self.assertEqual(tip['row'], {'route': '27-2', 'check_type': 1, 'check_paras': [3444], 'day': 5})


class PuzzleRoom4ConsumerTests(unittest.TestCase):
    @unittest.skipUnless((ROOT / 'toolchains/java/jdk-17.0.21+9/Contents/Home/bin/javac').is_file(),
                         'host toolchain unavailable')
    def test_original_consumer_accepts_room4_and_rejects_bounds(self):
        result = subprocess.run([sys.executable, str(DRIVER)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads((BUILD / 'host-result.json').read_text())
        self.assertEqual(report['status'], 'PASS')
        self.assertEqual(report['checks'], 55)
        self.assertIn('PASS 55 actual LocalEventCatalog checks', report['stdout'])
        self.assertIn('room4 success/clear/fail accepted', report['stdout'])
        self.assertIn('bounds/negatives preserved', report['stdout'])


if __name__ == '__main__':
    unittest.main()
