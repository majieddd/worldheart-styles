# -*- coding: utf-8 -*-
"""Emit styles.html - the three-direction comparison board.

Deliberately a SEPARATE page from gallery.html. gallery.html is 164 plates
across twelve directions and exists to explore; this one holds three directions
and exists to DECIDE between them, so it is built the other way round: the
comparison matrix is the first thing on the page, not a feature buried in a
filter.

Rows are the six game moments, columns are the three styles. Beat and world are
held identical across a row, so a column can only win on its look.
"""
import json, os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STYLES = [
 ('retroanime', '#d98ba6', 'Soft painted cel',
  'A hand-painted 1980s anime film cel. Every edge is a change of flat colour and one hard '
  'shadow terminator — no contour anywhere. Airbrushed sky gradients, muted print-warm '
  'palette, 35mm grain over the frame.',
  ['#c8593f', '#f0a65c', '#8e4633', '#4a2118']),
 ('inkcel', '#f0e6d8', 'Inked cel · the Borderlands read',
  'Cel fills under a thick black contour of even uniform weight, interior edges inked too, '
  'cross-hatch in the shadows, faceted low-polygon forms. The most game-like of the three.',
  ['#3f6ea8', '#9fd0e8', '#8a5a3c', '#1c1a17']),
 ('inkline', '#e05a3c', 'Printed comic panel',
  'Ink on newsprint. Brush contours that swell and taper, all shading carried by visible '
  'benday halftone dots, a limited three-ink screenprint palette, slight registration offset.',
  ['#e05a3c', '#e8ddc8', '#2b3a52', '#c8a44e']),
]

SHOTS = [
 ('towerline',    'Tower line', 'Three towers on a ridge, range circles drawn on the ground.'),
 ('waveincoming', 'Wave incoming', 'The horizon going dark with the swarm; the warning arc.'),
 ('clash',        'The clash', 'Impact on the defence line — muzzle flash, thrown debris.'),
 ('buildgrid',    'Build mode', 'Placement grid, ghosted tower preview, unlettered tile row.'),
 ('boss',         'Titan', 'A mountain-sized invader over the battlefield.'),
 ('orbit',        'Orbit', 'The planet limb, a satellite ring, a second world beyond.'),
]

ASSETS = [('commander', 'Commander'), ('enemy', 'Invader'), ('tower', 'Defence tower')]

