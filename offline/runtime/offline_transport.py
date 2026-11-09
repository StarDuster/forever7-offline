# -*- coding: ascii -*-
"""Keep local asynchronous RPC dispatch alive across stock scene timer purges."""
import weakref


def acquire_ui_lock_lease(gg, key):
    """Claim one audited request's original named UI reference, not a new lock.

    The integration must prove lock immediately precedes dispatch, use the
    delivery helper for its consumers, and bind transport retries to one source.
    Original reset_lock replaces _lock: its dictionary identity is a generation.
    No lock/reset behavior or unscoped unlock is changed here.
    """
    ui = getattr(gg, 'ui', None)
    generation = getattr(ui, '_lock', None)
    if key is None or not isinstance(generation, dict):
        return ui, generation, None, False
    if not hasattr(ui, '_f7_rpc_original_unlock'):
        original_unlock = ui.unlock
        ui._f7_rpc_original_unlock = original_unlock
        ui._f7_rpc_active_deliveries = []
        def tracked_unlock(key='default', show_panel=True):
            active = ui._f7_rpc_active_deliveries
            lease = active[-1] if active else None
            if lease is not None and lease['key'] == key:
                if lease['released']:
                    return
                lease['released'] = True
                if getattr(ui, '_lock', None) is not lease['generation']:
                    return
            return original_unlock(key, show_panel)
        ui.unlock = tracked_unlock
    leases = [lease for lease in getattr(ui, '_f7_rpc_lock_leases', [])
              if not lease['released'] and lease['generation'] is generation]
    ui._f7_rpc_lock_leases = leases
    reserved = sum(lease['key'] == key for lease in leases)
    if generation.get(key, 0) == reserved + 1:
        lease = {'ui': ui, 'generation': generation, 'key': key,
                 'released': False, 'delivering': False}
        leases.append(lease)
        return ui, generation, lease, True
    return ui, generation, None, True


def ui_lock_lease_state(gg, source):
    if source.get('lock_tracking'):
        if (getattr(gg, 'ui', None) is not source['ui'] or
                getattr(source['ui'], '_lock', None) is not source['lock_generation']):
            return 'lock-generation'
        lease = source['lock_lease']
        if lease is None:
            return 'unowned-lock'
        if lease['released']:
            return 'completed'
        if lease['delivering']:
            return 'delivering'
    return None


def complete_ui_lock_lease(gg, source, after_reply=False):
    """Complete this exact reference once, fencing both UI and reset generation."""
    lease = source.get('lock_lease')
    if lease is None or lease['released']:
        return
    lease['released'] = True
    ui, generation, key = lease['ui'], lease['generation'], lease['key']
    if getattr(gg, 'ui', None) is not ui or getattr(ui, '_lock', None) is not generation:
        return
    remaining = sum(not other['released'] and other['generation'] is generation and other['key'] == key
                    for other in getattr(ui, '_f7_rpc_lock_leases', []))
    # Original consumers normally unlock. If decoding/consumption failed,
    # reclaim only the surplus reference, keeping reentrant requests reserved.
    if generation.get(key, 0) > (remaining if after_reply else 0):
        ui._f7_rpc_original_unlock(key)


def deliver_ui_lock_reply(gg, source, emit):
    """Run one original consumer under its lease; always finish its reference.

    Owner, route, period, frame and business success checks belong to the caller.
    A completed/delivering/obsolete lease never runs a second business consumer.
    """
    if ui_lock_lease_state(gg, source) is not None:
        return False
    lease = source.get('lock_lease')
    if source.get('lock_tracking'):
        lease['delivering'] = True
        lease['ui']._f7_rpc_active_deliveries.append(lease)
    try:
        emit()
        return True
    finally:
        if lease is not None and lease['delivering']:
            lease['ui']._f7_rpc_active_deliveries.pop()
            lease['delivering'] = False
        complete_ui_lock_lease(gg, source, after_reply=True)


