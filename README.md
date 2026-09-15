# WorldHeart v2 — concept suite

144 in-game-screenshot concepts for a Roblox-styled, planet-hopping tower
defence game, rendered locally on **Krea 2 Turbo** and served as one HTML board.

Open **`gallery.html`**. Everything else here is how it was made and how to
change it.

---

## What this is for

The brief was a look, not a deliverable: *Roblox geometry, Genshin-grade
rendering, and enough grit that it does not read as pure anime* — explored
widely enough to pick a direction from. So the suite is deliberately **twelve
art directions**, not one, across **28 game moments** and **14 worlds**, plus
two 12-wide lineups where beat and world are held still so the directions can
be compared like for like.

## Layout

```
gallery.html          the board — group by direction / moment / world, click for prompt+seed
direction-approved.md the direction gate: the five-spine board and what each probe bought
tools/
  krea.py             Krea 2 Turbo over the ComfyUI HTTP API
  catalogue.py        the dimension grammar: PLACES x DIRECTIONS x BEATS -> compose()
  rows.py             the 144 shipping rows (curated spread + lineups + top-up)
  render_all.py       resumable, prompt-aware batch renderer
  build_gallery.py    emits gallery.html from out/index.json
  sheet.py            labelled contact sheets
  get_loras.sh        pulls the 18-LoRA probe set from Hugging Face
probe/                probe boards A/C/D and the 1459-name style index
out/                  the plates, plus index.json (metadata) and .prompts.json (staleness)
```

## Running it

ComfyUI must be up (`main.py --port 8188`); `COMFY` overrides the address.

```bash
python tools/render_all.py                 # everything missing or stale
python tools/render_all.py --stale         # report only, render nothing
python tools/render_all.py --only clash_   # one prefix
python tools/render_all.py --force clash_mars_inkline --variant 1   # re-roll one plate
python tools/build_gallery.py              # rebuild the board
```

A batch is safe to kill. Every plate is written the moment it exists, so
re-issuing the same command resumes for free.

## The two invariants

**Prompts are composed, never hand-typed.** One row is `(beat, place,
direction)`; `catalogue.compose()` turns it into the only prompt that plate will
ever see. Changing how a look reads is one edit in one dict, and every plate
that uses it is re-rendered — a hundred-odd format strings could not do that.

**A cached plate whose prompt has moved is treated as missing.** The seed is
FNV-1a of the key, which is what makes a re-render a *restore* rather than a
re-roll — but it also means an edited prompt would leave the stale image sitting
under the same name while every later run skipped it as done. That failure is
silent and invisible: what comes back is a perfectly good picture of the wrong
thing. `sha1(prompt)` is recorded beside each plate, and disagreement makes the
key stale.

## What the probes bought

Each of these cost a render batch and changed the shipping prompt. They are the
reusable part.

1. **`in-game screenshot from a third-person gameplay camera`** buys gameplay
   framing. Without it Krea 2 makes a hero portrait every single time.
2. **`stud-topped bricks` is a poisoned noun.** Added to buy Roblox-ness, it put
   a *LEGO baseplate* under all nineteen plates of probe B and took the whole
   ground plane with it. Modern Roblox is smooth flat-shaded primitives. The fix
   was replacing the noun, never negating it.
3. **A named palette plus a named light direction is what buys the Genshin-grade
   read** — not the phrase "Genshin Impact". Probe C dropped that clause and
   every plate collapsed into a generic Blender render. This is why PLACE owns a
   palette, DIRECTION owns a light, and both are stated before the subject.
4. **Grit has a ceiling.** One step past the shipping strength
   (`heavy atmospheric haze, coarse film grain, grime and soot`) and the look
   dies outright — probe A's a05 buried its own subject.
5. **HUD renders clean as a positive surface.** `plain unlettered icon tiles of
   solid colour` and `a slim curved health arc` produced real interface
   furniture with no garbled lettering. The negation `no text` was never used
   and never needed.
