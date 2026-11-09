"""Inspect fixed readonly history capabilities; does not execute a draw."""
import argparse,json
from .consumer import load,lookup

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--wire',type=int);a=p.parse_args();ir=load()
    if a.wire is None:result=ir['summary']
    else:
        row=lookup(ir,a.wire);result={k:row[k] for k in ['wire_t','epoch_utc','kind','rpc_family','ui','capability','required_generic_seams','issues','runtime_enabled_by_this_component']}
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
