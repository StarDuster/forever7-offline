# -*- coding: ascii -*-
"""Offline ACTIONAFTEREVENT (condition code 20) committed-action ledger.

Explicit offline policy, not original-server proof.  The original client has no
actionAfterEvent producer (reports/condition-codes-20-45-46-31-49.md).  This
module is the sole offline fact owner for code 20:

* A charge is counted only after the host accepted the action transaction and
  the whole progress document (effects + ledger) is persisted atomically.
  The Python offline host records the observed decrease of story.city_values.av
  because it has no exact action-cost argument; this net-av approximation is a
  host limitation, not a Java contract.  The manager Store/Engine must record
  the exact committed cost and receipt id instead (see
  reports/code20-java-transaction-evidence.md).  Neither owner invents one
  action per RPC.
* Failed actions and failed saves never reach this module.  Retries and
  duplicate settlements leave av unchanged, so their observed delta is zero.
  Optional stable receipt ids are persisted (bounded) and de-duplicated.
* A real event completion stores {week, spent, generation} from the current
  ledger.  "Actions since the event" is spent - baseline only for the current
  ledger generation, and only when it is non-negative.
* A missing, malformed or foreign ledger never yields a number.  Legacy saves
  without a ledger fall back to week_actions_spent/event_action_baselines only
  when event_days proves the completion week is the current week.  No zero or
  success is synthesized for an old save.
* Ordering policy (explicit local policy; original server order unknown): events
  are selected/evaluated during transaction preparation, before that same
  transaction's action value is charged and persisted.  A patrol therefore
  cannot satisfy its own code20 threshold; the next accepted transaction sees
  the committed charge.  Only ordinary story.city_values.av decreases count.
  Flashback and dream admissions use separate budgets and are excluded even
  though they are real actions, because they consume no ordinary action value.
  A net decrease is recorded; no same-transaction refund path is proven, and a
  refund would undercount rather than fabricate a pass.
* A real week transition by the week owner preserves the observed spend,
  advances the generation, and drops baselines/receipts from the old
  generation; prior-generation facts become unknown, never stale numbers.
"""

ACTION_LEDGER_POLICY = 'offline-committed-action-spend-after-event-v1'
ACTION_LEDGER_INVALID_POLICY = 'offline-committed-action-spend-after-event-invalidated-v1'
ACTION_LEDGER_VERSION = 1
_AL_MAX_BASELINES = 4096
_AL_MAX_RECEIPTS = 64
_AL_MAX_ID = 128

try:
    _AL_TEXT = (basestring,)
    _AL_INTS = (int, long)
except NameError:
    _AL_TEXT = (str,)
    _AL_INTS = (int,)

_AL_ABSENT = object()


def _al_integer(value):
    return isinstance(value, _AL_INTS) and not isinstance(value, bool)


def _al_event_key(event):
    if _al_integer(event) and event >= 0:
        return str(event)
    if isinstance(event, _AL_TEXT) and event:
        text = str(event)
        if text.isdigit() and str(int(text)) == text:
            return text
    raise ValueError('Invalid original event identity for the action ledger')


def _al_lookup(mapping, key, absent=_AL_ABSENT):
    if not isinstance(mapping, dict):
        return absent
    return mapping.get(key, mapping.get(str(key), absent))


def initial_action_ledger():
    return {'version': ACTION_LEDGER_VERSION, 'policy': ACTION_LEDGER_POLICY,
            'generation': 1, 'spent': 0, 'baselines': {}, 'receipts': []}