class LocalRpcScheduler(object):
    def __init__(self, gg):
        self.gg = gg
        self.pending = {}
        self.sequence = 0
        self.closed = False

    def schedule(self, delay, callback):
        if self.closed:
            return
        self.sequence += 1
        key = self.sequence
        order = getattr(self.gg, '_f7_rpc_dispatch_sequence', 0) + 1
        self.gg._f7_rpc_dispatch_sequence = order
        self.pending[key] = {'delay': delay, 'callback': callback, 'generation': 0, 'order': order}
        self.arm(key)

    def arm(self, key):
        entry = self.pending[key]
        entry['generation'] += 1
        generation = entry['generation']

        def dispatch():
            current = self.pending.get(key)
            if self.closed or current is None or current['generation'] != generation:
                return
            # Remove before entering game/client code: a nested purge must not
            # replay an operation which already acknowledged or committed.
            self.pending.pop(key)
            return current['callback']()
        self.gg.exec_delay(entry['delay'], dispatch)

    def rearm(self):
        if not self.closed:
            for key in sorted(self.pending):
                self.arm(key)

    def close(self):
        self.closed = True
        self.pending.clear()


def install_local_purge_recovery(gg):
    if not hasattr(gg, '_f7_local_rpc_schedulers'):
        gg._f7_local_rpc_schedulers = []
    if getattr(gg, '_f7_local_purge_recovery', False):
        return
    original = getattr(gg, 'exec_cancel_all', None)
    if original is None:
        return

    def cancel_with_recovery(*args, **kwargs):
        result = original(*args, **kwargs)
        alive, pending = [], []
        for reference in gg._f7_local_rpc_schedulers:
            scheduler = reference()
            if scheduler is not None and not scheduler.closed:
                alive.append(reference)
                pending.extend((entry['order'], scheduler, key)
                               for key, entry in scheduler.pending.items())
        for order, scheduler, key in sorted(pending, key=lambda item: item[0]):
            scheduler.arm(key)
        gg._f7_local_rpc_schedulers = alive
        probe_rearm = getattr(gg, '_f7_probe_rearm', None)
        if probe_rearm is not None:
            probe_rearm()
        return result
    gg.exec_cancel_all = cancel_with_recovery
    gg._f7_local_purge_recovery = True


def schedule_local_rpc(proxy, gg, delay, callback):
    install_local_purge_recovery(gg)
    scheduler = getattr(proxy, '_rpc_scheduler', None)
    if scheduler is None or scheduler.closed:
        scheduler = LocalRpcScheduler(gg)
        proxy._rpc_scheduler = scheduler
        gg._f7_local_rpc_schedulers.append(weakref.ref(scheduler))
    scheduler.schedule(delay, callback)


class AuthorizedEventStartDelivery(object):
    """One already-authorized event occurrence, gated by original client readiness.

    No story state is changed. Acceptance is the original client's processing
    membership AFTER its handler ran, never merely sending the RPC.
    """
    def __init__(self, schedule, current, ready, accepted, emit, finish):
        self.schedule = schedule
        self.current = current
        self.ready = ready
        self.accepted = accepted
        self.emit = emit
        self.finish = finish
        self.closed = False
        self.scheduled = False
        self.emitted = False

    def close(self):
        self.closed = True

    def attempt(self):
        if self.closed:
            return
        self.scheduled = False
        if not self.current():
            self.closed = True
            self.finish(False)
            return
        if self.accepted():
            self.closed = True
            self.finish(True)
            return
        if self.ready():
            self.emitted = True
            self.emit()
            self.closed = True
            # Never use the original handler/queryEventOptAsk as a probe. If it
            # did not accept, retire and allow only a later explicit start RPC.
            self.finish(bool(self.current() and self.accepted()))
            return
        if not self.closed and not self.scheduled:
            self.scheduled = True
            self.schedule(100,self.attempt)
