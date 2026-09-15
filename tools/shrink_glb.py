# -*- coding: utf-8 -*-
"""Re-encode the textures inside a GLB and rewrite it smaller.

Meshy ships each model with a large baked 2048px texture, which is where nearly
all of the 4-7 MB per file lives - the geometry is trivial by comparison. Its
JPEG is near-lossless, so re-encoding at the SAME resolution and q90 halves the
set (44 MB -> 22 MB) while keeping every pixel.

Do not be tempted to downscale. An earlier pass shipped 512px to fit an
artifact size cap, and the models visibly blurred; the cap was the constraint,
not the art.

GLB layout: a 12-byte header, then chunks of [uint32 length][4-char type][data].
Chunk 0 is the JSON manifest, chunk 1 the binary blob. Every accessor,
bufferView and image indexes into that blob by byte offset, so an image cannot
simply be swapped in place - the whole binary chunk is rebuilt by copying each
bufferView in order and rewriting its offset, which keeps every index valid.
"""
import io, json, os, struct, sys

from PIL import Image

# 2048 is what Meshy actually delivers. The first pass shipped 512 to fit an
# artifact size cap that GitHub Pages does not have, and throwing away 94% of
# the texture resolution is exactly why the models read as blurry. Re-encoding
# at 2048/q90 keeps every pixel and is still far smaller than Meshy's own
# near-lossless JPEG.
MAXPX = 2048
QUALITY = 90


def read_glb(path):
    with open(path, 'rb') as f:
        data = f.read()
    magic, ver, total = struct.unpack('<III', data[:12])
    assert magic == 0x46546C67, 'not a GLB: ' + path
    chunks, off = [], 12
    while off < total:
        clen, ctype = struct.unpack('<II', data[off:off + 8])
        chunks.append((ctype, data[off + 8:off + 8 + clen]))
        off += 8 + clen + ((4 - clen % 4) % 4)
    js = next(c for t, c in chunks if t == 0x4E4F534A)
    bins = [c for t, c in chunks if t == 0x004E4942]
    # Strip chunk padding before parsing: the spec pads JSON with spaces, but a
    # sloppy writer may have used nulls, and json.loads rejects either as
    # "Extra data".
    return json.loads(js.rstrip(b'\x00 ').decode('utf-8')), (bins[0] if bins else b'')


def pad4(b, fill=b'\x00'):
    return b + fill * ((4 - len(b) % 4) % 4)


def write_glb(path, gltf, blob):
    # THE JSON CHUNK IS PADDED WITH SPACES, THE BINARY CHUNK WITH ZEROS. That is
    # the spec, not a detail: padding JSON with nulls produces a file whose
    # manifest will not parse in any strict reader, and the first version of
    # this writer did exactly that.
    js = pad4(json.dumps(gltf, separators=(',', ':')).encode('utf-8'), b' ')
    bl = pad4(blob, b'\x00')
    total = 12 + 8 + len(js) + 8 + len(bl)
    with open(path, 'wb') as f:
        f.write(struct.pack('<III', 0x46546C67, 2, total))
        f.write(struct.pack('<II', len(js), 0x4E4F534A)); f.write(js)
        f.write(struct.pack('<II', len(bl), 0x004E4942)); f.write(bl)


def shrink(src, dst):
    gltf, blob = read_glb(src)
    views = gltf.get('bufferViews', [])
    # Which bufferViews hold images, and what the replacement bytes are.
    repl = {}
    for img in gltf.get('images', []):
        bv = img.get('bufferView')
        if bv is None:
            continue
        v = views[bv]
        o, n = v.get('byteOffset', 0), v['byteLength']
        try:
            im = Image.open(io.BytesIO(blob[o:o + n]))
            im = im.convert('RGB')
        except Exception:
            continue
        if max(im.size) > MAXPX:
            k = MAXPX / max(im.size)
            im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))),
                           Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, 'JPEG', quality=QUALITY, optimize=True)
        repl[bv] = buf.getvalue()
        img['mimeType'] = 'image/jpeg'

    # Rebuild the blob so every bufferView stays contiguous and correctly
    # offset. Copying in index order keeps accessors valid without touching them.
    out = bytearray()
    for i, v in enumerate(views):
        o, n = v.get('byteOffset', 0), v['byteLength']
        raw = repl.get(i, blob[o:o + n])
        while len(out) % 4:
            out.append(0)
        v['byteOffset'] = len(out)
        v['byteLength'] = len(raw)
        out += raw
    if gltf.get('buffers'):
        gltf['buffers'][0] = {'byteLength': len(out)}
    write_glb(dst, gltf, bytes(out))


if __name__ == '__main__':
    srcdir = sys.argv[1] if len(sys.argv) > 1 else 'models3d'
    dstdir = sys.argv[2] if len(sys.argv) > 2 else 'models3d_web'
    os.makedirs(dstdir, exist_ok=True)
    b = a = 0
    for f in sorted(os.listdir(srcdir)):
        if not f.endswith('.glb'):
            continue
        s, d = os.path.join(srcdir, f), os.path.join(dstdir, f)
        shrink(s, d)
        b += os.path.getsize(s); a += os.path.getsize(d)
        print('%-24s %5.1f MB -> %4.1f MB' % (f, os.path.getsize(s)/1048576,
                                              os.path.getsize(d)/1048576))
    print('total %.1f MB -> %.1f MB' % (b/1048576, a/1048576))
