# -*- coding: ascii -*-
"""Narrow P7 startup policy. Python 2.7 source; no replacement backend."""
import sys
import os
import json
import tempfile
import time
import types


_REPAIR_CODES = frozenset((
    'resource_verify_failed', 'unverified_activation', 'resource_activation_failed',
    'resource_query_failed', 'resource_query_exception', 'resource_download_failed',
    'inactive_game_start', 'startup_policy_install_failed'))
_REPAIR_BYTES = 256

# Bootstrap receipt budget. Injectable so contract tests use a short fake
# clock instead of waiting the production window out.
_BOOTSTRAP_WINDOW_S = 30.0
_BOOTSTRAP_TIMEOUT_S = 1.5
_BOOTSTRAP_RETRY_SLEEP_S = 0.5
_BOOTSTRAP_CLOCK = time.time
_BOOTSTRAP_SLEEP = time.sleep


def _capture_repair_launch(patch):
    # Capture once for this actual Python engine, never reread a newer generation.
    try:
        locate = _globals(patch._q7_verify_offline_resources).get('_q7_snapshot_path')
        if not callable(locate):
            return None
        directory = os.path.dirname(locate())
        with open(os.path.join(directory, '.p7-launch.json'), 'rb') as stream:
            raw = stream.read(_REPAIR_BYTES + 1)
        if len(raw) != _REPAIR_BYTES:
            return None
        state = json.loads(raw.decode('ascii'))
        generation = state.get('generation')
        if (set(state) != set(('generation', 'schema')) or
                type(state['schema']) is not int or state['schema'] != 1 or
                not isinstance(generation, type(u'')) or len(generation) != 32 or
                any(c not in '0123456789abcdef' for c in generation)):
            return None
        return (directory, generation)
    except Exception:
        return None


def _notify_repair(launch, code):
    # Notification failure never replaces the original startup failure/result.
    if launch is None or code not in _REPAIR_CODES:
        return
    temporary = None
    try:
        directory, generation = launch
        payload = json.dumps({'schema': 1, 'generation': generation, 'code': code},
            sort_keys=True, separators=(',', ':')).encode('ascii')
        if len(payload) > _REPAIR_BYTES:
            return
        descriptor, temporary = tempfile.mkstemp(prefix='.p7-repair-request.tmp-', dir=directory)
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(payload + b' ' * (_REPAIR_BYTES - len(payload)))
            stream.flush()
            os.fsync(stream.fileno())
        os.rename(temporary, os.path.join(directory, '.p7-repair-request.json'))
        temporary = None
    except Exception:
        pass
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except Exception:
                pass


def _raw(function):
    return getattr(function, 'im_func', getattr(function, '__func__', function))


def _globals(function):
    function = _raw(function)
    return getattr(function, 'func_globals', getattr(function, '__globals__', {}))


def _freeze(value):
    if isinstance(value, dict):
        return ('dict', tuple((_freeze(k), _freeze(v)) for k, v in value.items()))
    if isinstance(value, list):
        return ('list', tuple(_freeze(v) for v in value))
    if isinstance(value, tuple):
        return ('tuple', tuple(_freeze(v) for v in value))
    if value is None or isinstance(value, (str, int, float, bool)):
        return ('scalar', value)
    try:
        if isinstance(value, (unicode, long)):
            return ('scalar', value)
    except NameError:
        pass
    raise ValueError('Unsupported resource metadata type')


def _thaw(value):
    kind, data = value
    if kind == 'scalar':
        return data
    if kind == 'dict':
        return dict((_thaw(k), _thaw(v)) for k, v in data)
    if kind == 'tuple':
        return tuple(_thaw(v) for v in data)
    return [_thaw(v) for v in data]


def install_offline_hotfix_guard(patch):
    """Skip the official hotfix download in offline mode.

    The packaged local resources are authoritative. This is an explicit offline
    skip, not a claimed successful remote update; the original hotfix pipeline
    is left untouched for non-P7/offline callers.
    """
    hotfix = getattr(patch, 'patch_hotfix', None)
    if hotfix is None:
        return False

    def skip_download(callback):
        # Original step_hotfix waits until this callback populates ret.
        # Empty content means "no remote hotfix", not a successful download;
        # before_hotfix is intentionally not called.
        callback('')
        return None

    hotfix.download_hotfix = skip_download
    return True


def _panel_method(member, method_name):
    """Resolve both public and Python private-name-mangled panel methods."""
    candidates = [method_name]
    if method_name.startswith('__') and not method_name.endswith('__'):
        candidates.append('_' + member.__name__ + method_name)
    for candidate in candidates:
        value = getattr(member, candidate, None)
        if value is not None:
            return candidate, value
    return None, None


def install_panel_delay_guard(module, method_names):
    """Guard delayed callbacks inside named panel methods after panel destruction.

    Installation succeeds only when every requested method resolves and is
    wrapped with this module's exact wrapper. Existing foreign overrides are a
    hard failure, never a silent skip.
    """
    member = getattr(module, 'Panel', getattr(module, 'Member', None))
    if member is None:
        return False
    found = 0
    for method_name in method_names:
        actual_name, current = _panel_method(member, method_name)
        if actual_name is None:
            continue
        marker = '_q7_original_' + actual_name
        wrapped_marker = '_q7_wrapped_' + actual_name
        existing_original = getattr(member, marker, None)
        existing_wrapper = getattr(member, wrapped_marker, None)
        if existing_original is not None:
            # On Python 2, class attribute reads create new unbound-method
            # descriptors; compare the underlying functions, not descriptors.
            if existing_wrapper is None or _raw(current) is not _raw(existing_wrapper):
                return False
            found += 1
            continue
        original = _raw(current)
        if original is None:
            continue

        def make_wrapper(original):
            def wrapper(self, *args, **kwargs):
                import gg
                schedule = gg.exec_delay
                panel = self
                panel_node = getattr(panel, '_node', None)
                if panel_node is None:
                    return original(self, *args, **kwargs)

                def guarded_schedule(delay, callback):
                    def guarded_callback():
                        if (not getattr(panel, 'valid', False) or
                                getattr(panel, '_node', None) is not panel_node):
                            return
                        callback()
                    return schedule(delay, guarded_callback)

                namespace = dict(_globals(original))
                old_gg = namespace.get('gg')
                base_gg = old_gg if old_gg is not None else gg
                class _GGProxy(object):
                    def __init__(self, base, delay):
                        self._base = base
                        self.exec_delay = delay
                    def __getattr__(self, name):
                        return getattr(self._base, name)
                namespace['gg'] = _GGProxy(base_gg, guarded_schedule)
                code = getattr(original, 'func_code', getattr(original, '__code__', None))
                defaults = getattr(original, 'func_defaults', getattr(original, '__defaults__', None))
                closure = getattr(original, 'func_closure', getattr(original, '__closure__', None))
                cloned = types.FunctionType(code, namespace, original.__name__, defaults, closure)
                return cloned(self, *args, **kwargs)
            return wrapper

        wrapper = make_wrapper(original)
        setattr(member, marker, original)
        setattr(member, wrapped_marker, wrapper)
        setattr(member, actual_name, wrapper)
        found += 1
    return found == len(method_names)


