# -*- coding: utf-8 -*-
"""Convert each GLB into a self-contained glTF JSON with data: URIs.

WHY THIS EXISTS. Reported from another machine: on the published artifact the
asset viewers were empty and the walkable world's models arrived UNPAINTED.
Those two symptoms share one cause.

three.js does not read a GLB's embedded textures directly. For an image stored
in a bufferView it builds a Blob and hands itself a `blob:` URL
(GLTFParser.loadImageSource). model-viewer sits on the same loader, and I was
additionally handing model-viewer a `blob:` src of my own. So:

    blob: blocked  ->  mesh still parses, every texture fails  ->  grey models
    blob: blocked  ->  model-viewer's own src fails            ->  empty viewers

Exactly what was reported. The fix is to stop producing blob URLs at all:
store the buffer and every image as `data:` URIs, which the artifact docs
explicitly sanction, and let the loader resolve them in place.

Images move out of the binary buffer, so their bufferViews are dropped and
every surviving bufferView is renumbered - accessors index bufferViews by
position, and leaving a stale index is how you get a mesh that loads as
garbage. Without the compaction step the texture bytes would simply exist
twice and the file would roughly double.
"""
import base64, json, os, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, 'tools'))
from shrink_glb import read_glb  # noqa: E402


def convert(src, dst):
    gltf, blob = read_glb(src)
    views = gltf.get('bufferViews', [])

    # 1. Pull every image out of the binary and into a data: URI.
    image_views = set()
    for img in gltf.get('images', []):
        bv = img.get('bufferView')
        if bv is None:
            continue
        v = views[bv]
        o, n = v.get('byteOffset', 0), v['byteLength']
        mime = img.get('mimeType', 'image/jpeg')
        img['uri'] = 'data:%s;base64,%s' % (
            mime, base64.b64encode(blob[o:o + n]).decode('ascii'))
        img.pop('bufferView', None)
        image_views.add(bv)

    # 2. Compact the remaining bufferViews and record the renumbering.
    keep, remap, out = [], {}, bytearray()
    for i, v in enumerate(views):
        if i in image_views:
            continue
        o, n = v.get('byteOffset', 0), v['byteLength']
        while len(out) % 4:
            out.append(0)
        nv = dict(v)
        nv['byteOffset'] = len(out)
        nv['byteLength'] = n
        remap[i] = len(keep)
        keep.append(nv)
        out += blob[o:o + n]

    # 3. Repoint everything that indexes a bufferView by position.
    for acc in gltf.get('accessors', []):
        if 'bufferView' in acc:
            acc['bufferView'] = remap[acc['bufferView']]
        sp = acc.get('sparse')
        if sp:
            for part in ('indices', 'values'):
                if part in sp and 'bufferView' in sp[part]:
                    sp[part]['bufferView'] = remap[sp[part]['bufferView']]
    # Draco / meshopt would also carry bufferView indices; none of these assets
    # use them, and a silent wrong index is worse than a loud stop.
    for mesh in gltf.get('meshes', []):
        for prim in mesh.get('primitives', []):
            ext = prim.get('extensions', {})
            if 'KHR_draco_mesh_compression' in ext:
                raise SystemExit('Draco compression in %s - not handled' % src)

    gltf['bufferViews'] = keep
    gltf['buffers'] = [{
        'byteLength': len(out),
        'uri': 'data:application/octet-stream;base64,' +
               base64.b64encode(bytes(out)).decode('ascii')}]

    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(gltf, f, separators=(',', ':'))


if __name__ == '__main__':
    srcdir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'models3d_web')
    dstdir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'models3d_gltf')
    os.makedirs(dstdir, exist_ok=True)
    tot = 0
    for f in sorted(os.listdir(srcdir)):
        if not f.endswith('.glb'):
            continue
        d = os.path.join(dstdir, f[:-4] + '.json')
        convert(os.path.join(srcdir, f), d)
        tot += os.path.getsize(d)
        print('%-26s %5.2f MB' % (f[:-4] + '.json', os.path.getsize(d) / 1048576))
    print('total %.1f MB' % (tot / 1048576))