6. **Event beats need event nouns and a motion camera.** `muzzle flashes, thrown
   debris, figures in violent motion` on a close low camera gives combat; drop
   them and the same beat renders a procession.

## Verification

Two instruments, both runnable:

```bash
python tools/audit_colour.py      # does each world hold the palette its prompt names?
python tools/mutation_proof.py    # can that audit still REJECT a deliberately broken world?
```

**`audit_colour.py`** answers the one question a contact sheet cannot, because
every plate looks like competent art on its own: PLACE owns a palette and
DIRECTION owns a grade, and if the grade is winning then fourteen worlds have
collapsed into one world wearing twelve filters. Measured over the suite:

- **PLACE carries the colour** — world-mean tightness `0.17` against
  direction-mean `0.31`. The palette clause is the stronger of the two, which is
  what the catalogue needs. No direction shows grade-dominance.
- **13 of 14 worlds hold their palette.** `carbon` is achromatic by design and
  is scored on material mass (33% of frame), never on a colour test it was not
  trying to pass.
- **`europa` genuinely drifted** — only 3 of 9 plates land on the pale cyan its
  palette names; the world reads mint/celadon instead. The plates are good and
  the ice reads, so they ship as they are, but the finding is real and the fix
  is one word in `catalogue.PLACES` (`pale cyan` → `glacier blue`) plus
  `render_all.py --force survey_europa` etc.

**`mutation_proof.py`** exists because two worlds' expectations were *widened*
after looking at their plates, and from outside that is indistinguishable from
moving goalposts until the metric agrees with you. It rotates the hue of every
plate in a world into the widest gap in its palette and requires the audit's
verdict to flip to fail. Result: **13 worlds tested, 0 failed, 1 inconclusive**
(europa, which the audit already rejects unbroken — nothing to break).

Three things that went wrong building these are worth keeping:

1. **The first mutation proof was wrong, and failed a world I never touched.**
   It rotated one plate and scored it against the world's modes, while the audit
   judges the world as a whole — so a rotation could land a plate near an
   allowed mode by coincidence. A proof that fails on something you did not
   change is testing the wrong thing.
2. **The audit's first statistic was wrong for half the catalogue.** A circular
   mean is only meaningful on a unimodal distribution, and worlds like venus
   (gold platforms against a blue cloud deck) are bimodal by design — the mean
   of 45° and 210° lands near 90°, a yellow-green present in no plate, and
   scored the world as drifted for carrying exactly the two colours it was
   asked for. Share-on-palette replaced it.
3. **Two expectations were corrected, not loosened.** `ocean` gained a green
   mode because the catalogue's own terrain noun says *green islands*; `venus`
   gained a blue one because it is *platforms above a cloud deck*. Both were
   checked by eye first (`probe/audit_ocean.jpg`, `probe/audit_venus.jpg`), and
   the mutation proof re-run afterwards.

## LoRAs

Krea 2 has a real adapter ecosystem and ComfyUI maps its keys natively
(`comfy.utils.krea2_to_diffusers`). Civitai's download API now requires a token,
so everything here comes from Hugging Face, which does not.

The useful find is **`ilkerzgi/fal-Krea-2-Style-LoRAs`** — **1,459 style LoRAs
already in ComfyUI key layout** under its `comfy/` folder. `probe/style_index.txt`
has every name; `tools/get_loras.sh` pulls the 18 chosen here. Swapping a
direction's look is one filename in `catalogue.DIRECTIONS`.

Measured on this machine (RTX 5090 Laptop, 24GB, fp8_scaled, 8 steps, cfg 1.0,
euler/simple): **~23s** per 1920×1088 plate bare, **~31s** with a LoRA patched.
For comparison, the older diffusers NF4 path in `RemoteWorkspace/TowerDefense`
cost ~44s on this card and ~83 *minutes* on a 12GB 4080 — the ComfyUI fp8 route
is the one to use here.

