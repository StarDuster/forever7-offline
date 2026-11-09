import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
import story_city_virtual as virtual


class StoryCityVirtualTests(unittest.TestCase):
    def test_planner_is_exactly_seven_coc_scenes(self):
        plan = virtual.planner()
        self.assertEqual(plan['scenes'], (482, 483, 484, 485, 486, 487, 488))
        self.assertEqual(plan['virtual_areas'], (10000, 10001, 10002, 10003))
        self.assertEqual(len(plan['missions']), 7)

    def test_puzzle_room_4_has_text_and_cameras(self):
        puzzle = virtual.puzzle_room(4)
        self.assertEqual([row['id'] for row in puzzle['clues']], [17, 18, 19, 20, 21])
        self.assertEqual([row['id'] for row in puzzle['cameras']], [9, 10, 11, 12, 13])
        for clue in puzzle['clues']:
            self.assertTrue(virtual.clue_text(clue['id']))
        self.assertEqual(puzzle['wire']['protocol'], 'puzzleRoomGetClue')
        self.assertEqual(puzzle['wire']['clue_ids'], [17, 18, 19, 20, 21])

    def test_callers_cannot_mutate_the_source(self):
        puzzle = virtual.puzzle_room(4)
        puzzle['clues'][0]['clue_des'] = 'mutated'
        self.assertNotEqual(virtual.clue_text(17), 'mutated')


if __name__ == '__main__':
    unittest.main()
