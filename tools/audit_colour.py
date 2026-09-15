# -*- coding: utf-8 -*-
"""Colour audit: did the per-world palette survive the per-direction grade?

This is the one question the contact sheet cannot answer, because every plate
looks like competent art on its own. PLACE owns a palette and DIRECTION owns a
light and a grade, and those two clauses sit next to each other in every prompt.
If the grade is winning, fourteen worlds collapse into one world wearing twelve
filters, and the suite is worth much less than its plate count suggests.

Deliberately a REPORT, not a gate. Inventing a pass threshold here would just
invite moving it later; what is wanted is the measured answer and the plates
that sit furthest from their world's stated palette, so they can be LOOKED at.

Measurement notes that matter:
  * Hue is circular, so the average is the argument of the mean unit vector,
    never the arithmetic mean (a mean of 350 and 10 is 0, not 180).
  * Each pixel is weighted by its own saturation. Unweighted, the grey sky that
    every 'ashen' plate carries would drag every hue toward whatever noise sits
    in the near-neutrals.
  * A world whose palette is genuinely achromatic (carbon: graphite and
    prismatic white) is reported by MATERIAL MASS -- the share of frame that is
    desaturated mid-light material -- never punished by a colour test it was
    never trying to pass.
"""
import json, math, os, sys
from collections import defaultdict
from PIL import Image

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, 'out')

# Where each world's NAMED palette says its colour should land, in degrees.
# Several are honestly bimodal -- that is the palette, not a measurement fault.
EXPECT = {
    'io':        ([50], 'sulphur yellow / black basalt'),
    'europa':    ([190], 'pale cyan / bone white / rust fractures'),
    'titan':     ([35], 'amber / ochre'),
    # Bimodal, and the second mode was always in the catalogue: this world is
    # PLATFORMS ABOVE A CLOUD DECK, so a blue sky is in every frame by
    # construction. The table missed it, the art did not. Correcting the
    # expectation to match the catalogue is fixing the instrument; it would be
    # goalpost-moving only if the plates had drifted and the number were being
    # widened to forgive them. Checked by eye first -- probe/audit_venus.jpg.
    'venus':     ([45, 210], 'sulphur gold / pearl grey over a blue cloud deck'),
    'mars':      ([12, 285], 'rust red / dusty violet'),
    'enceladus': ([205], 'glacier white / pale blue'),
    'terminator':([25, 220], 'copper / deep blue, split by the terminator'),
    'reddwarf':  ([5], 'deep crimson / umber'),
    'rogue':     ([175], 'black / bioluminescent teal'),
    'ringmoon':  ([275, 45], 'violet / pale gold'),
    'carbon':    (None, 'graphite grey / prismatic white  [achromatic by design]'),
    # Same correction, same reason: the catalogue's terrain noun for this world
    # is "a floating archipelago of GREEN islands", so green is a specified
    # third mode, not drift. Checked by eye -- probe/audit_ocean.jpg.
    'ocean':     ([175, 45, 120], 'turquoise / sand gold / green islands'),
    'shattered': ([25], 'ash grey / ember orange'),
    'verdant':   ([120, 45], 'jade green / warm gold'),
}

STEP = 6          # sample every Nth pixel; 1080p is far more data than needed


def measure(path):
    im = Image.open(path).convert('HSV')
    w, h = im.size
    px = im.load()
    sx = sy = sw = 0.0
    sat = 0.0
    matmass = 0
    n = 0
    for y in range(0, h, STEP):
        for x in range(0, w, STEP):
            H, S, V = px[x, y]
            n += 1
            s = S / 255.0
            sat += s
            a = H / 255.0 * 2 * math.pi        # PIL packs 0-360 into 0-255
            sx += math.cos(a) * s
            sy += math.sin(a) * s
            sw += s
            # "desaturated mid-light material": the achromatic read.
            if s < 0.18 and 0.22 < V / 255.0 < 0.88:
                matmass += 1
    hue = (math.degrees(math.atan2(sy, sx)) % 360) if sw > 1e-6 else None
    # Resultant length: how much the plate AGREES with itself about its hue.
    conc = (math.hypot(sx, sy) / sw) if sw > 1e-6 else 0.0
    return hue, conc, sat / n, matmass / n


