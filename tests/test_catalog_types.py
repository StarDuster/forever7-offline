from pathlib import Path
import sys
import json
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from export_game_catalogs import encode, decode


class CatalogTypesTests(unittest.TestCase):
    def test_round_trip_keeps_tuple_keys_and_distinguishes_integer_and_string_ids(self):
        original = {1: {'id': 1}, '1': {'id': '1'}, (1064, 3): {'attrs': {7: 2.5}, 'parts': (1, 2)}}
        self.assertEqual(decode(json.loads(json.dumps(encode(original)))), original)

    def test_empty_types_and_reserved_tag_in_real_data_are_preserved(self):
        original = {'tuple': (), 'list': [], 'set': set(), 'frozenset': frozenset(),
                    'dict': {}, 'literal': {'$f7type': 'a game field', 'items': [1]}}
        restored = decode(json.loads(json.dumps(encode(original))))
        self.assertEqual(restored, original)
        for key in original:
            self.assertIs(type(restored[key]), type(original[key]))


if __name__ == '__main__':
    unittest.main()