def validate_action_ledger(ledger):
    """Raise ValueError unless the ledger is exactly usable.

    Unknown extra fields are tolerated so a future additive field does not
    invalidate committed history, but every field read here is checked.
    """
    if not isinstance(ledger, dict):
        raise ValueError('Invalid action ledger document')
    if ledger.get('version') != ACTION_LEDGER_VERSION:
        raise ValueError('Unsupported action ledger version')
    if ledger.get('policy') != ACTION_LEDGER_POLICY:
        raise ValueError('Unsupported action ledger policy')
    generation = ledger.get('generation')
    spent = ledger.get('spent')
    if not _al_integer(generation) or generation < 1:
        raise ValueError('Invalid action ledger generation')
    if not _al_integer(spent) or spent < 0:
        raise ValueError('Invalid action ledger spend')
    baselines = ledger.get('baselines')
    if not isinstance(baselines, dict) or len(baselines) > _AL_MAX_BASELINES:
        raise ValueError('Invalid action ledger baselines')
    for key, baseline in baselines.items():
        _al_event_key(key)
        if not isinstance(baseline, dict):
            raise ValueError('Invalid action ledger baseline')
        week, base = baseline.get('week'), baseline.get('spent')
        if (not _al_integer(week) or week < 0 or not _al_integer(base) or
                base < 0 or base > spent):
            raise ValueError('Invalid action ledger baseline')
        if baseline.get('generation') != generation:
            raise ValueError('Stale action ledger baseline generation')
    receipts = ledger.get('receipts')
    if not isinstance(receipts, list) or len(receipts) > _AL_MAX_RECEIPTS:
        raise ValueError('Invalid action ledger receipts')
    seen = set()
    for receipt in receipts:
        if not isinstance(receipt, dict):
            raise ValueError('Invalid action ledger receipt')
        identity = receipt.get('id')
        amount = receipt.get('spent')
        total = receipt.get('total')
        if (not isinstance(identity, _AL_TEXT) or not identity or
                len(identity) > _AL_MAX_ID or identity in seen or
                not _al_integer(amount) or amount < 1 or
                not _al_integer(total) or total < amount or total > spent):
            raise ValueError('Invalid action ledger receipt')
        seen.add(identity)
    return True


def read_action_ledger(state):
    """Return a valid ledger, or None when absent or unusable.

    An invalid document is never repaired or overwritten by a read.  Callers
    must treat None as unsupported, not as zero.
    """
    story = state.get('story') if isinstance(state, dict) else None
    if not isinstance(story, dict):
        return None
    ledger = story.get('action_ledger')
    if ledger is None:
        return None
    try:
        validate_action_ledger(ledger)
    except ValueError:
        return None
    return ledger


def _al_story(state):
    story = state.get('story') if isinstance(state, dict) else None
    if not isinstance(story, dict):
        raise ValueError('Action ledger requires a story document')
    return story


def _al_current_ledger(story, create):
    ledger = story.get('action_ledger')
    if ledger is None:
        if not create:
            return None
        ledger = initial_action_ledger()
        story['action_ledger'] = ledger
        return ledger
    validate_action_ledger(ledger)
    return ledger


def record_committed_spend(state, amount, receipt_id=None):
    """Count one accepted, persisted action charge.

    Returns True when the ledger grew, False for a duplicate receipt id, and
    None when an existing ledger is invalid (code 20 stays unsupported).
    Invalid arguments raise ValueError; the host never passes negative or
    non-integer deltas.
    """
    if not _al_integer(amount) or amount < 0:
        raise ValueError('Action ledger amount must be a non-negative integer')
    if receipt_id is not None:
        if (not isinstance(receipt_id, _AL_TEXT) or not receipt_id or
                len(receipt_id) > _AL_MAX_ID):
            raise ValueError('Invalid action ledger receipt identity')
    story = _al_story(state)
    try:
        ledger = _al_current_ledger(story, True)
    except ValueError:
        return None
    if receipt_id is not None:
        for receipt in ledger['receipts']:
            if receipt['id'] == receipt_id:
                if receipt['spent'] != amount:
                    raise ValueError('Action ledger receipt reused with a different charge')
                return False
    if amount == 0:
        return False
    ledger['spent'] += amount
    if receipt_id is not None:
        ledger['receipts'].append({'id': receipt_id, 'spent': amount,
                                   'total': ledger['spent']})
        ledger['receipts'] = ledger['receipts'][-_AL_MAX_RECEIPTS:]
    return True


def set_event_baseline(state, event, week=None):
    """Store the committed spend baseline of a real event completion.

    Returns False instead of raising when an existing ledger is invalid, so a
    corrupt optional ledger cannot block a real event completion; code 20 then
    stays unsupported.
    """
    key = _al_event_key(event)
    story = _al_story(state)
    if week is None:
        week = story.get('week', 0)
    if not _al_integer(week) or week < 0:
        raise ValueError('Action baseline requires an explicit week')
    try:
        ledger = _al_current_ledger(story, True)
    except ValueError:
        return False
    ledger['baselines'][key] = {'week': week, 'spent': ledger['spent'],
                                'generation': ledger['generation']}
    return True


