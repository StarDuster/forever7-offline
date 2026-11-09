"""Maintainer-only projection of the fixed public model index; no asset/game execution.
Default check uses bundled policy only. Runtime consumers receive embedded ASCII
policy text and never read the audit or any analysis path.
"""
from pathlib import Path
import argparse,hashlib,json
HERE=Path(__file__).resolve().parent
AUDIT_SHA='d9e3dadcb084dfa05f0e86dd7d0a0532c8c1d9653d550f8a2fe72ceb7a914758'
POLICY_SHA='453340b4f36c5de867d2288ef2e4afc70561c62098ee5fd60d1ddbd74d506fb9'
def sha(data):return hashlib.sha256(data).hexdigest()
def encoded(data):return (json.dumps(data,sort_keys=True,separators=(',',':'))+'\n').encode('ascii')
def project(path):
 blob=Path(path).read_bytes()
 if sha(blob)!=AUDIT_SHA:raise ValueError('Fixed public model index changed')
 audit=json.loads(blob);models=audit['models']
 ids=sorted(k for k,v in models.items() if v['status']=='found')
 if len(models)!=395 or len(ids)!=393 or any(not value.isdigit() for value in ids):raise ValueError('Unexpected model index shape')
 return {'format':'project7-collection-visibility-policy-v1','model_index_sha256':AUDIT_SHA,
  'indexed_model_ids':ids,'scope':'GIM entry index only; not proof of textures, animations, transitive dependencies or successful rendering'}
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--audit',type=Path);parser.add_argument('--write',action='store_true');args=parser.parse_args()
 path=HERE/'policy.json'
 if args.write:
  if args.audit is None:raise ValueError('Explicit public audit required')
  data=encoded(project(args.audit))
  if POLICY_SHA and sha(data)!=POLICY_SHA:raise ValueError('Projected policy changed')
  path.write_bytes(data);print(sha(data))
 else:
  blob=path.read_bytes()
  if sha(blob)!=POLICY_SHA:raise ValueError('Bundled policy hash mismatch')
  print('PASS fixed public model-index policy')
if __name__=='__main__':main()