CSS = """
:root{
  --ink:#14110e; --ink2:#1c1815; --line:#2e2822; --line2:#3d352c;
  --fg:#efe9e0; --fg2:#a89e91; --fg3:#6f665c; --amber:#e0913a;
  --display:"Archivo",ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  --pad:clamp(16px,3vw,34px);
}
*{box-sizing:border-box}
body{margin:0;background:var(--ink);color:var(--fg);font:14px/1.55 var(--display);
  -webkit-font-smoothing:antialiased;text-wrap:pretty}
.wrap{padding-block:var(--pad);padding-left:var(--pad);padding-right:var(--pad);
  max-width:2000px;margin:0 auto}
header{border-bottom:1px solid var(--line);padding-bottom:22px;margin-bottom:26px}
h1{font-size:clamp(23px,3.6vw,40px);letter-spacing:.14em;margin:0;font-weight:600;
   text-transform:uppercase}
h1 span{color:var(--amber)}
.sub{color:var(--fg2);margin-top:9px;max-width:72ch;font-size:13.5px}
.sub b{color:var(--fg);font-weight:600}
.back{display:inline-block;margin-top:14px;font-family:var(--mono);font-size:12px;
  color:var(--fg2);text-decoration:none;border-bottom:1px solid var(--line2)}
.back:hover{color:var(--amber)}

h2{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:var(--fg3);
  margin:0 0 4px;font-weight:600}
.lede{color:var(--fg2);max-width:80ch;margin:0 0 18px;font-size:13px}

/* ---- comparison matrix ---- */
.matrix{display:grid;grid-template-columns:150px repeat(3,minmax(0,1fr));gap:10px;
  align-items:start}
.matrix .colhead{position:sticky;top:0;z-index:2;background:var(--ink);
  padding:8px 0 10px;border-bottom:1px solid var(--line)}
.matrix .colhead h3{margin:0;font-size:14px;letter-spacing:.09em;text-transform:uppercase;
  display:flex;align-items:center;gap:8px;font-weight:600}
.matrix .colhead i{width:10px;height:10px;border-radius:50%;flex:none}
.matrix .colhead p{margin:4px 0 0;font-size:11.5px;color:var(--fg3);font-family:var(--mono)}
.rowhead{padding-top:6px}
.rowhead b{display:block;font-size:13px;letter-spacing:.04em}
.rowhead span{display:block;color:var(--fg3);font-size:11.5px;margin-top:3px}
.cell{margin:0;border:1px solid var(--line);background:var(--ink2);cursor:zoom-in;
  overflow:hidden;transition:border-color .12s}
.cell:hover{border-color:var(--line2)}
.cell img{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;background:#0d0b09}

/* ---- per-style band ---- */
.band{margin-top:46px;border-top:1px solid var(--line);padding-top:24px}
.bandhead{display:flex;gap:16px;align-items:flex-start;flex-wrap:wrap;margin-bottom:18px}
.bandhead h3{margin:0;font-size:19px;letter-spacing:.1em;text-transform:uppercase;
  display:flex;align-items:center;gap:9px;font-weight:600}
.bandhead h3 i{width:12px;height:12px;border-radius:50%;flex:none}
.bandhead .desc{flex:1 1 400px;min-width:0;color:var(--fg2);font-size:13px;margin:0}
.sw{display:flex;gap:5px;margin-top:8px}
.sw span{width:26px;height:14px;border:1px solid rgba(255,255,255,.14)}
.walk{font-family:var(--mono);font-size:12.5px;text-decoration:none;color:var(--fg);
  border:1px solid var(--amber);padding:9px 16px;border-radius:2px;white-space:nowrap;
  background:#2a231b}
.walk:hover{background:#3a2f22}
.row3{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr));
  margin-bottom:14px}
.asset{border:1px solid var(--line);background:#26231f;padding:10px;text-align:center}
.asset img{display:block;width:100%;aspect-ratio:1;object-fit:contain}
.asset model-viewer{width:100%;aspect-ratio:1;background:#26231f;--poster-color:transparent}
.asset b{display:block;margin-top:7px;font-size:11.5px;font-family:var(--mono);color:var(--fg2)}
.tag{font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--fg3);
  margin:16px 0 8px;font-weight:600}
.miss{display:grid;place-items:center;aspect-ratio:1;color:var(--fg3);font-family:var(--mono);
  font-size:11.5px;border:1px dashed var(--line2);padding:12px;text-align:center}

dialog{border:0;padding:0;background:transparent;max-width:none;max-height:none;
  width:100%;height:100%}
dialog::backdrop{background:#0a0807ee}
.lb{display:flex;align-items:center;justify-content:center;height:100%;padding:16px;
  position:relative}
.lb img{max-width:100%;max-height:100%;object-fit:contain}
.lb .x{position:absolute;top:14px;right:16px}
.lb .cap{position:absolute;bottom:14px;left:16px;font-family:var(--mono);font-size:12px;
  color:var(--fg2);background:rgba(14,12,11,.8);padding:6px 11px;border:1px solid var(--line)}
.chip{background:var(--ink2);border:1px solid var(--line);color:var(--fg2);
  padding:6px 12px;border-radius:2px;cursor:pointer;font:inherit;font-size:12.5px;
  font-family:var(--mono)}
.chip:hover{color:var(--fg);border-color:var(--line2)}
@media(max-width:820px){
  .matrix{grid-template-columns:1fr}
  .matrix .colhead{position:static}
  .rowhead{margin-top:18px}
}
"""


