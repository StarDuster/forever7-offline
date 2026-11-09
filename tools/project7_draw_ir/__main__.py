"""Export the verified current ordinary-t1 outer graph; no source/code execution.
For maintainer table reconstruction use tools.project7_draw_ir.produce instead.
Other draw types are preserved in public-source-tables, but their default resolver
semantics are not claimed by this entry point.
"""
import argparse
import hashlib
import os
from pathlib import Path
from . import canonical
from .consumer import load, CONTRACT_SHA256


def export():
    ir=load()
    return canonical({'schema':2,'scope':'ordinary-t1-outer-only','t1_contract_sha256':CONTRACT_SHA256,'outer':ir['outer']})+b'\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    data=export()
    with args.output.open('xb') as stream:
        stream.write(data);stream.flush();os.fsync(stream.fileno())
    print(hashlib.sha256(data).hexdigest(),len(data))

if __name__=='__main__':main()
