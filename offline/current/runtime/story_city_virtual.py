# -*- coding: utf-8 -*-
"""Read-only story-city virtual data for the 7 COC scenes and puzzle room 4.

This is a runtime asset/service boundary, not an analysis-corpus dependency.
The JSON is a pinned copy of the reviewed extraction; callers get copies so
neither the source document nor another caller can be mutated.
"""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'project7_story_city_virtual' / 'virtual-data-v1.json'
CONTRACT = ROOT / 'project7_story_city_virtual' / 'contract-v1.json'
DATA_SHA256 = '83fae3199e308db88513f4a6e6bf6af2288ca749258e3d81b5c81451f8fec6de'
SCHEMA = 'project7-story-city-virtual-data-v1'
COC_SCENES = (482, 483, 484, 485, 486, 487, 488)
VIRTUAL_AREAS = (10000, 10001, 10002, 10003)


def _load():
    raw = DATA.read_bytes()
    if hashlib.sha256(raw).hexdigest() != DATA_SHA256:
        raise ValueError('story-city virtual data hash mismatch')
    value = json.loads(raw)
    if value.get('schema') != SCHEMA:
        raise ValueError('story-city virtual schema mismatch')
    if value.get('checks', {}).get('failed') != 0:
        raise ValueError('story-city virtual extraction has failed checks')
    return value


def planner():
    """Return the immutable virtual-area/scene plan and its seven COC missions."""
    value = _load()
    scope = value.get('scope') or {}
    if tuple(scope.get('scenes', ())) != COC_SCENES:
        raise ValueError('COC scene set changed')
    if tuple(scope.get('virtual_areas', ())) != VIRTUAL_AREAS:
        raise ValueError('virtual area set changed')
    missions = value.get('missions') or []
    if len(missions) != 7 or [int(row['key']) for row in missions] != list(COC_SCENES):
        raise ValueError('COC mission set changed')
    return copy.deepcopy({'scenes': COC_SCENES, 'virtual_areas': VIRTUAL_AREAS, 'missions': missions})


def puzzle_room(room_id=4):
    """Return puzzle room 4 with its five clue texts and five camera rows."""
    value = _load()
    puzzle = value.get('puzzle_room') or {}
    room = puzzle.get('room') or {}
    if room.get('id') != room_id:
        raise ValueError('puzzle room id changed')
    clues = puzzle.get('clues') or []
    if [row.get('id') for row in clues] != [17, 18, 19, 20, 21]:
        raise ValueError('puzzle clue set changed')
    for row in clues:
        if not (row.get('display_text') or row.get('clue_des')):
            raise ValueError('puzzle clue text missing')
    cameras = puzzle.get('cameras') or []
    if [row.get('id') for row in cameras] != [9, 10, 11, 12, 13]:
        raise ValueError('puzzle camera set changed')
    return copy.deepcopy(puzzle)


def clue_text(clue_id):
    for row in puzzle_room(4)['clues']:
        if row['id'] == clue_id:
            return row.get('display_text') or row['clue_des']
    raise KeyError(clue_id)