def install_high_fps():
    """Expose the 60fps switch without changing the default rate.

    The client only shows the switch when the device is in the quality table,
    so an unlisted phone had no way to enable it. Keep the stored rate as is;
    the player decides in settings.
    """
    try:
        import com.const as const
    except Exception:
        return False
    try:
        const.ANDROID_HAS_HIGHFPS = True
    except Exception:
        return False
    return True


def install_nickname_review():
    """Accept every nickname offline (the engine review answers "" there)."""
    try:
        import game3d
    except Exception:
        return False
    if getattr(game3d, '_f7_nickname_review', None):
        return True

    def accept(*args, **kwargs):
        return json.dumps({'code': 0, 'message': 'ok', 'regularId': '-1'})

    for name in ('env_review_nickname', 'envmanager_review_nickname'):
        try:
            setattr(game3d, name, accept)
        except Exception:
            return False
    setattr(game3d, '_f7_nickname_review', True)
    return True


def install_valentine_letters():
    """Fill the white-valentine hero list offline.

    The activity asks the server for `can_heroes`; the local manager never
    answers, so the replica-letter picker showed 0 heroes. Rebuild the list
    from the letter table (heroes holding a 2018/2019 letter), which is what the
    activity's own rule text describes.
    """
    try:
        import com.data.cdata.letter_data as LETTER_DATA
        import entity.avatar_attrs.ActivityDatas.WhiteValentineData as module
    except Exception:
        return False
    cls = getattr(module, 'WhiteValentineData', None)
    if cls is None:
        return False
    marker = '_f7_valentine_letters'
    if getattr(cls, marker, None) is not None:
        return True
    original = _raw(getattr(cls, 'initFromDict', None))
    if not isinstance(original, types.FunctionType):
        return False

    def eligible():
        ids = set()
        try:
            table = LETTER_DATA.data
        except Exception:
            return []
        for row in table.values():
            if not isinstance(row, dict):
                continue
            hero = row.get('hero') or 0
            name = row.get('name') or u''
            if hero and (name.startswith(u'\u60c5\u4e662018') or
                         name.startswith(u'\u60c5\u4e662019')):
                ids.add(int(hero))
        return sorted(ids)

    def initFromDict(self, data):
        result = original(self, data)
        try:
            if not getattr(self, 'can_heroes', None):
                self.can_heroes = eligible()
        except Exception:
            pass
        return result

    initFromDict._f7_valentine = True
    cls.initFromDict = initFromDict
    setattr(cls, marker, True)
    return True


def install_wardrobe_lifecycle_guard(module):
    return install_panel_delay_guard(module, ('refresh_pendant',))



def install_event_trigger_inflight(member, rpc_method, avatar=None):
    """Coalesce only duplicate outbound startEvent sends.

    The original 640 ``startEventReply`` stays the sole typed reply consumer.
    The guard keeps a pending token per Avatar/event and releases it from the
    actual reliable callback for that send (or an explicit login reset). It does
    not gate replies, edit event queues, inspect pull snapshots, or special-case
    an event id.
    """
    owner = getattr(member, '_q7_event_inflight_owner', None)
    if owner is not None:
        if avatar is not None:
            for name in ('startEvent', 'eventOnLogin'):
                current = _raw(getattr(avatar, name, None))
                patched = _raw(getattr(member, name, None))
                if current is not patched:
                    setattr(avatar, name, getattr(member, '__dict__', {}).get(name, getattr(member, name)))
        return owner
    original_start = _raw(getattr(member, 'startEvent', None))
    original_login = _raw(getattr(member, 'eventOnLogin', None))
    if not callable(original_start):
        raise RuntimeError('Event trigger original startEvent missing')
    if not callable(original_login) or not hasattr(original_login, 'rpcmethod'):
        raise RuntimeError('Event trigger original eventOnLogin missing')
    owner = object()
    state_name = '_q7_event_inflight_state'
    def state(avatar):
        value = getattr(avatar, state_name, None)
        if value is None:
            value = {'pending': {}}
            setattr(avatar, state_name, value)
        return value
    def start(avatar, event):
        data = getattr(avatar, 'eventTriggerData', None)
        if data is None:
            return original_start(avatar, event)
        pending = state(avatar)['pending']
        if event in pending or event in getattr(data, 'processingEventsClient', ()):
            return False
        cache = getattr(avatar, 'reliableRpcCache', None)
        if cache is not None and len(cache) >= 100:
            return False
        checker = getattr(avatar, 'canStartEvent', None)
        if not callable(checker) or not checker(event):
            return original_start(avatar, event)
        token = object()
        pending[event] = token
        available = getattr(data, 'availableEvents', None)
        saved = available.get(event) if isinstance(available, dict) else None
        had_available = isinstance(available, dict) and event in available
        reliable = getattr(avatar, 'callServerMethodReliable', None)
        previous = getattr(avatar, '__dict__', {}).get('callServerMethodReliable', None)
        had_previous = 'callServerMethodReliable' in getattr(avatar, '__dict__', {})
        if callable(reliable):
            def guarded(method, parameters, callback=None, needresult=False):
                original_callback = callback
                if original_callback is not None:
                    def safe_callback(*args, **kwargs):
                        try:
                            return original_callback(*args, **kwargs)
                        finally:
                            if pending.get(event) is token:
                                pending.pop(event, None)
                    callback = safe_callback
                return reliable(method, parameters, callback=callback, needresult=needresult)
            setattr(avatar, 'callServerMethodReliable', guarded)
        try:
            result = original_start(avatar, event)
        except Exception:
            if pending.get(event) is token:
                pending.pop(event, None)
            if had_available and isinstance(available, dict) and event not in available:
                available[event] = saved
            try:
                import gg as _gg
                _gg.ui.unlock('startEvent')
            except Exception:
                pass
            raise
        finally:
            if callable(reliable):
                if had_previous:
                    setattr(avatar, 'callServerMethodReliable', previous)
                else:
                    try:
                        delattr(avatar, 'callServerMethodReliable')
                    except Exception:
                        pass
        if not result and pending.get(event) is token:
            pending.pop(event, None)
        return result
    def login(avatar, data):
        try:
            return original_login.rpcmethod.func(avatar, data)
        finally:
            state(avatar)['pending'].clear()
    def wrap_rpc(original, body):
        metadata = original.rpcmethod
        wrapped = rpc_method(metadata.rpctype, metadata.argtypes, metadata.pub)(body)
        wrapped.__name__ = original.__name__
        wrapped._q7_event_inflight_owner = owner
        return wrapped
    member.startEvent = start
    member.eventOnLogin = wrap_rpc(original_login, login)
    _raw(member.startEvent)._q7_event_inflight_owner = owner
    member._q7_event_inflight_owner = owner
    if avatar is not None:
        for name in ('startEvent', 'eventOnLogin'):
            current = _raw(getattr(avatar, name, None))
            patched = _raw(getattr(member, name, None))
            if current is patched:
                continue
            setattr(avatar, name, getattr(member, '__dict__', {}).get(name, getattr(member, name)))
    game_object = sys.modules.get('com.base.game_object')
    cache = getattr(game_object, 'members_cache', None)
    if isinstance(cache, dict) and member in cache:
        import inspect
        cache[member] = inspect.getmembers(member)
    return owner


