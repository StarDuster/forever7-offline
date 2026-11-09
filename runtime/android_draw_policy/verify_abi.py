"""Host-only ABI audit against fixed actual patched manager, no bytecode execution."""
from pathlib import Path
import re,subprocess,json
ROOT=Path(__file__).resolve().parents[2]
EXPECTED={
'BsonLite':{'EMPTY_DOCUMENT':'[B','document':'([Ljava/lang/Object;)[B','documentValue':'([BLjava/lang/String;)[B','withProfileInt':'([BLjava/lang/String;I)[B','withProfileDocument':'([BLjava/lang/String;[B)[B','withProfileArray':'([BLjava/lang/String;Ljava/util/List;)[B','withCopiedValue':'([BLjava/lang/String;[BLjava/lang/String;)[B'},
'LocalResourceCatalog':{'heroes':'Ljava/util/Map;','items':'Ljava/util/Map;','treasures':'Ljava/util/Map;'},
'LocalResourceCatalog$Hero':{'files':'I'},
'LocalResourceEngine$Result':{'profile':'[B'},
'LocalDrawEngine':{'q7OriginalTutorialCard':'(I)[B','reveal':'(Lcom/project7/localmanager/LocalResourceEngine$Result;Lcom/project7/localmanager/LocalResourceCatalog;[B)[B'}}

def verify():
 jar=ROOT/'analysis/project7/draw-policy-hook-v1/manager-translated-frames.jar';javap=ROOT/'toolchains/java/jdk-17.0.21+9/Contents/Home/bin/javap';checks=[]
 for cls,members in EXPECTED.items():
  text=subprocess.run([str(javap),'-p','-s','-classpath',str(jar),'com.project7.localmanager.'+cls],check=True,capture_output=True,text=True).stdout.splitlines()
  for name,desc in members.items():
   found=[]
   for i,line in enumerate(text):
    if re.search(r'\b'+re.escape(name)+r'(?:\(|;)',line):
     if i+1<len(text) and text[i+1].strip().startswith('descriptor:'):found.append(text[i+1].strip()[12:])
   if desc not in found:raise AssertionError((cls,name,desc,found))
   checks.append({'class':cls,'member':name,'descriptor':desc})
 return {'checks':len(checks),'members':checks,'scope':'compile ABI declarations only; no original implementation copied; synthetic bridge represented by compile-only declaration'}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
