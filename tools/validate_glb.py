#!/usr/bin/env python3
"""Independent structural and dimensional validation for generated GLB files."""
import json, struct, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXPECTED={"ash", "cedar", "dawn", "ember", "moss", "night", "plum", "sand"}

def check(path):
    raw=path.read_bytes()
    magic,version,total=struct.unpack_from('<4sII',raw)
    assert magic==b'glTF' and version==2 and total==len(raw)
    n,t=struct.unpack_from('<I4s',raw,12); assert t==b'JSON'
    doc=json.loads(raw[20:20+n]); at=20+n
    bn,bt=struct.unpack_from('<I4s',raw,at); assert bt==b'BIN\0'; blob=raw[at+8:at+8+bn]
    assert len(blob)==bn and len(doc['buffers'])==1 and 'uri' not in doc['buffers'][0]
    positions=[]; tris=0
    for mesh in doc['meshes']:
        for primitive in mesh['primitives']:
            ia=doc['accessors'][primitive['indices']]; tris += ia['count']//3
            pa=doc['accessors'][primitive['attributes']['POSITION']]
            view=doc['bufferViews'][pa['bufferView']]; off=view.get('byteOffset',0)+pa.get('byteOffset',0)
            positions=list(struct.iter_unpack('<fff',blob[off:off+pa['count']*12]))
    lo=[min(v[i] for v in positions) for i in range(3)]; hi=[max(v[i] for v in positions) for i in range(3)]
    assert abs(lo[1])<1e-6 and abs(hi[1]-1.8)<1e-5, (lo,hi)
    assert hi[2] > abs(lo[2]), "+Z must contain the forward toe/nose projection"
    assert all(0<=m['pbrMetallicRoughness']['roughnessFactor']<=1 for m in doc['materials'])
    return {"file":str(path.relative_to(ROOT)),"triangles":tris,"bounds_m":{"min":[round(x,4) for x in lo],"max":[round(x,4) for x in hi]},"materials":len(doc['materials']),"nodes":len(doc['nodes']),"embedded_buffer":True,"animations":len(doc.get('animations',[]))}

result=[check(p) for p in sorted((ROOT/'models').glob('*.glb'))]
assert {Path(item["file"]).stem.removeprefix("mystery_character_") for item in result}==EXPECTED
print(json.dumps({"status":"PASS","files":result},indent=2))
