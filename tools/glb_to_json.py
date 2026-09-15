# -*- coding: utf-8 -*-
"""Wrap each web-sized GLB as base64 inside a JSON file.

Artifact hosting serves only standard web media types, and model/gltf-binary is
not one of them -- a .glb supporting file is refused outright. JSON is served,
so the mesh travels as base64 inside it and the page decodes it to an
ArrayBuffer before handing it to the loader. One code path for both the local
build and the published one, because two would drift.
"""
import base64, json, os, sys

src = sys.argv[1] if len(sys.argv) > 1 else 'models3d_web'
dst = sys.argv[2] if len(sys.argv) > 2 else 'models3d_json'
os.makedirs(dst, exist_ok=True)
tot = 0
for f in sorted(os.listdir(src)):
    if not f.endswith('.glb'):
        continue
    raw = open(os.path.join(src, f), 'rb').read()
    out = os.path.join(dst, f[:-4] + '.json')
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump({'glb': base64.b64encode(raw).decode('ascii')}, fh)
    tot += os.path.getsize(out)
    print('%-26s %5.2f MB' % (f[:-4] + '.json', os.path.getsize(out) / 1048576))
print('total %.1f MB' % (tot / 1048576))