## Roblox IP

The brief asked the style to absorb "all the different IPs from Roblox".
Rendering identifiable third-party Roblox games or characters would be someone
else's IP, so the catalogue takes the platform's **genre vocabulary** instead —
pet-companion, obby/parkour, tycoon conveyor, horror corridor, anime-power
fighter, hover-kart racing, survival-craft, mining — as generic archetypes in
the WorldHeart look. That also answers the more useful question: whether one
style can *host* the platform's whole range.


---

# Style Trials — the three-direction shortlist

A second, separate deliverable: **`styles.html`**. The concept board explores
twelve directions; this one holds the three the owner shortlisted
(`retroanime`, `inkcel`, `inkline`) and exists to decide between them, so the
comparison matrix is the first thing on the page rather than a filter.

Published: https://claude.ai/artifact/H5YmCLGaFj6xV4WGLCLiRv

```
styles.html          the comparison board (matrix + posters + 3D + walk links)
world.html           first-person walkable scene, ?style=retroanime|inkcel|inkline
hf/posters/          9 style posters (3 styles x commander / invader / tower)
hf/shots/            18 in-game screenshots (6 moments x 3 styles)
models3d/            9 GLBs as delivered by Higgsfield (~44 MB)
models3d_web/        the same, textures downscaled (~12.7 MB)
models3d_gltf/       glTF JSON with data: URIs (what the pages actually load)
models3d_json/       superseded: base64 GLB in JSON, needed a blob to use
tools/fetch_models.py    pull the GLBs
tools/shrink_glb.py      re-encode their textures
tools/glb_to_gltf.py     convert to data:-URI glTF so nothing ever needs a blob:
tools/glb_to_json.py     superseded, see above
tools/build_styles_page.py
```

Everything here came from **Higgsfield**: GPT Image 2.5 for the posters and
screenshots (style-referenced to the local Krea 2 plates), Meshy `image_to_3d`
for the meshes. 369 credits.

## Order of operations

Posters first, then 3D, as asked: each mesh is built from that style's poster,
so the 3D inherits the look rather than being a separate guess at it. The
posters are rendered on a transparent background precisely because they are
doing double duty as image-to-3D input.

## What went wrong, and what it cost

1. **All three styles came back looking identical.** GPT Image has a strong
   house style for "game asset" and flattened them into one inked look — the
   retroanime set even had black outlines, the single thing that separates it
   from inkcel. Fixed by pushing the style clauses far apart and, critically,
   removing every ink noun from the retroanime prompt: its edges are now
   specified as *a change of flat colour alone*.
2. **`meshy_v7_image_to_3d` failed all nine jobs instantly**, with no error
   text, on a lowpoly + topology + pose_mode parameter set. `image_to_3d` with
   minimal params runs fine and is what shipped. The failed jobs were not
   charged.
3. **`model/gltf-binary` is not a servable artifact type.** Hence the JSON
   wrapper — the mesh travels as base64 and the page decodes it to a Blob.
4. **Hand-rewriting GLB binary chunks is easy to get subtly wrong.** The first
   `shrink_glb.py` padded the JSON chunk with nulls; the spec says spaces, and
   the result was a file whose own manifest would not parse. Caught by a
   structural check, not by eye.
5. **The outline pass recursed forever.** `toonify` added an inverted-hull mesh
   as a child of each mesh *during* `traverse()`, so traverse walked the hull it
   had just made and gave it a hull. The scene loaded to 100% and then never
   appeared.
6. **IntersectionObserver never fires in the preview renderer.** The lazy mesh
   loader observed nine elements and got zero callbacks with them on screen. A
   trigger that cannot be observed to work cannot be verified, so it was
   replaced with a plain sequential loader.

## Verified

Locally, over http: 9/9 model-viewers report `loaded`, 0 failures; all three
walkable scenes reach "click to walk" with no load errors and render visibly
different worlds. **Not verified:** the published artifact at runtime — the
in-app browser is not signed in to claude.ai, so whether its CSP permits the
same-origin JSON fetch the meshes need is untested. The images and the layout
do not depend on it.


