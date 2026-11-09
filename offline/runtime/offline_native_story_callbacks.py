# -*- coding: ascii -*-
"""Original area settlement callbacks carried by the stock UI queue.

Selective adaptation of Project7 client_event_compat.py lines 136-196:
source sha256 6b8a9210ee5cef40a785a63f9ba994afb7fb9280a759e23b975330a28e0722cd.
No event proof is produced here; the original cb resumes startMovie and the
existing story completion observer remains the sole offline completion bridge.
"""


class _F7StoryPanelContinuation(object):
    """Forward attrs/bound methods to the real Panel; own only continuation/cb.

    The four audited original bodies never pass bare self to native code,
    inspect its type, or call super/base methods. Native receiver identity stays
    with the actual Panel through its returned bound methods/widgets.
    """
    def __init__(self, panel, finish=None, callback_mode=False, callback=None):
        object.__setattr__(self, '_f7_panel', panel)
        object.__setattr__(self, '_f7_finish', finish)
        object.__setattr__(self, '_f7_callback_mode', callback_mode)
        object.__setattr__(self, '_f7_callback', callback)

    def __getattr__(self, name):
        if name == 'settlement_ended' and self._f7_finish is not None:
            return self._f7_finish
        if name == 'cb' and self._f7_callback_mode:
            return self._f7_callback
        return getattr(self._f7_panel, name)

    def __setattr__(self, name, value):
        if name == 'cb' and self._f7_callback_mode:
            object.__setattr__(self, '_f7_callback', value)
        else:
            setattr(self._f7_panel, name, value)


def _f7_area_source_matches(gg, source):
    avatar, proxy = source['avatar'], source['proxy']
    story = getattr(proxy, 'story', None)
    return (gg.avatar is avatar and getattr(avatar, 'server', None) is proxy and
            getattr(proxy, 'owner', None) is avatar and isinstance(story, dict) and
            story.get('week', 0) == source['week'] and
            story.get('event_occurrences', {}).get(str(source['event']), 0) == source['occurrence'] and
            source['event'] in getattr(proxy, 'processing_events', ()))