class _PortraitImageProxy(object):
    """Display-only fallback for non-public hero cards with absent/blank art."""
    def __init__(self, original, hero_id):
        self._original = original
        self._hero_id = hero_id

    def _available(self, path):
        try:
            import C_file
            if not C_file.find_res_file(path, ''):
                return False
            try:
                desc = C_file.get_res_file_desc(path)
                if desc and len(desc) >= 2 and int(desc[1]) < 512:
                    return False
            except Exception:
                pass
            return True
        except Exception:
            return True

    def _fallback(self, exact):
        for path in (
                'cocos/image/hero/common_frame/%d.png' % self._hero_id,
                'cocos/image/hero/hero_paper/%d.png' % self._hero_id):
            if self._available(path):
                return path
        try:
            import com.data.cdata.hero as HERO_DATA
            name = HERO_DATA.data[self._hero_id].get('name')
            for hid, row in HERO_DATA.data.items():
                if hid != self._hero_id and row.get('name') == name:
                    path = 'cocos/image/hero/hero_herolist/%d.png' % hid
                    if self._available(path):
                        return path
        except Exception:
            pass
        return exact

    def loadTexture(self, path):
        if not self._available(path):
            path = self._fallback(path)
        return self._original.loadTexture(path)

    def __getattr__(self, name):
        return getattr(self._original, name)


