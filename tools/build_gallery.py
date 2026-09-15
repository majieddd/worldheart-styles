# -*- coding: utf-8 -*-
"""Emit gallery.html from out/index.json.

The gallery is not a pretty wall of pictures; it is the REVIEW SHEET from the
catalogue method rendered as UI. The job the owner actually has is "compare one
beat across every direction" and "see whether a direction holds up across its
whole range", so grouping is a first-class mode, not a nice-to-have. A flat grid
cannot answer either question, because every plate looks like competent art on
its own.

Metadata is inlined as JS at build time. file:// blocks fetch(), so a gallery
that loaded index.json at runtime would be a gallery that only works behind a
server, and the owner wants to double-click it.
"""
import json, os, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, 'out')

# Each direction's chip colour is pulled from the palette that direction
# actually owns in catalogue.py, so the filter rail is a legend, not decoration.
DIR_HUE = {
    'elysian': '#9BBF5F', 'ashen': '#8E9AA3', 'voidlight': '#7B6BD6',
    'faceted': '#C4653C', 'toybox': '#E24B4B', 'chrome': '#9FB4C7',
    'retroanime': '#D98BA6', 'cinematic': '#6F8C86', 'clayworld': '#C98F63',
    'earlycgi': '#6FA8C9', 'inkline': '#D8D2C4', 'vinyl': '#E0B33A',
    'inkcel': '#1F1B18',
}

DIR_NOTE = {
    'elysian': 'Genshin-forward. High sun, painterly cumulus, god rays. The centre of the brief.',
    'ashen': 'The grounded end. Overcast broken by one shaft, heavy haze, hard rim.',
    'voidlight': 'Night and deep space. Lit from below by crystal, gas giant overhead.',
    'faceted': 'Low-poly geometry read. Hard low sun, flat planes, long raking shadows.',
    'toybox': 'Vinyl primaries at reduced strength. Any stronger and it stops being a screenshot.',
    'chrome': 'Polished metal and iridescent film, anamorphic flare. The tech register.',
    'retroanime': 'Flat cel light, hard shadow terminators, print warmth.',
    'cinematic': 'Backlit mist, long lens, shallow depth, lifted blacks.',
    'clayworld': 'Handmade clay with visible tool marks under soft studio light.',
    'earlycgi': 'Flat ambient and a hard sky gradient. Early-2000s engine sheen.',
    'inkline': 'Heavy ink contour and printed halftone. The graphic extreme.',
    'vinyl': 'Saturated primary vinyl, hard contact shadow, toy-catalogue punch.',
    'inkcel': ('The owner-directed refinement of retroanime. Cel fills under a heavy black '
               'contour of even weight, cross-hatch in the shadows, the polygon read kept. '
               'Two stacked adapters: retroanime carries the light, the superhero-comic '
               'adapter carries the ink.'),
}