def install_native_story_callbacks():
    """Install once on the original Panel, preserving original terminal bodies."""
    import gg
    import com.const as const
    import com.data.cdata.event_content as content
    import cocos.panels.settlement_fullscreen as settlement
    panel_class = settlement.Panel
    if getattr(panel_class, '_f7_native_story_callbacks', False):
        return
    original_notify = panel_class.notify_area_event
    # Only these four audited bodies accept the forwarding continuation.
    # Python 2 class lookup returns a receiver-checking unbound method; use
    # its raw function here (Python 3 class lookup already returns a function).
    original_ended = getattr(panel_class.settlement_ended, 'im_func', panel_class.settlement_ended)

    def finish(panel, batch):
        source = batch['source']
        if (batch['ended'] or not panel.valid or
                getattr(panel, '_f7_story_area_batch', None) is not batch):
            return
        batch['ended'] = True
        # Keep the consumed identity on this destroyed instance. The stock
        # manager creates a NEW Panel for the next batch; old bare bound ends
        # must never re-enter destroy and evict that new cached Panel.

        def callback():
            if (batch['last'] and not source['delivered'] and source['callback'] is not None and
                    _f7_area_source_matches(gg, source)):
                source['delivered'] = True
                return source['callback']()
        # Never read or erase arbitrary panel.cb: a reward may have installed
        # its own callback while this managed area batch was displayed.
        return original_ended(_F7StoryPanelContinuation(panel, callback_mode=True, callback=callback))

    def notify_area_event(self, event, *areas, **kwargs):
        row = content.data.get(event, {})
        if tuple(row.get('ui', ())[:2]) != ('settlement_fullscreen', 'notify_area_event'):
            return original_notify(self, event, *areas, **kwargs)
        avatar = gg.avatar
        proxy = getattr(avatar, 'server', None)
        story = getattr(proxy, 'story', None)
        if not isinstance(story, dict):
            return
        source = {'avatar': avatar, 'proxy': proxy, 'event': event,
                  'week': story.get('week', 0),
                  'occurrence': story.get('event_occurrences', {}).get(str(event), 0),
                  'callback': kwargs.get('cb'), 'delivered': False}
        if not _f7_area_source_matches(gg, source):
            return
        opens, fights = [], []
        missing = False
        if not const.DEBUG_OFFLINE:
            for area in areas:
                area = int(area)
                info = avatar.cityData.get_area_info(area)
                if not isinstance(info, dict) or not isinstance(info.get('st'), (list, tuple)) or not info['st']:
                    missing = True
                    continue
                if info['st'][0] == const.CityStatus.FREE:
                    opens.append(area)
                else:
                    fights.append(area)
        suppressed = bool(fights) and (
            const.StoryRouteConst.ZHOUNIAN2_WEEK_REFRESH_EVENTID in avatar.eventTriggerData.completedEvents or
            avatar.storyData.change_week)
        if suppressed:
            fights = []
        if const.DEBUG_OFFLINE or missing:
            self._f7_story_area_diagnostic = 'unavailable-native-area-info'
            return
        batches = []
        if opens:
            if gg.ui.panels.battle_stage.valid:
                gg.ui.panels.battle_stage.visible_self_layer(False)
            batches.append(('notify_settlement_area_open', 'area_open', opens))
        if fights:
            batches.append(('notify_settlement_area_fight', 'area_fight', sorted(fights)))
        if not batches:
            if suppressed:
                # Original native rule deliberately suppresses known fights;
                # resume its own cb, without fabricating a panel terminal.
                self._f7_story_area_diagnostic = 'native-area-fights-suppressed'
                if source['callback'] is not None and _f7_area_source_matches(gg, source):
                    source['delivered'] = True
                    return source['callback']()
            self._f7_story_area_diagnostic = 'no-native-area-batch'
            return
        for index, (method, kind, values) in enumerate(batches):
            batch = {'source': source, 'last': index == len(batches) - 1, 'ended': False}
            gg.ui.add_settlement('settlement_fullscreen', method, kind, values, _f7_story_area_batch=batch)
        gg.ui.proc_settlement()

    def wrap_start(original):
        def start(self, stype, areas, **kwargs):
            batch = kwargs.pop('_f7_story_area_batch', None)
            if batch is None:
                return original(self, stype, areas, **kwargs)
            if batch['ended'] or not _f7_area_source_matches(gg, batch['source']):
                gg.ui.proc_settlement()
                return
            self._f7_story_area_batch = batch
            return original(self, stype, areas, **kwargs)
        return start

    def wrap_producer(original):
        def produce(self, *args, **kwargs):
            batch = getattr(self, '_f7_story_area_batch', None)
            if batch is None:
                return original(self, *args, **kwargs)
            if batch['ended']:
                return
            # An expired CURRENT panel still needs its original close/cleanup;
            # only its business continuation is refused in finish().
            # Original nested closures now capture this fixed batch, even after
            # original ended->proc_settlement starts the next batch reentrantly.
            continuation = _F7StoryPanelContinuation(self, finish=lambda: finish(self, batch))
            return original(continuation, *args, **kwargs)
        return produce

    def ended(self):
        if getattr(self, '_f7_story_area_batch', None) is not None:
            # Bare calls contain no batch identity. Only audited original
            # ending producers can authorize a managed area batch completion.
            return
        callback = self.cb
        self.cb = None
        return original_ended(_F7StoryPanelContinuation(self, callback_mode=True, callback=callback))

    panel_class.notify_area_event = notify_area_event
    for method in ('notify_settlement_area_open', 'notify_settlement_area_fight'):
        setattr(panel_class, method, wrap_start(getattr(panel_class, method)))
    for method in ('_close_panel', 'process_area_op_end', 'city_attention'):
        setattr(panel_class, method, wrap_producer(getattr(getattr(panel_class, method), 'im_func', getattr(panel_class, method))))
    panel_class.settlement_ended = ended
    panel_class._f7_native_story_callbacks = True