class StartupPolicy(object):
    def __init__(self, patch, tutorial_source, log=None, collection_source=None,
                 collection_policy=None, capacity_source=None, capacity_policy=None,
                 draw_ui_source=None, draw_ui_policy=None,
                 furniture_ui_source=None, furniture_ui_policy=None, friend_ui_source=None,
                 selector_ui_source=None, selector_ui_policy=None, tutorial_completion_source=None,
                 dynamic_ui_source=None, dynamic_ui_policy=None,
                 trial_retry_source=None, trial_retry_policy=None,
                 wish_ui_source=None, wish_transport_source=None, wish_ui_policy=None,
                 render_mode='astc'):
        if any(value is not None for value in (wish_ui_source, wish_transport_source, wish_ui_policy)):
            if any(value is None for value in (wish_ui_source, wish_transport_source, wish_ui_policy)):
                raise ValueError('Wish UI, transport and policy must be supplied together')
            if dynamic_ui_source is None:
                raise ValueError('Wish UI requires its installed family companion')
        self.wish_ui_source = wish_ui_source
        self.wish_transport_source = wish_transport_source
        self.wish_ui_policy = wish_ui_policy
        self.wish_ui_module = None
        self.wish_transport_module = None
        self.wish_transport = None
        self.wish_member = None
        self.wish_ui = None
        if (trial_retry_source is None) != (trial_retry_policy is None):
            raise ValueError('Trial retry source and policy must be supplied together')
        self.trial_retry_source = trial_retry_source
        self.trial_retry_policy = trial_retry_policy
        self.trial_retry_namespace = None
        self.trial_retry = None
        if (collection_source is None) != (collection_policy is None):
            raise ValueError('Collection source and fixed policy must be supplied together')
        if (capacity_source is None) != (capacity_policy is None):
            raise ValueError('Shadow-capacity source and fixed policy must be supplied together')
        if draw_ui_policy is not None and draw_ui_source is None:
            raise ValueError('Draw UI policy requires its embedded source')
        if (furniture_ui_source is None) != (furniture_ui_policy is None):
            raise ValueError('Furniture UI source and policy must be supplied together')
        if (selector_ui_source is None) != (selector_ui_policy is None):
            raise ValueError('Selector UI source and policy must be supplied together')
        if (dynamic_ui_source is None) != (dynamic_ui_policy is None):
            raise ValueError('Dynamic UI source and policy must be supplied together')
        if dynamic_ui_source is not None and (draw_ui_source is None or friend_ui_source is None):
            raise ValueError('Dynamic UI requires its draw and friend companions')
        self.dynamic_ui_source = dynamic_ui_source
        self.dynamic_ui_policy = dynamic_ui_policy
        self.dynamic_ui_namespace = None
        self.dynamic_ui = None
        self.selector_ui_source = selector_ui_source
        self.selector_ui_policy = selector_ui_policy
        self.selector_ui_namespace = None
        self.selector_ui = None
        self.tutorial_completion_source = tutorial_completion_source
        self.tutorial_completion_namespace = None
        self.tutorial_completion = None
        self.friend_ui_source = friend_ui_source
        self.friend_ui_namespace = None
        self.friend_ui = None
        self.furniture_ui_source = furniture_ui_source
        self.furniture_ui_policy = furniture_ui_policy
        self.furniture_ui_namespace = None
        self.furniture_ui = None
        self.patch = patch
        self.tutorial_source = tutorial_source
        self.collection_source = collection_source
        self.collection_policy = collection_policy
        self.collection_namespace = None
        self.collection = None
        self.capacity_source = capacity_source
        self.capacity_policy = capacity_policy
        self.capacity_namespace = None
        self.capacity = None
        self.draw_ui_source = draw_ui_source
        self.draw_ui_policy = draw_ui_policy
        self.draw_ui_namespace = None
        self.draw_ui = None
        if render_mode not in ('astc', 'png'):
            raise ValueError('render_mode must be astc or png')
        self.render_mode = render_mode
        self.log = log or (lambda code: None)
        self.activation = None
        self.tutorials = None
        self.installed = False
        self.repair_launch = _capture_repair_launch(patch)

    def repair(self, code):
        if self.activation is not None:
            self.activation['valid'] = False
        self.patch.pconst.Q7_STARTUP_REPAIR_REQUIRED = code
        _notify_repair(self.repair_launch, code)
        self.log(code)  # fixed nonsecret codes only

    def live(self):
        return (self.activation is not None and self.activation['valid'] and
                getattr(self.patch.pconst, 'Q7_OFFLINE_MODE', False))

    def install(self):
        if self.installed:
            return self
        patch = self.patch
        part = patch.patch_part
        task = part.PartTask
        # P7 intentionally loads these as bare modules. Never import new aliases.
        query_globals = _globals(task.query)
        if (query_globals.get('pconst') is not patch.pconst or
                query_globals.get('patch_file') is not patch.patch_file or
                query_globals.get('PartTask') is not task):
            raise RuntimeError('P7 patch module identity mismatch')
        if _raw(task.query).__name__ != '_q7_local_part_query':
            raise RuntimeError('Expected original P7 local query')
        for name in ('clean', '_q7_activate_game_mode', '_q7_verify_offline_resources'):
            if not callable(getattr(patch, name, None)):
                raise RuntimeError('Expected original P7 startup methods')
        if getattr(patch, '_p7_startup_policy', None) is not None:
            raise RuntimeError('Startup policy already installed')
        old_activate = patch._q7_activate_game_mode
        old_verify = patch._q7_verify_offline_resources
        old_clean = patch.clean
        old_info = _raw(task.clean_info)
        old_query = _raw(task.query)
        old_query_complete = _raw(task.query_complete)
        old_download_complete = _raw(task.download_complete)
        verified = [None]

        def verify():
            if self.activation is not None:
                self.activation['valid'] = False
            verified[0] = None
            try:
                state = old_verify()  # all original schema/native checks remain
                verified[0] = (state, _freeze(state))
                return state
            except Exception:
                self.repair('resource_verify_failed')
                raise

        def activate(state):
            if verified[0] is None or verified[0][0] is not state or verified[0][1] != _freeze(state):
                self.repair('unverified_activation')
                raise RuntimeError('Resource activation lacks current verification')
            verified[0] = None  # verified result can authorize activation only once
            if self.activation is not None:
                self.activation['valid'] = False
            try:
                result = old_activate(state)
                self.activation = {'valid': True, 'scheduled': False, 'issued': False,
                    'basis': _freeze((task.PACKS, task.PARTS, task.CHECKS))}
                patch.pconst.INDEX = 640
                patch.pconst.Q7_STARTUP_REPAIR_REQUIRED = None
                return result
            except Exception:
                self.repair('resource_activation_failed')
                raise

        def hydrate():
            if self.live():
                task.PACKS, task.PARTS, task.CHECKS = _thaw(self.activation['basis'])

        def clean_info(instance, *args, **kwargs):
            result = old_info(instance, *args, **kwargs)
            hydrate()
            return result

        def query(instance, callback):
            if getattr(patch.pconst, 'Q7_OFFLINE_MODE', False) and not self.live():
                callback(None)  # explicit terminal failure, never fake success
                return
            if self.live() and (not task.PACKS or not task.PARTS or not task.CHECKS):
                hydrate()
            def finished(size):
                if size is None and self.activation is not None:
                    self.repair('resource_query_failed')
                return callback(size)
            try:
                return old_query(instance, finished)
            except Exception:
                self.repair('resource_query_exception')
                raise

        def query_complete(instance, code, size):
            if code and self.activation is not None:
                self.repair('resource_query_failed')
            return old_query_complete(instance, code, size)

        def download_complete(instance, code):
            if code and self.activation is not None:
                self.repair('resource_download_failed')
            return old_download_complete(instance, code)

        def clean(state):
            result = old_clean(state)  # original removes logic/com/gg first
            if state and getattr(patch.pconst, 'Q7_OFFLINE_MODE', False):
                if not self.live():
                    self.repair('inactive_game_start')
                    raise RuntimeError('Resource activation requires repair')
                try:
                    self.install_render_compat()
                    self.install_wish_early()
                    self.install_trial_retry()
                    self.install_tutorials()
                    self.install_event_trigger_inflight()
                    self.install_tutorial_completion()
                    warning = None
                    if self.tutorials is not None:
                        warning = self.tutorials.get('namespace', {}).get('install_paid_warning')
                    if callable(warning):
                        warning()
                    self.install_collection()
                    self.install_capacity()
                    self.install_draw_ui()
                    self.install_furniture_ui()
                    self.install_friend_ui()
                    self.install_selector_ui()
                    self.install_dynamic_ui()
                    self.install_pixel_asset_fallbacks()
                    self.install_wish_ui()
                    self.install_tutorial_completion_panels()
                    self.install_login()
                    self.install_wardrobe_lifecycle()
                    self.install_settlement_lifecycle()
                    install_valentine_letters()
                    install_high_fps()
                    install_nickname_review()
                    self.install_rpc_listener_guard()
                    self.install_login_send_diagnostic()
                    self.install_city_event_diagnostics()
                    self.check_avatar()
                except Exception:
                    self.repair('startup_policy_install_failed')
                    raise  # prevents original done from importing/starting game logic
            return result

        patch._q7_verify_offline_resources = verify
        patch._q7_activate_game_mode = activate
        patch.clean = clean
        task.clean_info = clean_info
        task.query = query
        task.query_complete = query_complete
        task.download_complete = download_complete
        patch._p7_startup_policy = self
        install_offline_hotfix_guard(patch)
        if callable(getattr(patch, 'start', None)):
            if not self.install_startup_receipt():
                raise RuntimeError('Startup receipt controller unavailable')
        self.installed = True
        return self

    def _avatar(self):
        module = sys.modules.get('entity.ClientAvatar')
        return getattr(module, 'ClientAvatar', None) if module is not None else None

    def check_avatar(self):
        avatar = self._avatar()
        if avatar is None:
            return
        if self.tutorials is None:
            raise RuntimeError('ClientAvatar constructed before tutorial policy')
        for name, replacement in self.tutorials['avatar_methods'].items():
            if _raw(getattr(avatar, name, None)) is not replacement:
                raise RuntimeError('ClientAvatar tutorial method identity mismatch')
        if self.tutorial_completion is not None:
            self.tutorial_completion.check_avatar(avatar)
        if (self.trial_retry is not None and
                _raw(getattr(avatar, 'battleRealFailWithEventMode', None)) is not self.trial_retry[3]):
            raise RuntimeError('ClientAvatar trial retry method identity mismatch')
        if self.wish_member is not None:
            self.wish_member.check_avatar(avatar)
        if self.capacity is not None:
            # _avatar() is the ClientAvatar class, not an instance. Capacity's
            # projection check requires an instance; verify class/owner/method
            # assembly here and defer instance projection to check()/init_from_dict.
            self.capacity.check_avatar_class(avatar)

    def _wish_module(self, name, source, current):
        if current is not None:
            if (sys.modules.get(name) is not current or
                    getattr(current, '_q7_startup_policy', None) is not self or
                    getattr(current, '_q7_startup_source', None) != source):
                raise RuntimeError('Wish embedded module generation changed')
            return current
        if name in sys.modules:
            raise RuntimeError('Foreign Wish embedded module already loaded')
        module = types.ModuleType(name)
        module._q7_startup_policy = self
        module._q7_startup_source = source
        sys.modules[name] = module
        try:
            eval(compile(source, name + '.py', 'exec'), module.__dict__, module.__dict__)
        except Exception:
            if sys.modules.get(name) is module:
                del sys.modules[name]
            raise
        return module

    def install_render_compat(self):
        """Explicit PNG compatibility only; default ASTC path is untouched.

        The original UI manager chooses cocos2 only from its runtime texture
        capability check.  This hook runs after patch.clean() (which purges
        logic/com/gg) and before game logic constructs UIManager.
        """
        if self.render_mode != 'png':
            return
        import C_file
        if not callable(getattr(C_file, 'set_path_patch', None)):
            raise RuntimeError('Original C_file path patch unavailable')
        C_file.set_path_patch('cocos', 'cocos')
        # UIManager._do_init calls this after construction begins; forcing only
        # the path setter is insufficient because the original method can select
        # cocos2 from a false-positive driver report.
        import cocos.ui_manager as ui_manager
        original = getattr(ui_manager.UIManager, 'init_astc_modifer', None)
        if not callable(original):
            raise RuntimeError('Original UIManager.init_astc_modifer unavailable')
        def png_astc(self):
            C_file.set_path_patch('cocos', 'cocos')
        ui_manager.UIManager.init_astc_modifer = png_astc
        self.log('render_png_compat')

    def install_wish_early(self):
        if self.wish_ui_source is None:
            return
        __import__('gg')
        self.wish_transport_module = self._wish_module(
            'project7_wish_transport', self.wish_transport_source, self.wish_transport_module)
        self.wish_ui_module = self._wish_module(
            'project7_wish_ui', self.wish_ui_source, self.wish_ui_module)
        self.wish_transport = self.wish_transport_module.install()
        self.wish_member = self.wish_ui_module.install_member_guard(self.wish_transport)

    def install_wish_ui(self):
        if self.wish_ui_source is None:
            return
        if (self.wish_member is None or self.dynamic_ui is None or self.friend_ui is None or
                self.draw_ui_namespace is None):
            raise RuntimeError('Wish exact companion installation incomplete')
        self._wish_module('project7_wish_ui', self.wish_ui_source, self.wish_ui_module)
        self._wish_module('project7_wish_transport', self.wish_transport_source, self.wish_transport_module)
        self.wish_ui = self.wish_ui_module.install(
            self.wish_ui_policy,
            history_avatar_type=self.draw_ui_namespace['_HistoryAvatar'],
            friend_owner=self.friend_ui, families_owner=self.dynamic_ui,
            member_owner=self.wish_member)

    def install_trial_retry(self):
        if self.trial_retry_source is None:
            return
        if self.trial_retry_namespace is None:
            namespace = {}
            eval(compile(self.trial_retry_source, 'project7_trial_retry_compat.py', 'exec'),
                 namespace, namespace)
            if not callable(namespace.get('install')):
                raise RuntimeError('Trial retry installer missing')
            self.trial_retry_namespace = namespace
        member = __import__('entity.avatar_members.BattleStageMember', fromlist=['Member'])
        gg = __import__('gg')
        self.trial_retry = self.trial_retry_namespace['install'](member, gg, self.trial_retry_policy)

    def install_tutorials(self):
        if self._avatar() is not None and self.tutorials is None:
            raise RuntimeError('ClientAvatar already constructed')
        targets = [
            ('entity.avatar_attrs.NewbeeData', 'NewbeeData', 'canNewbeeTrigger', 'no_newbee_trigger'),
            ('entity.avatar_attrs.NewbeeData', 'NewbeeData', 'checkAllNewbee', 'clear_newbee_queue')]
        for name in ('clientTriggerNewbeeFromClient', 'clientAskTriggerNewbee', 'checkProcessingNewbee', 'triggerNewbee'):
            targets.append(('entity.avatar_members.NewbeeMember', 'Member', name, 'skip_newbee_request'))
        targets.append(('entity.avatar_members.EventTriggerMember', 'Member', 'startEventNewbee', 'continue_story_without_teaching'))
        targets.extend([
            ('cocos.panels.newbee_guidance', 'Panel', 'trigger_newbee_event', 'skip_guidance'),
            ('cocos.panels.newbee_guidance', 'Panel', 'notify_show', 'skip_tutorial_panel'),
            ('cocos.panels.combat_monster', 'Panel', 'notify_show', 'skip_new_monster_tutorial'),
            ('cocos.panels.city', 'Panel', 'on_yanhua_guide_click', 'skip_tutorial_panel'),
            ('cocos.panels.common_confirm', 'Panel', 'notify_guide_bind', 'skip_tutorial_panel')])
        for name in ('notify_mask_area', 'notify_mask_build', 'notify_mask_upgrade'):
            targets.append(('cocos.panels.newbee_mask', 'Panel', name, 'skip_tutorial_panel'))
        for module in ('combat_guide_hero', 'combat_guide_restrain', 'city_yanhua_guide'):
            targets.append(('cocos.panels.' + module, 'Panel', 'notify_show', 'skip_tutorial_panel'))
        loaded = []
        for module_name, cls_name, method, replacement in targets:
            module = __import__(module_name, fromlist=[cls_name])
            loaded.append((module, getattr(module, cls_name), method, replacement))
        game_object = __import__('com.base.game_object', fromlist=['members_cache'])
        if self.tutorials is not None:
            if all(self.tutorials['classes'].get((m.__name__, c.__name__)) is c for m,c,n,r in loaded):
                for module, cls, method, replacement in loaded:
                    if _raw(getattr(cls, method, None)) is not self.tutorials['namespace'][replacement]:
                        raise RuntimeError('Tutorial policy was replaced')
                self.check_avatar()
                return
            self.tutorials = None
            if self._avatar() is not None:
                raise RuntimeError('Fresh tutorial classes with existing ClientAvatar')
        for module, cls, method, replacement in loaded:
            if '.avatar_members.' in module.__name__ and cls in game_object.members_cache:
                raise RuntimeError('Member cache materialized before tutorial policy')
        namespace = {'_f7_log': lambda ignored: self.log('tutorial_ui_policy')}
        eval(compile(self.tutorial_source, 'offline_tutorials.py', 'exec'), namespace, namespace)
        namespace['install_tutorial_bypass']()
        avatar_methods = {}
        classes = {}
        for module, cls, method, replacement in loaded:
            if _raw(getattr(cls, method, None)) is not namespace[replacement]:
                raise RuntimeError('Tutorial method not installed')
            classes[(module.__name__, cls.__name__)] = cls
            if '.avatar_members.' in module.__name__:
                avatar_methods[method] = namespace[replacement]
        self.tutorials = {'classes': classes, 'namespace': namespace, 'avatar_methods': avatar_methods}
        self.check_avatar()  # dependency imports may have constructed the real class

    def install_tutorial_completion(self):
        if self.tutorial_completion_source is None:
            return
        if self.tutorial_completion_namespace is None:
            namespace = {}
            eval(compile(self.tutorial_completion_source, 'project7_tutorial_completion.py', 'exec'),
                 namespace, namespace)
            if not callable(namespace.get('install')) or not callable(namespace.get('install_panels')):
                raise RuntimeError('Tutorial completion installers missing')
            self.tutorial_completion_namespace = namespace
        self.tutorial_completion = self.tutorial_completion_namespace['install']()

    def install_tutorial_completion_panels(self):
        if self.tutorial_completion_source is not None:
            self.tutorial_completion_namespace['install_panels']()

    def install_collection(self):
        # Production embeds both reviewed sources. Optional arguments preserve
        # isolated resource/login harnesses without importing any game panels.
        if self.collection_source is None:
            return
        if self.collection_namespace is None:
            namespace = {}
            eval(compile(self.collection_source, 'project7_collection_visibility.py', 'exec'),
                 namespace, namespace)
            if not callable(namespace.get('install')):
                raise RuntimeError('Collection installer missing')
            self.collection_namespace = namespace
        self.collection = self.collection_namespace['install'](self.collection_policy)

    def install_capacity(self):
        if self.capacity_source is None:
            return
        if self.capacity_namespace is None:
            namespace = {}
            eval(compile(self.capacity_source, 'project7_shadow_capacity.py', 'exec'),
                 namespace, namespace)
            if not callable(namespace.get('install')):
                raise RuntimeError('Shadow-capacity installer missing')
            self.capacity_namespace = namespace
        self.capacity = self.capacity_namespace['install'](self.capacity_policy)

    def install_draw_ui(self):
        if self.draw_ui_source is None:
            return
        if self.draw_ui_namespace is None:
            namespace = {}
            eval(compile(self.draw_ui_source, 'project7_draw_ui.py', 'exec'), namespace, namespace)
            if not callable(namespace.get('install')):
                raise RuntimeError('Draw UI installer missing')
            self.draw_ui_namespace = namespace
        if self.draw_ui_policy is None:
            self.draw_ui = self.draw_ui_namespace['install']()
        else:
            self.draw_ui = self.draw_ui_namespace['install'](self.draw_ui_policy)

    def install_furniture_ui(self):
        if self.furniture_ui_source is None:
            return
        if self.furniture_ui_namespace is None:
            namespace = {}
            eval(compile(self.furniture_ui_source, 'project7_furniture_ui.py', 'exec'),
                 namespace, namespace)
            if not callable(namespace.get('install')):
                raise RuntimeError('Furniture UI installer missing')
            self.furniture_ui_namespace = namespace
        self.furniture_ui = self.furniture_ui_namespace['install'](self.furniture_ui_policy)

    def install_friend_ui(self):
        if self.friend_ui_source is None:
            return
        if self.draw_ui_namespace is None:
            raise RuntimeError('Friend UI requires the installed draw UI namespace')
        if self.friend_ui_namespace is None:
            namespace = {}
            eval(compile(self.friend_ui_source, 'project7_friend_ui.py', 'exec'),
                 namespace, namespace)
            if not callable(namespace.get('install')):
                raise RuntimeError('Friend UI installer missing')
            self.friend_ui_namespace = namespace
        self.friend_ui = self.friend_ui_namespace['install'](
            history_avatar_type=self.draw_ui_namespace['_HistoryAvatar'])

    def install_selector_ui(self):
        if self.selector_ui_source is None:
            return
        if self.draw_ui_namespace is None:
            raise RuntimeError('Selector UI requires the installed draw UI namespace')
        if self.selector_ui_namespace is None:
            namespace = {}
            eval(compile(self.selector_ui_source, 'project7_selector_ui.py', 'exec'),
                 namespace, namespace)
            if not callable(namespace.get('install')):
                raise RuntimeError('Selector UI installer missing')
            self.selector_ui_namespace = namespace
        self.selector_ui = self.selector_ui_namespace['install'](
            self.selector_ui_policy,
            history_avatar_type=self.draw_ui_namespace['_HistoryAvatar'])

    def install_wardrobe_lifecycle(self):
        import cocos.panels.hero_wardrobe as module
        if not install_wardrobe_lifecycle_guard(module):
            raise RuntimeError('Hero wardrobe refresh_pendant unavailable')
        return True

    def install_settlement_lifecycle(self):
        import cocos.panels.settlement_fullscreen_bonus as bonus
        import cocos.panels.settlement_reward_chest as chest
        if not install_panel_delay_guard(bonus, ('refresh_skin_comps', '__refresh_pendant_comps')):
            raise RuntimeError('Settlement bonus delayed methods unavailable')
        if not install_panel_delay_guard(chest, ('update_combat_reward',)):
            raise RuntimeError('Settlement reward chest delayed method unavailable')
        return True

    def install_event_trigger_inflight(self):
        try:
            import entity.avatar_members.EventTriggerMember as event_member
        except Exception:
            return False
        avatar_module = sys.modules.get('entity.ClientAvatar')
        avatar = getattr(avatar_module, 'ClientAvatar', None) if avatar_module is not None else None
        owner = install_event_trigger_inflight(event_member.Member, event_member.rpc_method, avatar)
        if avatar is not None:
            for name in ('startEvent', 'startEventReply', 'pullEventsReply', 'pushEvents', 'eventOnLogin'):
                if _raw(getattr(avatar, name, None)) is not _raw(getattr(event_member.Member, name, None)):
                    raise RuntimeError('Event trigger ClientAvatar binding mismatch: ' + name)
        return owner

    def install_city_event_diagnostics(self):
        """Log-only city/event state. No return values or callbacks are changed."""
        try:
            import entity.avatar_members.EventTriggerMember as event_member
            import entity.avatar_members.StatusMember as status_member
            import cocos.panels.city as city_panel
        except Exception:
            return False
        if getattr(event_member.Member, '_q7_city_event_diagnostics', None):
            return True

        def emit(label, fields):
            try:
                print('P7_CITY_DIAG ' + label + ' ' + ' '.join(
                    '%s=%r' % (key, fields[key]) for key in sorted(fields)))
            except Exception:
                pass

        original_try = event_member.Member.tryNotifyEvent
        def diagnostic_try(self, ignoreClientLimit=False):
            data = getattr(self, 'eventTriggerData', None)
            available = getattr(data, 'availableEvents', None) or {}
            processing = getattr(data, 'processingEventsServer', None) or ()
            before = {'processing': sorted(list(processing)),
                      'available': sorted(list(available.keys())),
                      'ignore': bool(ignoreClientLimit)}
            emit('try_notify', before)
            result = original_try(self, ignoreClientLimit)
            after = {'processing': sorted(list(processing)),
                     'available': sorted(list(available.keys())),
                     'result': bool(result)}
            emit('try_notify_result', after)
            return result
        event_member.Member.tryNotifyEvent = diagnostic_try

        original_enter = status_member.Member.statusSwitchEnterArea
        def diagnostic_enter(self, areaid, successCb):
            status = None
            try:
                status = self.cityData.get_area_state(areaid).status
            except Exception:
                pass
            emit('area_enter', {'area': areaid, 'status': status,
                                'callback': successCb is not None})
            return original_enter(self, areaid, successCb)
        status_member.Member.statusSwitchEnterArea = diagnostic_enter

        original_open = city_panel.Panel.notify_entrance_open
        def diagnostic_open(self, area_id, instant=False, zoom_scn=True):
            status = None
            in_city = None
            try:
                status = gg.avatar.cityData.get_area_state(area_id).status
                in_city = self.is_in_city()
            except Exception:
                pass
            emit('notify_open', {'area': area_id, 'status': status,
                                 'in_city': in_city, 'instant': bool(instant),
                                 'zoom': bool(zoom_scn)})
            return original_open(self, area_id, instant, zoom_scn)
        city_panel.Panel.notify_entrance_open = diagnostic_open
        event_member.Member._q7_city_event_diagnostics = True
        return True

    def install_startup_receipt(self):
        """Resolve the manager loopback receipt before the stock updater.

        A transient or invalid loopback reply is an explicit local-start failure,
        never a silent resources-mode fallback into the official updater.
        """
        patch = self.patch
        original_start = getattr(patch, 'start', None)
        if not callable(original_start):
            return False
        patch_globals = _globals(original_start)
        render = patch_globals.get('render')
        done = patch_globals.get('done')
        # `patch_panel` is the module imported by patch.py; the callable is its
        # PatchPanel class. Calling the module raised "'module' object is not
        # callable" on the failure path, hiding the real bootstrap error.
        panel_ref = patch_globals.get('patch_panel')
        if panel_ref is not None and not callable(panel_ref):
            panel_ref = getattr(panel_ref, 'PatchPanel', None)
        panel_type = panel_ref
        if render is None or not callable(done) or panel_type is None:
            raise RuntimeError('Startup receipt render/done/panel unavailable')
        if getattr(patch, '_q7_startup_receipt_installed', False):
            return True

        def diagnostic(stage, **fields):
            try:
                print('P7_STARTUP_RECEIPT stage=%s %s' % (
                    stage, ' '.join('%s=%r' % (key, fields[key]) for key in sorted(fields))))
            except Exception:
                pass

        diagnostic('INSTALL', port=23334, window_s=_BOOTSTRAP_WINDOW_S,
                   timeout_ms=int(_BOOTSTRAP_TIMEOUT_S * 1000))

        def query_receipt():
            import urllib2
            clock, sleep = _BOOTSTRAP_CLOCK, _BOOTSTRAP_SLEEP
            last = None
            started = clock()
            deadline = started + _BOOTSTRAP_WINDOW_S
            attempt = 0
            while clock() < deadline:
                attempt += 1
                try:
                    response = urllib2.build_opener(urllib2.ProxyHandler({})).open(
                        'http://127.0.0.1:23334/bootstrap', timeout=_BOOTSTRAP_TIMEOUT_S)
                    try:
                        data = response.read(128)
                    finally:
                        response.close()
                    if data == 'project7-bootstrap-v1\ngame\n':
                        diagnostic('QUERY_OK', attempt=attempt, mode='game',
                                   elapsed_ms=int((clock() - started) * 1000))
                        return 'game'
                    if data == 'project7-bootstrap-v1\nresources\n':
                        diagnostic('QUERY_OK', attempt=attempt, mode='resources',
                                   elapsed_ms=int((clock() - started) * 1000))
                        return 'resources'
                    last = 'invalid_reply'
                except Exception as error:
                    last = type(error).__name__
                diagnostic('QUERY_RETRY', attempt=attempt, code=last,
                           elapsed_ms=int((clock() - started) * 1000))
                sleep(_BOOTSTRAP_RETRY_SLEEP_S)
            diagnostic('QUERY_FAILED', code=last,
                       elapsed_ms=int((clock() - started) * 1000))
            raise RuntimeError('local bootstrap unavailable: %s' % last)

        def startup():
            result = {}

            def work():
                diagnostic('QUERY_BEGIN')
                try:
                    result['mode'] = query_receipt()
                except Exception as error:
                    result['error'] = type(error).__name__
                    diagnostic('QUERY_ERROR', code=type(error).__name__)
                result['ready'] = True

            import threading
            worker = threading.Thread(target=work)
            worker.daemon = True
            worker.start()

            def dispatch(*args):
                if not result.get('ready') or result.get('dispatched'):
                    return
                result['dispatched'] = True
                mode = result.get('mode')
                if mode == 'game':
                    state = None
                    try:
                        state = patch._q7_verify_offline_resources()
                        patch._q7_activate_game_mode(state)
                    except Exception as error:
                        diagnostic('SNAPSHOT_FAILED', code=type(error).__name__)
                        self.repair('resource_verify_failed')
                        panel = panel_type()
                        panel.set_text('Project7 local resources unavailable; use resources mode')
                        render.set_logic(lambda *args: None)
                        return
                    step_globals = _globals(patch.clean)
                    if '_step_skip' in step_globals:
                        step_globals['_step_skip'] = True
                    diagnostic('GAME_READY')
                    print('Project7 game mode: local resources verified; official updater skipped')
                    render.set_logic(lambda *args: None)
                    done(True)
                    return
                if mode == 'resources':
                    # Receipt explicitly selected resource mode: preserve the
                    # original updater rather than treating it as a timeout.
                    diagnostic('RESOURCES')
                    original_start()
                    return
                diagnostic('MODE_FAILED', code='unavailable')
                self.repair('resource_verify_failed')
                panel = panel_type()
                panel.set_text('Project7 local bootstrap mode unavailable; repair required')
                render.set_logic(lambda *args: None)

            render.logic = dispatch
            render.set_logic(dispatch)

        patch.start = startup
        patch._q7_startup_receipt_installed = True
        return True

    def install_rpc_listener_guard(self):
        """Keep original RPC listener teardown idempotent after disconnect."""
        try:
            from mobilerpc.RpcChannel import MobileRpcChannel
        except Exception:
            return False
        if getattr(MobileRpcChannel, '_q7_idempotent_unreg', False):
            return True
        original = _raw(MobileRpcChannel.unreg_listener)

        def unreg_listener(self, listener):
            listeners = getattr(self, 'con_listeners', None)
            if listeners is None:
                return
            discard = getattr(listeners, 'discard', None)
            if callable(discard):
                discard(listener)
                return
            return original(self, listener)

        MobileRpcChannel.unreg_listener = unreg_listener
        MobileRpcChannel._q7_idempotent_unreg = True
        return True

    def install_login_send_diagnostic(self):
        """Fixed login send stage/size logs; never log credentials or payload."""
        try:
            from lib.client import ServerProxy as proxy_module
            from bson import BSON
        except Exception:
            return False
        target = proxy_module.ServerProxy
        if getattr(target, '_q7_login_send_diagnostic', False):
            return True
        original = _raw(target.call_server_method)

        def call_server_method(self, methodname, parameters=None, entityid=None):
            if methodname != 'login':
                return original(self, methodname, parameters, entityid)
            size = -1
            try:
                size = len(BSON.encode(parameters)) if parameters is not None else 0
            except Exception:
                pass
            print('P7_AUTH_CLIENT stage=login_send_begin bytes=%s' % size)
            try:
                result = original(self, methodname, parameters, entityid)
            except Exception:
                print('P7_AUTH_CLIENT stage=login_send_exception')
                raise
            print('P7_AUTH_CLIENT stage=login_send_end bytes=%s' % size)
            return result

        target.call_server_method = call_server_method
        target._q7_login_send_diagnostic = True
        return True

    def install_login(self):
        module = __import__('cocos.panels.login', fromlist=['Panel'])
        panel = module.Panel
        click = _raw(panel.on_user_click)
        if click is not getattr(module, '_q7_click', None):
            raise RuntimeError('Expected P7 patched click')
        existing = getattr(panel, '_p7_startup_policy', None)
        if existing is self:
            return
        if existing is not None:
            raise RuntimeError('Unexpected login scheduler owner')
        self_policy = self
        def notify_setting(instance):
            activation = self_policy.activation
            if not self_policy.live() or activation['scheduled']:
                return
            # Consume the sole automatic opportunity before enqueueing, even if stale later.
            activation['scheduled'] = True
            gg = module.gg
            logic = gg.logic
            ui = gg.ui
            panels = ui.panels
            def issue():
                if (self_policy.activation is not activation or not self_policy.live() or activation['issued'] or
                        sys.modules.get('gg') is not gg or module.gg is not gg or
                        gg.logic is not logic or gg.ui is not ui or ui.panels is not panels or
                        panels._panels.get('login') is not instance or
                        type(instance) is not panel or _raw(panel.on_user_click) is not click or
                        not getattr(instance, 'valid', False) or not getattr(instance, 'visible', False) or
                        (getattr(instance, 'mask', None) is not None and instance.mask.isVisible()) or
                        logic.game_state.current != module.const.GameState.LOGIN or
                        logic.online_state.current != module.const.OnlineState.OFFLINE or
                        getattr(gg, '_q7_login_attempt', None) is not None):
                    return
                activation['issued'] = True
                click(instance, 0, module.cc.ccui.TOUCH_EVENT_ENDED)
            gg.exec_delay(700, issue)
        panel.notify_setting = notify_setting
        panel._p7_startup_policy = self

    def _fix_water_model(self, model):
        if model is None:
            return
        try:
            import C_file
            if C_file.find_res_file('model/pve/zjm/water_n2.tga', ''):
                return
            material = model.all_materials
            material.set_texture('NormalMap', 'fx/texture/normalmap/noise_wave_111.dds')
            # The material requests reflection without a TexReflection parameter;
            # disable the missing reflection path instead of rendering black.
            material.set_macro('MIRROR_ENABLE', 'FALSE')
            material.rebuild_tech()
        except Exception:
            pass

    def install_pixel_asset_fallbacks(self):
        """Static resource gaps seen on Pixel: water normal map and non-public portraits."""
        try:
            from res_mgr.effects import water_adjust
            effect = water_adjust.Effect
            original_water = getattr(effect, 'reset_model_tech', None)
            if callable(original_water) and not getattr(original_water, '_q7_water_fallback', False):
                owner = self
                def water_reset(self):
                    result = original_water(self)
                    owner._fix_water_model(getattr(self, 'water_gim', None))
                    return result
                water_reset._q7_water_fallback = True
                effect.reset_model_tech = water_reset
        except Exception:
            pass
        try:
            from res_mgr.effects import water_adjust_new
            effect_new = water_adjust_new.Effect
            original_new = getattr(effect_new, 'set_scn_data', None)
            if callable(original_new) and not getattr(original_new, '_q7_water_fallback', False):
                owner = self
                def water_new(self, data):
                    result = original_new(self, data)
                    try:
                        import gg
                        model = gg.scene_mgr.active_scn.get_model('water_442') if gg.scene_mgr.active_scn else None
                        owner._fix_water_model(model)
                    except Exception:
                        pass
                    return result
                water_new._q7_water_fallback = True
                effect_new.set_scn_data = water_new
        except Exception:
            pass
        try:
            from cocos.comps.hero_herolist_common import hero as hero_comp
            original_hero = getattr(hero_comp.Comp, 'set_hero', None)
            if callable(original_hero) and not getattr(original_hero, '_q7_portrait_fallback', False):
                def set_hero(self, hero_id, style='item'):
                    image = getattr(self, 'img', None)
                    if image is not None:
                        self.img = _PortraitImageProxy(image, hero_id)
                    try:
                        return original_hero(self, hero_id, style)
                    finally:
                        self.img = image
                set_hero._q7_portrait_fallback = True
                hero_comp.Comp.set_hero = set_hero
        except Exception:
            pass
        return self

    def install_dynamic_ui(self):
        if self.dynamic_ui_source is None:
            return
        if self.draw_ui_namespace is None or self.friend_ui is None:
            raise RuntimeError('Dynamic UI requires the installed draw and friend owners')
        if self.dynamic_ui_namespace is None:
            namespace = {}
            eval(compile(self.dynamic_ui_source, 'project7_dynamic_ui_families.py', 'exec'),
                 namespace, namespace)
            if not callable(namespace.get('install')):
                raise RuntimeError('Dynamic UI installer missing')
            self.dynamic_ui_namespace = namespace
        self.dynamic_ui = self.dynamic_ui_namespace['install'](
            self.dynamic_ui_policy,
            history_avatar_type=self.draw_ui_namespace['_HistoryAvatar'],
            friend_owner=self.friend_ui)


def install(patch, tutorial_source, log=None, collection_source=None, collection_policy=None, capacity_source=None, capacity_policy=None, draw_ui_source=None, draw_ui_policy=None, furniture_ui_source=None, furniture_ui_policy=None, friend_ui_source=None, selector_ui_source=None, selector_ui_policy=None, tutorial_completion_source=None, dynamic_ui_source=None, dynamic_ui_policy=None, trial_retry_source=None, trial_retry_policy=None, wish_ui_source=None, wish_transport_source=None, wish_ui_policy=None, render_mode='astc'):
    return StartupPolicy(patch, tutorial_source, log, collection_source, collection_policy, capacity_source, capacity_policy, draw_ui_source, draw_ui_policy, furniture_ui_source, furniture_ui_policy, friend_ui_source, selector_ui_source, selector_ui_policy, tutorial_completion_source, dynamic_ui_source, dynamic_ui_policy, trial_retry_source, trial_retry_policy, wish_ui_source, wish_transport_source, wish_ui_policy, render_mode).install()
