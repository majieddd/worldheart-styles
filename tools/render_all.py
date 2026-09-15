# -*- coding: utf-8 -*-
"""Render the catalogue. Resumable, prompt-aware, safe to kill at any point.

Two properties matter more than speed here:

1. **A resumed run is free.** Every plate is written to out/<key>.webp the
   moment it exists, so an interrupted batch continues by re-issuing the same
   command and nothing already rendered is paid for twice.

2. **A cached plate whose PROMPT has moved is treated as missing.** The cache
   is keyed by KEY and the seed is a function of KEY, which is what makes a
   re-render a restore -- but it also means editing a prompt leaves the old
   image sitting under the same name, and every later run skips it as "already
   done". That failure is silent and invisible, because what comes back is a
   perfectly good picture of the wrong thing. sha1 of the composed prompt is
   recorded beside each plate and disagreement makes the key stale.

Rows are rendered grouped by DIRECTION so the LoRA stays patched across a run
of plates instead of being swapped every image. Order does not touch output:
the seed is FNV-1a of the key, not of the position.
"""
import argparse, hashlib, io, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import krea, catalogue as cat, rows as R
from PIL import Image

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, 'out')
MANIFEST = os.path.join(OUT, '.prompts.json')
META = os.path.join(OUT, 'index.json')

GEN_W, GEN_H = 1920, 1088      # 1088 not 1080: the latent needs the multiple
OUT_W, OUT_H = 1920, 1080      # true 16:9 after a centre crop
QUALITY = 90


def phash(p):
    return hashlib.sha1(p.encode('utf-8')).hexdigest()[:16]


def load(path, default):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def save_atomic(path, obj):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=0, sort_keys=True)
    os.replace(tmp, path)      # a kill cannot truncate the real file


def fit(img):
    """Cover-crop 1088 down to a true 1080. Downsampling is free antialiasing."""
    sc = max(OUT_W / img.width, OUT_H / img.height)
    img = img.resize((round(img.width * sc), round(img.height * sc)), Image.LANCZOS)
    l, t = (img.width - OUT_W) // 2, (img.height - OUT_H) // 2
    return img.crop((l, t, l + OUT_W, t + OUT_H))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default='', help='key prefix filter')
    ap.add_argument('--force', default='', help='re-roll keys with this prefix')
    ap.add_argument('--variant', type=int, default=0, help='different image, same prompt')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--stale', action='store_true', help='report only, render nothing')
    a = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    man = load(MANIFEST, {})
    meta = load(META, {})

    jobs = []
    for row in R.ROWS:
        key = R.key_of(row)
        if not key.startswith(a.only):
            continue
        jobs.append((key, row, cat.compose(*row)))

    if a.force:
        for key, _r, _p in jobs:
            if key.startswith(a.force):
                f = os.path.join(OUT, key + '.webp')
                if os.path.exists(f):
                    os.remove(f)

    todo = []
    for key, row, prompt in jobs:
        f = os.path.join(OUT, key + '.webp')
        missing = not os.path.exists(f)
        stale = man.get(key) != phash(prompt)
        if missing or stale:
            todo.append((key, row, prompt, missing))

    if a.stale:
        print('%d cached plates are STALE, %d MISSING, %d current'
              % (sum(1 for t in todo if not t[3]), sum(1 for t in todo if t[3]),
                 len(jobs) - len(todo)))
        for key, _r, _p, miss in todo[:40]:
            print('  ', 'missing' if miss else 'stale  ', key)
        return

    if a.limit:
        todo = todo[:a.limit]

    # Group by direction: same LoRA stays patched across the run of plates.
    todo.sort(key=lambda t: (t[1][2], t[0]))

    print('%d to render (of %d in the catalogue)' % (len(todo), len(jobs)), flush=True)
    t0 = time.time()
    for i, (key, row, prompt, _miss) in enumerate(todo, 1):
        beat, place, direction = row
        stack = cat.loras_for(direction)
        seed = krea.seed_of(key if not a.variant else key + '#' + str(a.variant))
        t1 = time.time()
        try:
            im, _dt = krea.render(prompt, GEN_W, GEN_H, seed, loras=stack,
                                  prefix='wh/' + key)
        except Exception as e:
            print('  !! %s FAILED: %s' % (key, str(e)[:200]), flush=True)
            continue
        img = Image.open(io.BytesIO(krea.fetch(im))).convert('RGB')
        fit(img).save(os.path.join(OUT, key + '.webp'), 'WEBP',
                      quality=QUALITY, method=6)
        # Record the prompt this plate was ACTUALLY made from, immediately after
        # the plate exists -- an hour-long batch killed at minute fifty must not
        # lose the record of what it already got right.
        man[key] = phash(prompt)
        meta[key] = dict(beat=beat, place=place, direction=direction, prompt=prompt,
                         seed=seed, lora=' + '.join(n for n, _s in stack),
                         lora_strength=' / '.join(str(s) for _n, s in stack),
                         ref=cat.PLACES[place]['ref'])
        save_atomic(MANIFEST, man)
        save_atomic(META, meta)
        el = time.time() - t0
        print('[%3d/%d] %-44s %5.1fs  (elapsed %5.0fs, eta %5.0fs)'
              % (i, len(todo), key, time.time() - t1, el, el / i * (len(todo) - i)),
              flush=True)
    print('done in %.0fs' % (time.time() - t0))


if __name__ == '__main__':
    main()