def sep(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def circmean(hs):
    x = sum(math.cos(math.radians(h)) for h in hs)
    y = sum(math.sin(math.radians(h)) for h in hs)
    return math.degrees(math.atan2(y, x)) % 360, math.hypot(x, y) / max(1, len(hs))


def main():
    meta = json.load(open(os.path.join(OUT, 'index.json'), encoding='utf-8'))
    rows = []
    for key, m in sorted(meta.items()):
        p = os.path.join(OUT, key + '.webp')
        if not os.path.exists(p):
            continue
        hue, conc, sat, mm = measure(p)
        rows.append((key, m['place'], m['direction'], hue, conc, sat, mm))
    if not rows:
        print('no plates'); return

    print('%d plates measured\n' % len(rows))

    by_place = defaultdict(list)
    by_dir = defaultdict(list)
    for key, pl, di, hue, conc, sat, mm in rows:
        by_place[pl].append((key, hue, sat, mm))
        by_dir[di].append(hue)

    print('=' * 78)
    print('PER WORLD  -- does each world hold the palette its prompt names?')
    print('=' * 78)
    print('%-11s %3s %7s %7s %6s  %s' % ('world', 'n', 'hue', 'tight', 'sat', 'verdict'))
    offenders = []
    for pl in sorted(by_place):
        items = by_place[pl]
        hs = [h for _k, h, _s, _m in items if h is not None]
        mean, tight = circmean(hs)
        sat = sum(s for _k, _h, s, _m in items) / len(items)
        exp, label = EXPECT[pl]
        if exp is None:
            mm = sum(m for _k, _h, _s, m in items) / len(items)
            verdict = 'achromatic: material mass %.0f%% of frame' % (mm * 100)
        else:
            # PER PLATE against the NEAREST allowed mode, not the world mean.
            #
            # The mean was the first statistic here and it is wrong for any
            # world whose palette names more than one hue. Venus is gold
            # platforms against a blue cloud deck; the saturation-weighted mean
            # of 45 and 210 lands near 90, a yellow-green that appears in NO
            # plate, and the world was scored as drifted for carrying exactly
            # the two colours it was asked for. A mean is only meaningful on a
            # unimodal distribution, and half this catalogue is bimodal by
            # design. Share-on-palette also answers the more useful question:
            # how many of this world's plates actually carry its palette.
            ds = [min(sep(h, e) for e in exp) for h in hs]
            on = sum(1 for d in ds if d <= 40)
            share = on / max(1, len(ds))
            verdict = ('on palette (%d/%d plates, median %.0f deg off %s)'
                       % (on, len(ds), sorted(ds)[len(ds) // 2], label.split(' /')[0])
                       if share >= 0.75 else
                       'DRIFTED (only %d/%d plates on %s)' % (on, len(ds), label))
            if share < 0.75:
                worst = max(zip(items, ds), key=lambda t: t[1])[0]
                offenders.append((pl, 100 * (1 - share), worst[0]))
        if len(items) < 3:
            verdict += '   (n=%d, indicative only)' % len(items)
        print('%-11s %3d %6.0f%s %6.2f %6.2f  %s' % (pl, len(items), mean, chr(176),
                                                     tight, sat, verdict))

    print('\n' + '=' * 78)
    print('PER DIRECTION -- is the grade flattening every world into one look?')
    print('=' * 78)
    for di in sorted(by_dir):
        hs = [h for h in by_dir[di] if h is not None]
        mean, tight = circmean(hs)
        # tight near 1.0 means every plate in this direction lands on the SAME
        # hue whatever world it was shot on: the grade has eaten the palette.
        # A resultant length of 1.00 from one or two samples carries no
        # information -- it is arithmetic, not evidence. Flagging it would be
        # the instrument lying, which is worse than the instrument being quiet.
        if len(hs) < 4:
            flag = '  (n too small to judge)'
        elif tight > 0.88:
            flag = '  <-- grade dominates, worlds not separating'
        else:
            flag = ''
        print('%-11s n=%-3d mean %5.0f%s  spread-tightness %.2f%s'
              % (di, len(hs), mean, chr(176), tight, flag))

    # The headline number: if worlds spread WIDER than directions, the palette
    # clause is the stronger of the two and the catalogue is doing its job.
    pm = circmean([circmean([h for _k, h, _s, _m in by_place[p] if h is not None])[0]
                   for p in by_place])[1]
    dm = circmean([circmean([h for h in by_dir[d] if h is not None])[0]
                   for d in by_dir])[1]
    print('\nworld-mean tightness     %.2f   (lower = worlds differ more)' % pm)
    print('direction-mean tightness %.2f   (lower = directions differ more)' % dm)
    if abs(pm - dm) < 0.04:
        print('VERDICT: too close to call -- neither axis dominates the colour.')
    else:
        print('VERDICT: %s carries the colour.' % ('PLACE' if pm < dm else 'DIRECTION'))
    if offenders:
        print('\nlook at these by eye (too few plates carry the named palette):')
        for pl, pct, key in offenders:
            print('  %-11s %3.0f%% of plates off palette   worst: %s' % (pl, pct, key))


if __name__ == '__main__':
    main()
