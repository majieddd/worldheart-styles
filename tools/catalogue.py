# -*- coding: utf-8 -*-
"""WorldHeart v2 concept catalogue: every plate is a ROW, never a hand-typed string.

A prompt is COMPOSED, never authored per image:

    PALETTE(place) + REGISTER(fixed) + LIGHT(direction) + SUBJECT(beat x place)
    + MATERIAL(fixed) + FRAME(beat camera) + GRADE(direction) + GRIT(fixed)

That order is the clause-order law and it is also the order of weight. Probe C
proved the first clause is load-bearing: strip the named palette and named light
and every plate collapses into a generic Blender render, whatever else the
sentence says.

Three axes, three different consistency mechanisms, which is the whole point of
keeping them apart:

  PLACE     (where) each derived from a REAL body or a real planetary-science
                    class, and the reference drives what the place is FOR. Owns
                    a palette nobody else owns.
  DIRECTION (how)   owns a LIGHT and a GRADE and one LoRA. This is the axis the
                    brief asks to be explored rather than settled.
  BEAT      (what)  owns a subject template and a CAMERA. Event beats carry
                    event nouns and a motion camera, or they render processions.

Keys are stable; seeds are FNV-1a of the key. A re-render is a restore, not a
re-roll.
"""

# ---------------------------------------------------------------- PLACES ----
# The reference is not decoration: it is what stops fourteen planets reading as
# fourteen rolls of one planet. Each gets a function the reference implies.
PLACES = {
 'io': dict(
    ref='Io: tidally heated, the most volcanic body in the solar system',
    pal='sulphur yellow and black basalt palette',
    ter='sulphur plains split by lava fountains and black basalt shelves',
    sky='a hazy orange sky with a banded giant low on the horizon'),
 'europa': dict(
    ref='Europa: ice shell over a liquid ocean, rust-stained fractures',
    pal='pale cyan and bone white palette with rust-brown fracture lines',
    ter='cracked ice plains scored with pressure ridges and refrozen leads',
    sky='a black star-field sky with a thin blue limb of atmosphere'),
 'titan': dict(
    ref='Titan: thick orange haze, hydrocarbon dunes and methane lakes',
    pal='amber and ochre palette under a sunless orange haze',
    ter='dunes of dark hydrocarbon sand around flat mirror-still methane lakes',
    sky='a thick orange haze ceiling with no visible sun'),
 'venus': dict(
    ref='Venus: the habitable zone is the cloud deck at 50km, not the ground',
    pal='sulphur gold and pearl grey palette',
    ter='tethered platforms floating above an unbroken cloud deck',
    sky='layered yellow cloud ceilings lit from above'),
 'mars': dict(
    ref='Valles Marineris: a canyon system four thousand kilometres long',
    pal='rust red and dusty violet palette',
    ter='a layered sediment canyon four kilometres deep with dust devils on the floor',
    sky='a butterscotch sky with a small pale sun'),
 'enceladus': dict(
    ref='Enceladus: tiger-stripe fissures venting plumes into space',
    pal='glacier white and pale blue palette',
    ter='tiger-stripe fissures venting geyser plumes over fresh snow',
    sky='a black sky with a ring system seen edge-on'),
 'terminator': dict(
    ref='A tidally locked world: all the weather lives on the day-night line',
    pal='copper and deep blue palette split along a terminator line',
    ter='an eternal sunset band between a scorched day side and an ice night side',
    sky='a red sun fixed unmoving on the horizon'),
 'reddwarf': dict(
    ref='A TRAPPIST-1 class world: dim red primary, permanent long shadows',
    pal='deep crimson and umber palette',
    ter='low hardy scrub and wind-carved stone under permanent red light',
    sky='a large dim red sun filling a quarter of the sky'),
 'rogue': dict(
    ref='A rogue planet: no star at all, geothermal heat and life that glows',
    pal='black and bioluminescent teal palette',
    ter='geothermal vents feeding glowing fungal forests in total darkness',
    sky='a starless black sky'),
 'ringmoon': dict(
    ref='A shepherd moon: the primary and its rings dominate the sky',
    pal='violet and pale gold palette',
    ter='dust plains crossed by the hard-edged shadow band of a ring',
    sky='a banded gas giant filling half the sky with its ring cutting across'),
 'carbon': dict(
    ref='A carbon planet: graphite crust, diamond where the pressure allowed',
    pal='graphite grey and prismatic white palette',
    ter='graphite plains studded with diamond outcrops throwing spectra',
    sky='a hard white sun with no atmosphere to soften it'),
 'ocean': dict(
    ref='A global-ocean world: land exists only as an archipelago',
    pal='turquoise and sand gold palette',
    ter='a floating archipelago of green islands over a global ocean',
    sky='painterly cumulus with a second planet low on the horizon'),
 'shattered': dict(
    ref='A world already lost: broken hemisphere, continents adrift',
    pal='ash grey and ember orange palette',
    ter='the broken hemisphere of a cracked planet with continent shards adrift above it',
    sky='a debris ring overhead raining slow meteors'),
 'verdant': dict(
    ref='A runaway-biosphere world: growth has eaten the architecture',
    pal='jade green and warm gold palette',
    ter='terraced jungle plateaus and waterfalls over ruins swallowed by growth',
    sky='painterly cumulus pierced by volumetric god rays'),
}