def build():
    have3d = {}
    d3 = os.path.join(HERE, 'models3d_gltf')
    if os.path.isdir(d3):
        for f in os.listdir(d3):
            if f.endswith('.json'):
                have3d[f[:-5]] = 'models3d_gltf/' + f

    # ---- matrix ----
    cols = ''.join(
        '<div class="colhead"><h3><i style="background:%s"></i>%s</h3><p>%s</p></div>'
        % (hue, key, short) for key, hue, short, _desc, _pal in STYLES)
    rows = ''
    for skey, title, note in SHOTS:
        rows += '<div class="rowhead"><b>%s</b><span>%s</span></div>' % (title, note)
        for key, _hue, _short, _d, _p in STYLES:
            f = 'hf/shots/%s_%s.webp' % (key, skey)
            rows += ('<figure class="cell" data-src="%s" data-cap="%s &middot; %s">'
                     '<img loading="lazy" src="%s" alt="%s %s"></figure>'
                     % (f, key, title, f, key, title))

    # ---- per-style bands ----
    bands = ''
    for key, hue, short, desc, pal in STYLES:
        sw = ''.join('<span style="background:%s"></span>' % c for c in pal)
        posters = ''
        for akey, alabel in ASSETS:
            posters += ('<div class="asset"><img loading="lazy" src="hf/posters/%s_%s.webp" '
                        'alt="%s %s"><b>%s</b></div>' % (key, akey, key, akey, alabel))
        models = ''
        for akey, alabel in ASSETS:
            src = have3d.get('%s_%s' % (key, akey))
            if src:
                models += ('<div class="asset"><model-viewer src="%s" camera-controls '
                           'auto-rotate touch-action="pan-y" '
                           'exposure="0.72" tone-mapping="neutral" shadow-intensity="0.35" '
                           'shadow-softness="1" interaction-prompt="none" loading="eager" '
                           'reveal="auto"></model-viewer>'
                           '<b>%s</b></div>' % (src, alabel))
            else:
                models += ('<div class="asset"><div class="miss">%s not built yet<br>'
                           'run fetch_models &rarr; shrink_glb &rarr; glb_to_json'
                           '</div><b>%s</b></div>' % (key + '_' + akey, alabel))
        bands += """
<section class="band" id="%s">
  <div class="bandhead">
    <div><h3><i style="background:%s"></i>%s</h3><div class="sw">%s</div></div>
    <p class="desc">%s</p>
    <a class="walk" href="world.html?style=%s">Walk this world &rarr;</a>
  </div>
  <div class="tag">Style posters &mdash; the source the 3D was built from</div>
  <div class="row3">%s</div>
  <div class="tag">3D assets &mdash; drag to rotate</div>
  <div class="row3">%s</div>
</section>""" % (key, hue, short, sw, desc, key, posters, models)

    html = """<title>WorldHeart Style Trials</title>
<meta charset="utf-8">
<meta name="robots" content="noindex,nofollow">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<script type="module" src="https://cdn.jsdelivr.net/npm/@google/model-viewer@3.5.0/dist/model-viewer.min.js"></script>
<style>%s</style>
<div class="wrap">
<header>
  <h1>WorldHeart <span>Style Trials</span></h1>
  <p class="sub">Three art directions carried all the way through: <b>18 in-game screenshots</b>
  (Higgsfield GPT&nbsp;Image&nbsp;2.5, style-referenced to the local Krea&nbsp;2 plates),
  <b>9 style posters</b>, <b>9 3D assets</b> built from those posters, and
  <b>3 walkable environments</b>. The same six game moments are rendered in each style, so a
  column can only win on how it looks.</p>
  <a class="back" href="gallery.html">&larr; the 164-plate concept board</a>
</header>

<h2>The comparison</h2>
<p class="lede">Same moment, same world, three looks. Click any frame to enlarge.</p>
<div class="matrix">
  <div></div>%s
  %s
</div>

%s
</div>

<dialog id="lb"><div class="lb">
  <img id="lbimg" alt="">
  <form method="dialog" class="x"><button class="chip">close</button></form>
  <div class="cap" id="lbcap"></div>
</div></dialog>

<script>
// The meshes are plain glTF JSON with data: URIs inside, so model-viewer loads
// each one straight from its own src. The previous version fetched JSON, decoded
// base64 and handed model-viewer a `blob:` URL -- which produced empty viewers
// wherever blob: is blocked, and unpainted models in the walkable scene for the
// same reason. Nothing here creates a blob.
//
// Failures are shown ON THE PAGE rather than only in the console: this page is
// read on machines I cannot open a devtools window on.
document.querySelectorAll('model-viewer[src]').forEach(mv=>{
  mv.addEventListener('error',ev=>{
    const d=document.createElement('div');
    d.className='miss';
    d.textContent='3D asset failed to load — '+((ev.detail&&ev.detail.type)||'unknown');
    mv.replaceWith(d);
  });
});

const lb=document.getElementById('lb');
document.addEventListener('click',e=>{
  const f=e.target.closest('.cell');
  if(!f)return;
  document.getElementById('lbimg').src=f.dataset.src;
  document.getElementById('lbcap').innerHTML=f.dataset.cap;
  lb.showModal();
});
</script>""" % (CSS, cols, rows, bands)

    p = os.path.join(HERE, 'styles.html')
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(html)
    print('wrote %s  (%d 3D assets present, %.0fKB)' % (p, len(have3d), len(html)/1024))


if __name__ == '__main__':
    build()