CSS = """
/* Committed single-theme on purpose: this is a lightbox for 144 images, and
   the plates are the only colour source on the page. A light ground would
   wash them and break the contact-sheet read. Every token is declared here on
   bare :root and the body ground is painted explicitly, so the page holds on
   either host theme rather than borrowing one.

   The neutral is a warm near-black, biased toward the amber accent rather
   than a pure grey, and the accent itself is drawn from the game's own
   palette (the ember orange of `shattered`, the warm gold of `verdant`) --
   not the cyan neon that every dark tool page reaches for. */
:root{
  --ink:#14110e; --ink2:#1c1815; --line:#2e2822; --line2:#3d352c;
  --fg:#efe9e0; --fg2:#a89e91; --fg3:#6f665c; --amber:#e0913a;
  --display:"Archivo",ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  --pad:clamp(16px,3vw,34px);
}
*{box-sizing:border-box}
body{margin:0;background:var(--ink);color:var(--fg);
  font:14px/1.5 var(--display);
  -webkit-font-smoothing:antialiased;text-wrap:pretty}
/* Anything that is an identifier, a coordinate or a measurement is set in the
   mono face: plate keys, seeds, counts and prompts are data the reader compares
   down a column, not prose. */
.count,figcaption .k,figcaption .p,.chip b,.lb h4,.lb dd,.lb pre{font-family:var(--mono)}
.count,.chip b,.ghead .n{font-variant-numeric:tabular-nums}
a{color:inherit}
.wrap{padding-block:var(--pad);padding-left:var(--pad);padding-right:var(--pad);
  max-width:2100px;margin:0 auto}

/* ---- masthead ---- */
header{border-bottom:1px solid var(--line);padding-bottom:22px;margin-bottom:22px}
h1{font-size:clamp(23px,3.6vw,40px);letter-spacing:.14em;margin:0;font-weight:600;
   text-transform:uppercase}
h1 span{color:var(--amber)}
.sub{color:var(--fg2);margin-top:9px;max-width:66ch;font-size:13.5px}
.sub b{color:var(--fg);font-weight:600}

/* ---- controls ---- */
.bar{display:flex;flex-wrap:wrap;gap:9px;align-items:center;margin:16px 0 6px}
.bar h2{font-size:10.5px;letter-spacing:.17em;text-transform:uppercase;
  color:var(--fg3);margin:0 6px 0 0;min-width:74px;font-weight:600}
.chip{background:var(--ink2);border:1px solid var(--line);color:var(--fg2);
  padding:5px 11px;border-radius:2px;cursor:pointer;font-size:12.5px;
  display:inline-flex;align-items:center;gap:7px;font-family:inherit;
  transition:border-color .12s,color .12s,background .12s}
.chip:hover{border-color:var(--line2);color:var(--fg)}
.chip[aria-pressed=true]{background:#2a231b;border-color:var(--amber);color:var(--fg)}
.chip i{width:8px;height:8px;border-radius:50%;display:block;flex:none}
.chip b{color:var(--fg3);font-weight:500;font-variant-numeric:tabular-nums}
.chip[aria-pressed=true] b{color:var(--amber)}
input[type=search]{background:var(--ink2);border:1px solid var(--line);color:var(--fg);
  padding:6px 11px;border-radius:2px;font:inherit;font-size:12.5px;min-width:190px}
input[type=search]:focus{outline:none;border-color:var(--amber)}
.count{color:var(--fg3);font-size:12px;margin-left:auto;font-variant-numeric:tabular-nums}

/* ---- grid ---- */
.group{margin:34px 0 0}
.ghead{display:flex;align-items:baseline;gap:13px;border-bottom:1px solid var(--line);
  padding-bottom:8px;margin-bottom:15px;flex-wrap:wrap}
.ghead h3{margin:0;font-size:15px;letter-spacing:.09em;text-transform:uppercase;font-weight:600}
.ghead .n{color:var(--fg3);font-size:12px;font-variant-numeric:tabular-nums}
.ghead p{margin:0;color:var(--fg2);font-size:12.5px;flex:1 1 340px;min-width:0}
.grid{display:grid;gap:13px;
  grid-template-columns:repeat(auto-fill,minmax(min(100%,330px),1fr))}
figure{margin:0;background:var(--ink2);border:1px solid var(--line);position:relative;
  cursor:zoom-in;overflow:hidden;transition:border-color .12s}
figure:hover{border-color:var(--line2)}
figure img{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;
  background:#0d0b09}
figcaption{padding:8px 10px 9px;display:flex;gap:8px;align-items:center;
  font-size:11.5px;color:var(--fg2);border-top:1px solid var(--line)}
figcaption i{width:7px;height:7px;border-radius:50%;flex:none}
figcaption .k{color:var(--fg);letter-spacing:.02em}
figcaption .p{color:var(--fg3);margin-left:auto;white-space:nowrap}

/* ---- lightbox ---- */
dialog{border:0;padding:0;background:transparent;max-width:none;max-height:none;
  width:100%;height:100%}
dialog::backdrop{background:#0a0807ee}
.lb{display:grid;grid-template-columns:minmax(0,1fr) 340px;height:100%;
  background:var(--ink);border:1px solid var(--line2)}
.lb .fig{display:flex;align-items:center;justify-content:center;background:#0a0807;
  min-width:0;padding:14px}
.lb .fig img{max-width:100%;max-height:100%;object-fit:contain}
.lb aside{border-left:1px solid var(--line);padding:19px;overflow:auto;min-width:0}
.lb h4{margin:0 0 3px;font-size:15px;letter-spacing:.05em;word-break:break-word}
.lb .coord{color:var(--fg2);font-size:12px;margin-bottom:17px;display:flex;
  gap:7px;align-items:center;flex-wrap:wrap}
.lb dl{margin:0 0 16px;display:grid;grid-template-columns:auto 1fr;gap:5px 13px;font-size:12.5px}
.lb dt{color:var(--fg3);text-transform:uppercase;font-size:10px;letter-spacing:.11em;
  padding-top:2px}
.lb dd{margin:0;color:var(--fg);word-break:break-word}
.lb .ref{color:var(--fg2);font-style:italic}
.lb pre{background:var(--ink2);border:1px solid var(--line);padding:11px;
  font:11.5px/1.62 ui-monospace,SFMono-Regular,Menlo,monospace;white-space:pre-wrap;
  color:var(--fg2);margin:0 0 9px;max-height:32vh;overflow:auto}
.lb .acts{display:flex;gap:8px;flex-wrap:wrap}
.nav{position:absolute;top:12px;right:14px;display:flex;gap:8px}
@media(max-width:900px){
  .lb{grid-template-columns:1fr;grid-template-rows:minmax(0,1fr) auto}
  .lb aside{border-left:0;border-top:1px solid var(--line);max-height:46vh}
}

/* ---- research strip ---- */
.research{margin-top:46px;border-top:1px solid var(--line);padding-top:24px}
.research h3{font-size:12px;letter-spacing:.17em;text-transform:uppercase;
  color:var(--fg3);margin:0 0 5px;font-weight:600}
.research p{color:var(--fg2);max-width:80ch;margin:0 0 15px;font-size:13px}
.research figure{cursor:zoom-in}
.research img{aspect-ratio:auto}
.rgrid{display:grid;gap:13px;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr))}
.empty{color:var(--fg3);padding:50px 0;text-align:center}
"""

