#!/usr/bin/env python3
"""Bounded, read-only Cocos 3.2 CocoLoader structure extractor (not a renderer)."""
import _bootstrap  # noqa: E402,F401
import argparse, hashlib, json, struct, zlib
from pathlib import Path

class Reader:
 def __init__(self,path):
  b=Path(path).read_bytes(); self.sha=hashlib.sha256(b).hexdigest()
  if len(b)<88: raise ValueError('short header')
  size,compressed,count,self.attr,self.node,self.string=struct.unpack_from('<6I',b,64)
  if size>32_000_000 or compressed!=len(b)-88 or not (count*12<=self.attr<=self.node<=self.string<=size): raise ValueError('header bounds')
  z=zlib.decompressobj(); self.d=z.decompress(b[88:],size+1)+z.flush()
  if not z.eof or z.unused_data or len(self.d)!=size: raise ValueError('zlib bounds')
  self.header=dict(uncompressed=size,compressed=compressed,object_count=count,attribute_offset=self.attr,node_offset=self.node,string_offset=self.string)
  self.desc=[]
  for i in range(count):
   n,name,off=struct.unpack_from('<B3xII',self.d,i*12)
   if self.attr+off+n*8>self.node: raise ValueError('descriptor bounds')
   attrs=[]
   for j in range(n):
    t,s=struct.unpack_from('<B3xI',self.d,self.attr+off+j*8);attrs.append((chr(t),self.str(s)))
   self.desc.append((self.str(name),attrs))
  self.seen=set()
 def str(self,off):
  pos=self.string+off
  if not self.string<=pos<len(self.d): raise ValueError('string bounds')
  end=self.d.find(b'\0',pos)
  if end<0: raise ValueError('unterminated string')
  return self.d[pos:end].decode('utf-8','replace')
 def read(self,off=0,depth=0):
  if depth>250 or off in self.seen or off%16 or not 0<=off<=self.string-self.node-16: raise ValueError('node bounds/cycle')
  self.seen.add(off); obj,att,num,val,child=struct.unpack_from('<hhB3xII',self.d,self.node+off)
  if obj>=0:
   if obj>=len(self.desc): raise ValueError('object index')
   if att>=0:
    if att>=len(self.desc[obj][1]): raise ValueError('attribute index')
    typ,name=self.desc[obj][1][att]
   else: typ,name='O',self.str(val) or self.desc[obj][0]
  elif att<0: typ,name='A',self.str(val)
  else: typ,name=chr(num),self.str(child)
  out={'name':name,'type':typ,'value':self.str(val),'offset':off}
  if typ in ('O','A'):
   if child%16 or child+num*16>self.string-self.node: raise ValueError('child bounds')
   out['children']=[self.read(child+i*16,depth+1) for i in range(num)]
  return out

def field(n,key):
 return next((c for c in n.get('children',[]) if c['name']==key),None)
def widgets(root):
 out=[]
 def walk(n,prefix=''):
  o=field(n,'options'); name=field(o,'name') if o else None; cls=field(n,'classname')
  if not name or not cls: raise ValueError('widget lacks options.name/classname')
  path=prefix+'.'+name['value'] if prefix else name['value']
  out.append({'path':path,'class':cls['value'],'node_offset':n['offset']})
  c=field(n,'children')
  for child in c.get('children',[]) if c else []: walk(child,path)
 walk(field(root,'widgetTree'))
 return out

def main():
 p=argparse.ArgumentParser();p.add_argument('files',nargs='+');args=p.parse_args();out=[]
 for f in args.files:
  r=Reader(f);root=r.read();out.append({'file':f,'sha256':r.sha,'decoded_sha256':hashlib.sha256(r.d).hexdigest(),'header':r.header,'node_graph_count':len(r.seen),'widgets':widgets(root)})
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
