# -*- coding: utf-8 -*-
"""Mutation proof for the colour audit.

The EXPECT table in audit_colour.py was widened for two worlds after looking at
their plates. Seen from outside, that move is indistinguishable from moving the
goalposts until the metric agrees with you. The difference is whether the
widened metric can still FAIL something, so: break passing plates on purpose and
require the audit to reject them.

FIRST VERSION OF THIS FILE WAS WRONG and is worth recording, because the bug is
a general one: it tested a statistic the audit does not use. It rotated ONE
plate and scored that plate against its world's modes, while the audit judges
the world as a whole. A single plate legitimately sits away from its world's
centre, so a rotation could land it near an allowed mode by pure coincidence and
be scored a miss -- and it duly reported that even `io`, whose expectation was
never touched, "accepts mutants". A proof that fails on a world you did not
change is testing the wrong thing.

So the mutation is applied the way the audit reads: rotate EVERY plate of a
world by the same angle and require the audit's own verdict --
SHARE-ON-PALETTE, the fraction of that world's plates within tolerance of some
allowed mode -- to flip from pass to fail. The rotation is chosen per world to
land it in the widest gap between allowed modes, the most favourable break
available. Two outcomes are not failures and must not be counted as such:

  * VACUOUS -- the modes are so spread that no rotation could ever land off
    palette. The expectation is untestable and says so out loud.
  * INCONCLUSIVE -- the audit already rejects that world unbroken, so there is
    no pass to turn into a fail. Blaming the instrument here would be blaming
    it for a finding it got right.

    python tools/mutation_proof.py            # every world with >= 3 plates
    python tools/mutation_proof.py ocean venus
"""
import json, os, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
import audit_colour as A

TOL = 40          # the same tolerance audit_colour calls "on palette"
SAMPLE = 4        # plates per world; the mean is taken over the same set twice


def rotate_hue(src, dst, deg):
    im = Image.open(src).convert('HSV')
    h, s, v = im.split()
    shift = round(deg / 360.0 * 255) % 256
    h = h.point(lambda p: (p + shift) % 256)
    Image.merge('HSV', (h, s, v)).convert('RGB').save(dst, 'WEBP', quality=88)


def best_break(mean, modes):
    """Rotation putting the world mean as far from every allowed mode as it goes."""
    best = (-1, 0)
    for deg in range(5, 360, 5):
        d = min(A.sep((mean + deg) % 360, m) for m in modes)
        if d > best[0]:
            best = (d, deg)
    return best[1], best[0]


def world_hues(paths):
    hs = []
    for p in paths:
        hue, _c, _s, _m = A.measure(p)
        if hue is not None:
            hs.append(hue)
    return hs


def share_on(hs, modes):
    """The statistic the audit actually reports: fraction of plates on a mode.

    The proof must test the audit's own verdict. When the audit moved from a
    world MEAN to share-on-palette, this had to move with it -- a proof that
    exercises a statistic the tool no longer uses proves nothing about the tool.
    """
    if not hs:
        return 0.0
    return sum(1 for h in hs if min(A.sep(h, m) for m in modes) <= TOL) / len(hs)


def main():
    meta = json.load(open(os.path.join(A.OUT, 'index.json'), encoding='utf-8'))
    by_place = {}
    for key, m in meta.items():
        p = os.path.join(A.OUT, key + '.webp')
        if os.path.exists(p):
            by_place.setdefault(m['place'], []).append(p)

    want = sys.argv[1:] or sorted(by_place)
    tmp = tempfile.mkdtemp(prefix='wh_mut_')
    failed = tested = inconclusive = 0
    for place in want:
        modes, _label = A.EXPECT.get(place, (None, ''))
        paths = sorted(by_place.get(place, []))[:SAMPLE]
        if modes is None or len(paths) < 3:
            print('%-11s skipped (achromatic by design, or fewer than 3 plates)' % place)
            continue
        tested += 1
        hs = world_hues(paths)
        s0 = share_on(hs, modes)
        # Break relative to the world's own centre of mass, so the rotation is
        # the most favourable one available rather than an arbitrary angle.
        deg, predicted = best_break(A.circmean(hs)[0], modes)
        if predicted <= TOL:
            print('%-11s !! VACUOUS: modes %s leave no rotation further than %d deg '
                  'from an allowed mode; this world can never fail the hue test'
                  % (place, modes, predicted))
            failed += 1
            continue
        rot = []
        for i, p in enumerate(paths):
            dst = os.path.join(tmp, '%s_%d.webp' % (place, i))
            rotate_hue(p, dst, deg)
            rot.append(dst)
        s1 = share_on(world_hues(rot), modes)
        if s0 < 0.75:
            # The audit already rejects this world unbroken, so breaking it
            # proves nothing about the audit's power -- there is no pass to
            # turn into a fail. INCONCLUSIVE, not FAILED: counting it as a
            # failure would blame the instrument for a finding it got right.
            inconclusive += 1
            print('%-11s -- inconclusive: audit already rejects this world '
                  '(%.0f%% on palette); nothing to break' % (place, s0 * 100))
            continue
        ok = s1 < 0.75
        if not ok:
            failed += 1
        print('%-11s %s  share-on-palette %.0f%% --rotate+%3d--> %.0f%%'
              % (place, 'REJECTS' if ok else '!! ACCEPTS', s0 * 100, deg, s1 * 100))

    print('\n%d worlds tested, %d failed, %d inconclusive'
          % (tested, failed, inconclusive))
    if failed:
        raise SystemExit('MUTATION PROOF FAILED: the audit cannot reject broken worlds')
    print('MUTATION PROOF PASSED: every expectation, widened or not, still '
          'rejects a deliberate hue break')


if __name__ == '__main__':
    main()