JS = """
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const F={direction:new Set(),beat:new Set(),place:new Set()};
let mode='direction', q='', view=[];

function visible(){
  return DATA.filter(d=>
    (!F.direction.size||F.direction.has(d.direction))&&
    (!F.beat.size||F.beat.has(d.beat))&&
    (!F.place.size||F.place.has(d.place))&&
    (!q||(d.key+' '+d.prompt).toLowerCase().includes(q)));
}
function card(d,i){
  return `<figure data-i="${i}"><img loading="lazy" src="out/${d.key}.webp" alt="${d.key}">
    <figcaption><i style="background:${HUE[d.direction]}"></i>
    <span class="k">${d.beat}</span><span>&middot; ${d.place}</span>
    <span class="p">${d.direction}</span></figcaption></figure>`;
}
function render(){
  view=visible();
  $('.count').textContent=view.length+' / '+DATA.length+' plates';
  const host=$('#plates');
  if(!view.length){host.innerHTML='<div class="empty">No plates match these filters.</div>';return;}
  if(mode==='flat'){
    host.innerHTML='<div class="grid">'+view.map(card).join('')+'</div>';
  }else{
    const keys=[...new Set(view.map(d=>d[mode]))].sort();
    host.innerHTML=keys.map(k=>{
      const rows=view.map((d,i)=>[d,i]).filter(([d])=>d[mode]===k);
      const note=(mode==='direction'&&NOTE[k])?`<p>${NOTE[k]}</p>`:
                 (mode==='place'&&REF[k])?`<p>${REF[k]}</p>`:'';
      const dot=mode==='direction'?`<i style="background:${HUE[k]};width:9px;height:9px;border-radius:50%;display:inline-block"></i> `:'';
      return `<section class="group"><div class="ghead"><h3>${dot}${k}</h3>
        <span class="n">${rows.length}</span>${note}</div>
        <div class="grid">${rows.map(([d,i])=>card(d,i)).join('')}</div></section>`;
    }).join('');
  }
}
function chips(){
  for(const dim of ['direction','beat','place']){
    const n={}; DATA.forEach(d=>n[d[dim]]=(n[d[dim]]||0)+1);
    $('#f-'+dim).innerHTML=Object.keys(n).sort().map(v=>
      `<button class="chip" aria-pressed="false" data-dim="${dim}" data-v="${v}">`+
      (dim==='direction'?`<i style="background:${HUE[v]}"></i>`:'')+
      `${v}<b>${n[v]}</b></button>`).join('');
  }
}
document.addEventListener('click',e=>{
  const c=e.target.closest('.chip[data-dim]');
  if(c){const{dim,v}=c.dataset;const on=c.getAttribute('aria-pressed')==='true';
    on?F[dim].delete(v):F[dim].add(v);c.setAttribute('aria-pressed',!on);render();return;}
  const m=e.target.closest('.chip[data-mode]');
  if(m){mode=m.dataset.mode;$$('.chip[data-mode]').forEach(x=>
    x.setAttribute('aria-pressed',x===m));render();return;}
  const f=e.target.closest('#plates figure');
  if(f){open(+f.dataset.i);return;}
  const r=e.target.closest('.research figure');
  if(r){const d=$('#sheet');$('#sheetimg').src=r.dataset.src;d.showModal();}
});
let cur=0;
function open(i){
  cur=i; const d=view[i];
  $('#lbimg').src='out/'+d.key+'.webp'; $('#lbimg').alt=d.key;
  $('#lbkey').textContent=d.key;
  $('#lbcoord').innerHTML=`<i style="width:9px;height:9px;border-radius:50%;background:${HUE[d.direction]};display:inline-block"></i> `+
    `${d.beat} &middot; ${d.place} &middot; ${d.direction} <span style="color:var(--fg3)">&nbsp;${i+1} of ${view.length}</span>`;
  $('#lbref').textContent=d.ref;
  // No ^/$ anchors: a direction may stack two adapters and the field is then
  // "k2_a.safetensors + k2_b.safetensors", where anchored strips leave a mess.
  $('#lblora').textContent=d.lora.replace(/k2_|\\.safetensors/g,'')+'  @  '+d.lora_strength;
  $('#lbseed').textContent=d.seed;
  $('#lbprompt').textContent=d.prompt;
  $('#lb').showModal();
}
function step(n){ if(view.length) open((cur+n+view.length)%view.length); }
addEventListener('keydown',e=>{
  if(!$('#lb').open)return;
  if(e.key==='ArrowRight'){e.preventDefault();step(1)}
  if(e.key==='ArrowLeft'){e.preventDefault();step(-1)}
});
$('#next').onclick=()=>step(1); $('#prev').onclick=()=>step(-1);
$('#copy').onclick=async()=>{ await navigator.clipboard.writeText($('#lbprompt').textContent);
  $('#copy').textContent='copied'; setTimeout(()=>$('#copy').textContent='copy prompt',1200); };
$('#search').oninput=e=>{q=e.target.value.toLowerCase().trim();render()};
$('#clear').onclick=()=>{for(const k in F)F[k].clear();q='';$('#search').value='';
  $$('.chip[data-dim]').forEach(c=>c.setAttribute('aria-pressed','false'));render()};
chips(); render();
"""