# ------------------------------------------------------------ DIRECTIONS ----
# Five spines off the probe-D board plus seven wildcards. The brief asks for
# paths not yet taken, so the wildcards are deliberate range, not filler.
DIRECTIONS = {
 'elysian': dict(
    light='high afternoon sun, painterly cumulus, volumetric god rays, soft rim light',
    grade='rich but grounded grade',
    lora=('k2_sunlit-painterly-anime.safetensors', 0.60)),
 'ashen': dict(
    light='low overcast broken by one shaft of pale sun, heavy atmospheric haze, hard rim light',
    grade='desaturated grounded grade',
    lora=('k2_bold-inked-anime-realism.safetensors', 0.75)),
 'voidlight': dict(
    light='lit from below by glowing cyan crystal, bioluminescent rim light',
    grade='deep cool grade with protected highlights',
    lora=('k2_glowing-ember-fantasy.safetensors', 0.70)),
 'faceted': dict(
    light='hard low sun, flat faceted planes catching light, long raking shadows',
    grade='flat matte grade',
    lora=('k2_terracotta-lowpoly-miniature.safetensors', 0.70)),
 # 0.45, not the board's 0.7: at 0.7 this stops being a game screenshot and
 # becomes toy photography on a tabletop.
 'toybox': dict(
    light='clean bright key light, glossy vinyl highlights, crisp contact shadows',
    grade='saturated clean grade',
    lora=('k2_bold-clay-toy-render.safetensors', 0.45)),
 'chrome': dict(
    light='hard specular key, polished chrome and iridescent film, anamorphic lens flare',
    grade='cool metallic grade',
    lora=('k2_chrome-iridescent-render.safetensors', 0.60)),
 'retroanime': dict(
    light='flat cel light with hard shadow terminators',
    grade='retro anime colour grade with slight print warmth',
    lora=('k2_official_retroanime.safetensors', 0.65)),
 'cinematic': dict(
    light='backlit mist, long lens compression, shallow depth of field',
    grade='filmic grade with lifted blacks',
    lora=('k2_misty-anime-cinematic.safetensors', 0.60)),
 'clayworld': dict(
    light='soft broad studio light, handmade clay surfaces with visible tool marks',
    grade='warm handmade grade',
    lora=('k2_miniature-diorama-figurine.safetensors', 0.60)),
 'earlycgi': dict(
    light='flat ambient light with a hard sky gradient, early-2000s game-engine sheen',
    grade='clean nostalgic grade',
    lora=('k2_early-cgi-surreal-render.safetensors', 0.60)),
 'inkline': dict(
    light='hard directional sun, heavy ink contour lines, printed halftone shadow',
    grade='graphic high-contrast grade',
    lora=('k2_bold-inked-anime-realism.safetensors', 0.95)),
 'vinyl': dict(
    light='bright even key, saturated primary vinyl surfaces, hard contact shadow',
    grade='punchy toy-catalogue grade',
    lora=('k2_vintage-plastic-toy.safetensors', 0.50)),

 # ---- OWNER-DIRECTED, probes E/F/G. The refinement of `retroanime`. ----
 # Illustrative but still polygon: cel fills, a heavy uniform black contour on
 # every form, cross-hatch in the shadows -- the Borderlands shader, rather than
 # `inkline`'s print/halftone register or `retroanime`'s contourless cel light.
 #
 # Three things this recipe cost, all of them measured:
 #   * the ink clause must sit in the REGISTER slot (hence `reg`). After the
 #     subject it produced no contour at all across ten plates.
 #   * `inked-comic-crosshatch` and `graphic-novel-earthy-ink` both read a
 #     humanoid silhouette as a COMIC CHARACTER and draw hair and a face on it,
 #     which kills the Roblox read. `bold-inked-superhero-comic` does it least,
 #     so it is the one carried, with retroanime under it holding the cel light.
 #   * the heads still needed saying: "smooth featureless ... plain unmarked"
 #     as a surface the head HAS, never as features it lacks.
 # Verified to hold its line weight at 1920x1088, which a thinner recipe did not.
 'inkcel': dict(
    reg=('cel-shaded comic book videogame render, every form bounded by a thick black ink '
         'outline of even uniform weight, interior panel edges inked too, in-game screenshot '
         'from a third-person gameplay camera'),
    light='hard low sun, flat cel fills with hard shadow terminators',
    mat=(', smooth featureless rounded heads of plain unmarked plastic, avatars in differing '
         'bold team colours, cross-hatched ink hatching inside the shadows, faceted '
         'low-polygon rock'),
    grade='high-contrast comic grade',
    lora=('k2_official_retroanime.safetensors', 0.50),
    lora2=('k2_bold-inked-superhero-comic.safetensors', 0.85)),
}

