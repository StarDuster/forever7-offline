# Reuse the requested qualification scene instead of comparing its name to a list.
import gg
import entity.avatar_members.HeroTestMember as _q7_exam
import entity.avatar_attrs.HeroTestData as _q7_exam_data


def _q7_exam_init(self, data):
    _q7_exam_data.HeroTestData._q7_original_init(self, data)
    self.integrationTestScenePos = dict((data or {}).get('q7ScenePos', []))


def _q7_exam_switch_scene(self, name):
    names = list(_q7_exam.const.HEROTEST_SCENE_INFO.values())
    if name not in names:
        return
    scene = None
    for candidate in list(gg.city_container.scene_objs.values()):
        if getattr(candidate, 'mod_name', None) == name:
            scene = candidate
            break
    if scene is None:
        module = __import__('game_scene.%s' % name, fromlist=[''])
        scene = module.Scene()
        scene.mod_name = name
        gg.city_container.add_scene(scene.scene_id, scene)
    setattr(gg, name, scene)
    gg.city_container.push_scene(scene.scene_id, force=True)
    for candidate in list(gg.city_container.scene_objs.values()):
        other = getattr(candidate, 'mod_name', None)
        if other in names and candidate is not scene:
            gg.city_container.remove_scene(candidate.scene_id)
            if getattr(gg, other, None) is candidate:
                delattr(gg, other)


_q7_exam.Member.heroTestSwitchScene = _q7_exam_switch_scene
# qualification runs after login: GameObjectMeta has already copied Member
# methods onto ClientAvatar. Patch the live class consumer too, preserving the
# original callable for identity/generation checks.
_q7_avatar_cls = type(gg.avatar) if getattr(gg, 'avatar', None) is not None else None
if _q7_avatar_cls is not None:
    if not hasattr(_q7_avatar_cls, '_q7_original_heroTestSwitchScene'):
        _q7_avatar_cls._q7_original_heroTestSwitchScene = getattr(
            _q7_avatar_cls, 'heroTestSwitchScene', None)
    _q7_avatar_cls.heroTestSwitchScene = _q7_exam_switch_scene
if not hasattr(_q7_exam_data.HeroTestData, '_q7_original_init'):
    _q7_exam_data.HeroTestData._q7_original_init = _q7_exam_data.HeroTestData.initFromDict
    _q7_exam_data.HeroTestData.initFromDict = _q7_exam_init
gg.avatar.callServerMethod('evalEcho', {'m': 'q7_qualification_scene_v1'})