### The blob: bug (reported from a second machine)

On the published artifact the asset viewers came up empty and the walkable
world's models arrived **unpainted**. One cause behind both, and the pair of
symptoms is what identifies it.

three.js never reads a GLB's embedded textures directly. For an image stored in
a bufferView it builds a `Blob` and hands *itself* a `blob:` URL
(`GLTFParser.loadImageSource`). model-viewer sits on the same loader, and I was
separately handing model-viewer a `blob:` src of my own. So where `blob:` is
blocked:

* the mesh still parses and every texture fails &rarr; **grey, unpainted models**
* model-viewer's own src fails &rarr; **empty viewers, nothing to drag**

The fix is not a workaround, it is removing the mechanism: `glb_to_gltf.py`
rewrites each model as plain glTF JSON with its buffer and its texture stored as
`data:` URIs, which the loader resolves in place. Both pages now load a model by
plain URL — no fetch, no base64 decode, no blob anywhere. Verified: 9/9 viewers
loaded, `blobUsed: 0`.

Images move out of the binary buffer, so their bufferViews are dropped and every
surviving one is renumbered; accessors index bufferViews **by position**, and a
stale index there loads as garbage rather than failing loudly. That remap is
checked by the validator in the same script.

Two related lessons kept from this round: the toon ramp floored at 60/255 was
separately crushing the models' painted colour into a 23%-brightness band, and a
toon ramp discards hue entirely wherever the key light does not reach — feeding
the base texture back as an **emissive map** is what keeps the shadowed side
coloured. Neither is a texture problem; both look like one.


### Making the 3D read as the style (not as a filter over it)

Two owner notes drove this round, and both were the same complaint in different
clothes: the styling sat **over** the render instead of **in** it.

**The comic look was a screen overlay.** `inkline`'s halftone was a CSS dot
screen across the viewport, so it stayed pinned to the glass while the world
slid underneath — a filter on the lens, not ink on the object. It is now a
hatch computed from each fragment's **object-space position**, injected into the
toon material's fragment stage via `onBeforeCompile`: two line sets at different
angles, the first fading in through mid shadow and the second crossing it only
in deep shadow, which is how a cross-hatch is actually built up. The lines turn
with the mesh and follow its curvature.

Three things that only show up once you try it:

* **Frequency has to scale per object.** One global frequency gives a 2m
  character a readable five lines across the chest and the 760m terrain lines
  0.4m apart — sub-pixel, so the ground came back with no hatch at all. Each
  material now takes a multiplier.
* **The hatch must fade with distance.** A line fine enough to read at your feet
  is moiré at fifty metres. `1.0 / gl_FragCoord.w` is the view distance and,
  unlike `vViewPosition`, is guaranteed to exist in every fragment stage —
  reaching for that varying is what made the first version fail to compile and
  silently drop the entire terrain out of the scene.
* **Open sunlit ground should carry no ink.** Starting the hatch at 0.74
  luminance striped a lit meadow. Hatching belongs on the shadow side of a form.

**The cel look had no world.** `retroanime` was a red dust plain, which is not
what that style is for. It is now a green valley: a painted gouache sky
panorama generated with Higgsfield and mapped equirectangularly onto the dome,
rolling noise-displaced terrain with height-blended vertex colour, and scattered
low-poly trees. All three styles share that same valley and the same tableau —
only sky, palette, ramp and ink change, so a style can only win on how it looks
rather than on having drawn a nicer location.

### One operational scar

`stage_pages.py` used to `rmtree` its own output directory, which is also the
git checkout it pushes from. The second run deleted the repository along with
the files, and Windows' read-only git objects made it fail halfway. It now
clears everything **except `.git`**, with an `onerror` that chmods read-only
objects. The remote was intact, so the history came back from a re-clone.