# ----------------------------------------------------------------- BEATS ----
# {ter} and {sky} are filled from the place. Event beats carry event nouns and a
# motion camera; establishing beats hand the frame to the place on purpose.
BEATS = {
 'starmap': (
    'a holographic star chart table aboard a ship, a dozen planet globes floating above it '
    'as plain unlettered spheres of solid colour, an avatar commander reaching toward one',
    'medium shot over the shoulder, interface glow on the avatar'),
 'approach': (
    'a drop pod streaking down through the upper atmosphere toward {ter} far below, heat '
    'shear peeling off its nose',
    'high wide shot, motion streaks, the ground rushing up'),
 'landing': (
    'the WorldHeart core, a faceted glowing crystal heart in a heavy metal cradle, lowered '
    'onto {ter} on cables while avatar engineers steady it',
    'low angle looking up past the cradle'),
 'survey': (
    'an avatar explorer traversing {ter}, a scan pulse ring expanding outward across the '
    'ground ahead, {sky}',
    'third person from behind, wide, the horizon high in frame'),
 'buildgrid': (
    'build mode active: a translucent blue placement grid laid over {ter}, a ghosted preview '
    'of a defence tower snapping to one cell, plain unlettered icon tiles of solid colour '
    'along the lower edge of the frame',
    'elevated three-quarter view, the grid receding to the horizon'),
 'towerline': (
    'three defence towers of clearly different silhouettes spaced along a ridge of {ter}, '
    'their firing arcs drawn as faint translucent circles on the ground',
    'wide three-quarter view'),
 'loadout': (
    'a character select screen: four blocky avatars on lit turntable podiums with {ter} '
    'blurred far behind them, plain unlettered stat bars of solid colour beside each',
    'frontal centred composition, shallow depth'),
 'waveincoming': (
    'the horizon of {ter} going dark with an approaching swarm, defenders turning toward it, '
    'a slim curved warning arc across the top of the frame',
    'wide shot with a low horizon, stillness before contact'),
 'clash': (
    'the moment of impact on a defence line across {ter}, muzzle flashes, thrown debris, '
    'avatar defenders in violent motion, invaders breaking against a shield wall',
    'close low camera, dynamic tilt, foreground figures cut by the frame'),
 'swarm': (
    'a mass of insectoid invaders pouring over {ter} in a dense column, tracer fire cutting '
    'lanes through them, bodies tumbling',
    'high angle looking down the length of the column'),
 'boss': (
    'a titan invader, a mountain-sized armoured leviathan, rising over {ter} while tiny '
    'avatar defenders brace at its feet',
    'extreme low angle, the titan breaking the top of the frame'),
 'coresiege': (
    'the WorldHeart core cracked and flickering at the centre of a ruined emplacement on '
    '{ter}, defenders forming a last ring around it, shield panels failing',
    'medium shot from slightly high, the core centred and small'),
 'aftermath': (
    # "wreckage" was the first word here and it is a poisoned noun: on Venus it
    # rendered a CAR PARK, twice, on two different seeds. Re-rolling could not
    # fix it because the seed was never the problem -- "wreckage" simply means
    # crashed vehicles to this model, and the toy-render direction has plenty of
    # die-cast cars to reach for. Hunt the noun, do not add a negation: the
    # carcasses are now named as the only debris in the sentence.
    'the battlefield after a won wave on {ter}, split insectoid carapaces and severed '
    'chitin limbs lying where they fell, scorch marks burnt into the ground, a single '
    'avatar defender standing among them',
    'wide still shot, no motion, long shadows'),
 'victory': (
    'planet secured: the WorldHeart core blazing above a rebuilt emplacement on {ter}, '
    'avatars gathered below it, a dropship lifting away',
    'wide heroic shot from a low camera'),
 'hub': (
    'the interior of a between-worlds ship hub, avatars at workbenches and a crew table, a '
    'wide curved window showing {ter} turning below',
    'medium interior shot, warm practical light against the window'),
 'forge': (
    'an upgrade forge: a tower schematic rotating in light above a dark anvil, plain '
    'unlettered tiles of solid colour arranged in a ring around it',
    'medium centred shot, the schematic as the only bright thing'),
 'procgen': (
    'a planet assembling itself out of floating terrain tiles in mid-air, half-formed {ter}, '
    'seams of light where the tiles have not yet knitted together',
    'wide cosmic shot, the unfinished edge toward camera'),
 'traverse': (
    'avatars crossing a rope-and-plank bridge strung between two floating shards of {ter}, '
    'a long drop below them',
    'side-on wide shot, the bridge cutting the frame diagonally'),
 'nightwatch': (
    'a night watch on {ter}, lantern light pooling on the ground, two avatar sentries '
    'silhouetted against the sky',
    'wide low shot, the figures small against the horizon'),
 'orbit': (
    'an orbital view of the whole planet with {ter} legible as continents far below, a thin '
    'ring of defence satellites, and a second planet beyond it',
    'space shot, the planet limb curving across the frame'),
 # ---- Roblox genre archetypes. Generic vocabulary, no third-party IP. ----
 'petzone': (
    'a companion creature paddock built into {ter}, small blocky pet creatures trotting '
    'after avatars, a stable cut into the rock behind',
    'medium shot at creature height'),
 'obby': (
    'an obby parkour course of floating platforms strung across {ter}, an avatar caught '
    'mid-leap between two of them, a checkpoint marker on the far platform',
    'side-on shot, the gap between the platforms centred'),
 'tycoon': (
    'a tycoon conveyor line built across {ter}, ore buckets riding the belt into a smelter, '
    'plain unlettered counter tiles of solid colour mounted above the line',
    'three-quarter shot following the belt into depth'),
 'horror': (
    'a buried corridor under {ter}, one swinging lamp, a wet floor, something long-limbed '
    'standing at the far end of the hall',
    'centred one-point corridor shot, the lamp the only light'),
 'fighter': (
    'an arena duel on {ter}, an avatar suspended mid-air wreathed in an energy aura, a '
    'shockwave ring blowing dust outward beneath them',
    'low three-quarter hero shot, the dust ring in the foreground'),
 'racing': (
    'a hover-kart race along a track cut into {ter}, three avatars in karts fighting for a '
    'line through a banked turn, boost trails behind them',
    'chase camera low and close behind the lead kart'),
 'survival': (
    'a survival camp on {ter} at dusk, a campfire, crafted palisade walls, avatars hauling '
    'gathered resources in through the gate',
    'medium wide shot from outside the palisade'),
 'mining': (
    'a mine shaft descending into {ter}, glowing ore veins in the walls, an avatar riding a '
    'rail cart down with a headlamp lit',
    'down-the-shaft shot, the veins receding into dark'),
}

