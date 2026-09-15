# -*- coding: utf-8 -*-
"""Assemble the GitHub Pages deploy tree in _pages/.

The working directory carries three generations of the same nine meshes (the
44 MB originals, the texture-shrunk GLBs, the superseded base64-in-JSON build)
plus every probe contact sheet. Publishing all of it would put ~140 MB in a
repo to serve ~74 MB of actually-referenced files, so the tree is assembled
explicitly rather than by copying the folder and hoping.

What ships and why:
  *.html            the three boards and the walkable scene
  out/*.webp        the 164 Krea plates the concept board renders
  hf/               the Higgsfield screenshots and style posters
  sky/              the three painted equirectangular sky panoramas
  models3d_gltf/    the meshes the pages actually load (data: URIs, no blob)
  models3d_web/     the same meshes as real .glb, for importing into an engine
  probe/sheet_*.jpg the three research boards gallery.html links to
  tools/, README    how it was all made
"""
import os, shutil, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(HERE, '_pages')

FILES = ['index.html', 'styles.html', 'gallery.html', 'world.html',
         'robots.txt', '.nojekyll', 'README.md', 'direction-approved.md']
GLOBS = [('out', '.webp'), ('hf/shots', '.webp'), ('hf/posters', '.webp'),
         ('sky', '.webp'),
         ('models3d_gltf', '.json'), ('models3d_web', '.glb'), ('tools', None)]
EXTRA = ['out/index.json',
         'probe/sheet_a.jpg', 'probe/sheet_c.jpg', 'probe/sheet_d.jpg',
         'probe/style_index.txt']


def copy(rel):
    src = os.path.join(HERE, rel)
    if not os.path.exists(src):
        print('  skip (missing)', rel); return 0
    dst = os.path.join(SITE, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return os.path.getsize(src)


def _force_rm(func, path, _exc):
    # Git object files are written read-only; on Windows unlink refuses them.
    os.chmod(path, 0o700)
    func(path)


def main():
    # CLEAR THE TREE BUT KEEP .git. _pages is the deploy checkout AND the clone,
    # so an unconditional rmtree deletes the repository along with the files it
    # was about to rebuild -- which is exactly what happened the first time this
    # ran a second time, and it took the history with it.
    os.makedirs(SITE, exist_ok=True)
    for entry in os.listdir(SITE):
        if entry == '.git':
            continue
        p = os.path.join(SITE, entry)
        if os.path.isdir(p):
            shutil.rmtree(p, onerror=_force_rm)
        else:
            os.remove(p)
    total = 0
    for f in FILES:
        total += copy(f)
    for d, ext in GLOBS:
        p = os.path.join(HERE, d)
        if not os.path.isdir(p):
            print('  skip (missing dir)', d); continue
        n = 0
        for f in sorted(os.listdir(p)):
            if ext and not f.endswith(ext):
                continue
            if not ext and not (f.endswith('.py') or f.endswith('.sh')):
                continue
            total += copy(os.path.join(d, f)); n += 1
        print('  %-18s %3d files' % (d, n))
    for f in EXTRA:
        total += copy(f)
    print('\n_pages assembled: %.1f MB' % (total / 1048576))
    # A page that references a file which did not ship is the failure mode this
    # check exists to catch, and it is cheap: every src= the HTML names must
    # exist under _site.
    import re
    missing = []
    for page in ('index.html', 'gallery.html', 'styles.html', 'world.html'):
        p = os.path.join(SITE, page)
        if not os.path.exists(p):
            continue
        html = open(p, encoding='utf-8').read()
        for m in re.findall(r'(?:src|href)="([^"#?:]+\.(?:webp|jpg|png|json|glb|html))"', html):
            # Skip JS template literals like out/${d.key}.webp -- those are
            # built at runtime and are not a static reference to check.
            if '${' in m:
                continue
            if not os.path.exists(os.path.join(SITE, m)):
                missing.append('%s -> %s' % (page, m))
    if missing:
        print('\nMISSING REFERENCED FILES:')
        for m in sorted(set(missing))[:20]:
            print('  ', m)
        sys.exit(1)
    print('every referenced asset is present')


if __name__ == '__main__':
    main()
