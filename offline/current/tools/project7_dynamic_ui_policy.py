"""Readonly UI snapshot projection from the frozen dynamic public bundle.
Does not enable historical IDs or mutate any runtime catalog/clock/owner.
"""
import _bootstrap  # noqa: E402,F401
import json,sys
from pathlib import Path
from _bootstrap import ROOT
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from project7_dynamic_catalog import load,ASSET_SHA256,BASE_SHA
from project7_draw_history_ir.codec import untyped
SCHEMA='project7-dynamic-ui-v1'
REQUIRED=('cocos/card_tab.csb','cocos/card_box.csb','cocos/card_jiaozhi_2.csb','cocos/card_common.csb','cocos/common_frame.csb','cocos/common_property.csb','cocos/common_icon.csb','cocos/hero_herolist_common.csb','cocos/res/hkytw5.ttf','cocos/card_activity_7.csb','cocos/image/hero/skill_dazhao/147.png','cocos/image/bbs/activity_39_mask_dispatch.png','cocos/image/item/common/11733.png')
def policy(directory=None):
 data=load() if directory is None else load(directory)
 # Explicit vertical scope is configuration, not an alternative reward handler.
 selected=[p for p in data['pools'] if p['pool']==485]
 if len(selected)!=1:raise ValueError('dynamic UI source485 missing')
 p=selected[0];info=untyped(p['raw']);jiaozhi=[untyped(t['raw']) for t in p['jiaozhi']];charge=[untyped(t['raw']) for t in p['charge']]
 if p['epoch']!=1631084400 or [(r['id'],r['times']) for r in charge]!=[(274,12),(275,36),(276,90),(277,180)] or [(r['id'],r['jiaozhi_count']) for r in jiaozhi]!=[(133,1),(134,2),(135,3),(136,4),(137,5),(138,6)]:raise ValueError('dynamic UI source oracle changed')
 return {'schema':SCHEMA,'backend_sha256':ASSET_SHA256,'base_sha256':BASE_SHA,'pools':[485],'epochs':{'485':p['epoch']},'info':info,'charge':charge,'jiaozhi':jiaozhi,'required_assets':list(REQUIRED),'optional_poster':'cocos/card_activity_61.csb','public_ready_claim':False,'policy':'dynamic485-fixed-archive-ui-v1'}
def canonical(value):return json.dumps(value,sort_keys=True,ensure_ascii=True,separators=(',',':')).encode('ascii')
def ui_policy(directory=None):return policy(directory)
def main():
 import argparse,hashlib
 parser=argparse.ArgumentParser();parser.add_argument('--directory',type=Path);parser.add_argument('--output',type=Path);args=parser.parse_args()
 if args.output is not None and (args.output.exists() or args.output.is_symlink()):raise FileExistsError(args.output)
 raw=canonical(policy(args.directory))
 if args.output is not None:
  with args.output.open('xb') as handle:handle.write(raw)
 print('policy bytes=%d SHA256=%s public_ready=false'%(len(raw),hashlib.sha256(raw).hexdigest()))
if __name__=='__main__':main()