def invalidate_action_ledger(story):
    """Replace an untrustworthy ledger with an explicit unsupported sentinel.

    Used when a stable receipt identity conflicts with its recorded charge: the
    sequence can no longer be proven complete, so no code20 number may be
    returned.  The document is never repaired implicitly.
    """
    if not isinstance(story, dict):
        raise ValueError('Action ledger requires a story document')
    story['action_ledger'] = {'version': ACTION_LEDGER_VERSION,
                              'policy': ACTION_LEDGER_INVALID_POLICY,
                              'generation': 1, 'spent': 0,
                              'baselines': {}, 'receipts': []}
    return story['action_ledger']


def next_week_action_ledger(ledger):
    """Carry observed committed spend into a new week generation.

    The real week owner rebuilds story state and resets the action budget, so
    baselines from the previous generation cannot be used.  Spend stays
    monotonic; generation advances; baselines and bounded receipt ids reset.
    An absent or invalid ledger stays unsupported (None), never a fresh zero
    with old baselines.
    """
    if ledger is None:
        return None
    try:
        validate_action_ledger(ledger)
    except ValueError:
        return None
    return {'version': ACTION_LEDGER_VERSION, 'policy': ACTION_LEDGER_POLICY,
            'generation': ledger['generation'] + 1, 'spent': ledger['spent'],
            'baselines': {}, 'receipts': []}


def _al_ledger_value(ledger, event):
    baseline = _al_lookup(ledger['baselines'], event)
    if baseline is _AL_ABSENT:
        return _AL_ABSENT
    if (not isinstance(baseline, dict) or
            baseline.get('generation') != ledger['generation']):
        return None
    base = baseline.get('spent')
    if not _al_integer(base) or base < 0 or base > ledger['spent']:
        return None
    return ledger['spent'] - base


def _al_legacy_value(state, event):
    story = state.get('story') if isinstance(state, dict) else None
    if not isinstance(story, dict):
        return None
    spent = story.get('week_actions_spent')
    week = story.get('week')
    if not _al_integer(spent) or spent < 1 or not _al_integer(week) or week < 0:
        # A legacy save whose counter is absent was defaulted to zero by the
        # host; an exact zero cannot be distinguished from that default, so it
        # is unknown rather than a synthesized "no actions".
        return None
    baseline = _al_lookup(story.get('event_action_baselines'), event)
    if not _al_integer(baseline) or baseline < 0 or baseline > spent:
        return None
    stamp = _al_lookup(story.get('event_days'), event)
    if (not isinstance(stamp, dict) or not _al_integer(stamp.get('week')) or
            stamp.get('week') != week):
        return None
    return spent - baseline


def action_spent_since_event(state, event):
    """Committed action charge since the event completion, or None.

    None means the fact is unsupported/unknown: no completed baseline, an
    old save without a baseline, a different week, or an invalid ledger.
    """
    _al_event_key(event)
    story = state.get('story') if isinstance(state, dict) else None
    if not isinstance(story, dict) or 'action_ledger' not in story:
        return _al_legacy_value(state, event)
    try:
        validate_action_ledger(story['action_ledger'])
    except ValueError:
        return None
    value = _al_ledger_value(story['action_ledger'], event)
    if value is not _AL_ABSENT:
        return value
    # A ledger created after this event has no baseline for it.  A same-week
    # legacy baseline was still written at a real completion; use it instead
    # of turning a previously supported event into unknown.
    return _al_legacy_value(state, event)


def code20_condition_values(state, required, completed_events):
    """Return {event: int|None} for exactly the completed required events.

    Events that are not completed stay absent from the map, which the original
    dict predicate treats as a known false row.
    """
    completed = set()
    for event in completed_events or ():
        try:
            completed.add(_al_event_key(event))
        except ValueError:
            continue
    values = {}
    for event in required:
        try:
            key = _al_event_key(event)
        except ValueError:
            values[event] = None
            continue
        if key not in completed:
            continue
        values[event] = action_spent_since_event(state, event)
    return values