def build():
    meta = json.load(open(os.path.join(OUT, 'index.json'), encoding='utf-8'))
    sys.path.insert(0, os.path.join(HERE, 'tools'))
    import catalogue as cat
    data = []
    for key, m in sorted(meta.items()):
        if not os.path.exists(os.path.join(OUT, key + '.webp')):
            continue
        d = dict(m); d['key'] = key
        data.append(d)

    refs = {k: v['ref'] for k, v in cat.PLACES.items()}
    sheets = [('sheet_d.jpg', 'Direction board (probe D)',
               'Five candidate spines, three shots each, so a direction is judged on range '
               'rather than on one flattering frame.'),
              ('sheet_c.jpg', 'Style axis (probe C)',
               'Every LoRA at one strength against a frozen scene. Probe B is not shown: '
               '"stud-topped bricks" put a LEGO baseplate under all nineteen of its plates.'),
              ('sheet_a.jpg', 'Prompt grammar (probe A)',
               'One scene, eight framings. This is where the screenshot register, the grit '
               'ceiling and the unlettered-HUD trick were found.')]
    sheets = [s for s in sheets if os.path.exists(os.path.join(HERE, 'probe', s[0]))]

    html = f"""<title>WorldHeart V2 Concept Board</title>
<meta charset="utf-8">
<meta name="robots" content="noindex,nofollow">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{CSS}</style>
<div class="wrap">
<header>
  <h1>WorldHeart <span>V2</span> &mdash; Concept Board</h1>
  <p class="sub"><b>{len(data)} plates</b>, rendered locally on Krea 2 Turbo (fp8, RTX&nbsp;5090)
  across <b>{len(set(d['beat'] for d in data))} game moments</b>,
  <b>{len(set(d['place'] for d in data))} worlds</b> and
  <b>{len(set(d['direction'] for d in data))} art directions</b>.
  Every prompt is composed from a catalogue row, never hand-typed, so a look can be
  changed once and re-rendered everywhere. Click any plate for its full prompt, seed and LoRA.</p>
</header>

<div class="bar"><h2>Group by</h2>
  <button class="chip" data-mode="direction" aria-pressed="true">art direction</button>
  <button class="chip" data-mode="beat" aria-pressed="false">game moment</button>
  <button class="chip" data-mode="place" aria-pressed="false">world</button>
  <button class="chip" data-mode="flat" aria-pressed="false">no grouping</button>
  <input type="search" id="search" placeholder="search prompts&hellip;">
  <button class="chip" id="clear">reset</button>
  <span class="count"></span>
</div>
<div class="bar"><h2>Direction</h2><span id="f-direction" style="display:contents"></span></div>
<div class="bar"><h2>Moment</h2><span id="f-beat" style="display:contents"></span></div>
<div class="bar"><h2>World</h2><span id="f-place" style="display:contents"></span></div>

<div id="plates"></div>

<section class="research">
  <h3>Research &mdash; what the probes bought</h3>
  <p>Each board below cost a render batch and changed the shipping prompt.
  <b>&ldquo;in-game screenshot from a third-person gameplay camera&rdquo;</b> is what buys gameplay
  framing; without it Krea&nbsp;2 makes a hero portrait every time.
  <b>A named palette plus a named light direction</b> is what buys the Genshin-grade read &mdash;
  not the words &ldquo;Genshin Impact&rdquo;. <b>Grit has a ceiling</b>: one step past the shipping
  strength and the look dies. And <b>HUD renders clean</b> when it is described as a positive
  surface &mdash; &ldquo;plain unlettered icon tiles of solid colour&rdquo; &mdash; with no negation anywhere.</p>
  <div class="rgrid">
    {''.join(f'<figure data-src="probe/{f}"><img loading="lazy" src="probe/{f}" alt="{t}">'
             f'<figcaption><span class="k">{t}</span></figcaption></figure>' for f, t, _ in sheets)}
  </div>
</section>
</div>

<dialog id="lb"><div class="lb">
  <div class="fig"><img id="lbimg" alt=""></div>
  <aside>
    <div class="nav">
      <button class="chip" id="prev">&larr;</button>
      <button class="chip" id="next">&rarr;</button>
      <form method="dialog"><button class="chip">close</button></form>
    </div>
    <h4 id="lbkey"></h4>
    <div class="coord" id="lbcoord"></div>
    <dl>
      <dt>World</dt><dd class="ref" id="lbref"></dd>
      <dt>LoRA</dt><dd id="lblora"></dd>
      <dt>Seed</dt><dd id="lbseed"></dd>
    </dl>
    <pre id="lbprompt"></pre>
    <div class="acts"><button class="chip" id="copy">copy prompt</button></div>
  </aside>
</div></dialog>

<dialog id="sheet"><div class="lb" style="grid-template-columns:1fr">
  <div class="fig" style="position:relative"><img id="sheetimg" alt="">
  <div class="nav"><form method="dialog"><button class="chip">close</button></form></div></div>
</div></dialog>

<script>
const DATA={json.dumps(data)};
const HUE={json.dumps(DIR_HUE)};
const NOTE={json.dumps(DIR_NOTE)};
const REF={json.dumps(refs)};
{JS}
</script>"""
    p = os.path.join(HERE, 'gallery.html')
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(html)
    print('wrote %s  (%d plates, %.0fKB)' % (p, len(data), len(html) / 1024))


if __name__ == '__main__':
    build()