# --------------------------------------------------------- FIXED CLAUSES ----
REGISTER = 'in-game screenshot from a third-person gameplay camera'
# "stud-topped bricks" used to live here. It put a LEGO baseplate under all
# nineteen plates of probe B and took the whole ground plane with it. Modern
# Roblox is smooth flat-shaded primitives, so that is what the nouns say now.
MATERIAL = ('blocky Roblox-style avatars with smooth rounded heads, cylindrical limbs and '
            'rectangular torsos, visible joint gaps, smooth flat-shaded primitive terrain, '
            'matte plastic and brushed metal')
# Probe A's a04 strength. a05 doubled this and killed the look outright.
GRIT = 'fine film grain, drifting dust, weathered edge wear, dirt settled in the crevices'


def loras_for(direction):
    """The adapter stack for a direction, in patch order.

    Most directions carry one. `inkcel` carries two because the look is two
    separable jobs -- cel light from retroanime, contour ink from the superhero
    comic adapter -- and neither does both on its own.
    """
    d = DIRECTIONS[direction]
    stack = [d['lora']]
    if 'lora2' in d:
        stack.append(d['lora2'])
    return tuple(stack)


def compose(beat, place, direction):
    """The one function that turns a row into a prompt. No plate bypasses it.

    A direction may optionally carry `reg` (replacing the shared REGISTER) and
    `mat` (appended to the shared MATERIAL). Both default to absent, so every
    direction that does not use them composes byte-identically to before and
    nothing already rendered goes stale.

    `reg` exists because a direction can be a RENDERING TECHNIQUE and not just a
    light: an inked cel look has to say so in the register slot, next to "in-game
    screenshot", or it loses to whatever the subject clause describes. Measured
    in probe E -- the same ink nouns placed after the subject produced almost no
    contour on ten plates; moved into the register slot they landed on all of
    them. Clause order is order of weight.
    """
    body, camera = BEATS[beat]
    p, d = PLACES[place], DIRECTIONS[direction]
    subject = body.format(ter=p['ter'], sky=p['sky'])
    reg = d.get('reg', REGISTER)
    mat = MATERIAL + d.get('mat', '')
    return (p['pal'] + ', ' + reg + ', ' + d['light'] + ', ' + subject + ', '
            + mat + ', ' + camera + ', ' + d['grade'] + ', ' + GRIT)
