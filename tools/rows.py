# -*- coding: utf-8 -*-
"""The shipping row list: 164 (beat, place, direction) triples.

106 curated below, plus two 12-wide direction LINEUPS and a coverage top-up
appended after the literal (see the LINEUPS block).

NOT a cartesian product. 28 x 14 x 12 is 4704 plates and most of them would be
the same picture twice; the spread here is chosen so that

  * the tower-defence core (build, line, wave, clash, swarm, boss, siege,
    aftermath, victory) carries the most weight, because it is the game;
  * every PLACE appears 7-8 times, so no world reads as a one-off;
  * every DIRECTION appears 8-10 times across DIFFERENT beats, so the owner can
    judge a look on its range rather than on one flattering frame;
  * place and beat are paired on FUNCTION where the reference suggests one --
    the forge goes to the volcanic world, the horror corridor to the sunless
    one, the parkour course to the world whose only land floats.

Key is 'beat_place_direction' and the seed is FNV-1a of that, so any single
plate can be re-rolled by name without disturbing its neighbours.
"""

ROWS = [
 # ---- star map / between-worlds meta -------------------------------------
 ('starmap',      'ringmoon',   'voidlight'),
 ('starmap',      'carbon',     'chrome'),
 ('starmap',      'ocean',      'elysian'),
 ('hub',          'ringmoon',   'cinematic'),
 ('hub',          'ocean',      'elysian'),
 ('hub',          'shattered',  'ashen'),
 ('loadout',      'verdant',    'elysian'),
 ('loadout',      'io',         'inkline'),
 ('loadout',      'europa',     'toybox'),
 ('forge',        'io',         'ashen'),
 ('forge',        'carbon',     'chrome'),
 ('forge',        'titan',      'clayworld'),

 # ---- arrival ------------------------------------------------------------
 ('approach',     'io',         'cinematic'),
 ('approach',     'venus',      'elysian'),
 ('approach',     'ringmoon',   'voidlight'),
 ('approach',     'shattered',  'ashen'),
 ('landing',      'mars',       'ashen'),
 ('landing',      'verdant',    'elysian'),
 ('landing',      'europa',     'faceted'),
 ('landing',      'rogue',      'voidlight'),

 # ---- exploration / the procedural world --------------------------------
 ('survey',       'verdant',    'elysian'),
 ('survey',       'europa',     'faceted'),
 ('survey',       'enceladus',  'cinematic'),
 ('survey',       'titan',      'ashen'),
 ('survey',       'reddwarf',   'retroanime'),
 ('procgen',      'ocean',      'chrome'),
 ('procgen',      'shattered',  'voidlight'),
 ('procgen',      'enceladus',  'earlycgi'),
 ('procgen',      'carbon',     'faceted'),
 ('orbit',        'ringmoon',   'cinematic'),
 ('orbit',        'terminator', 'voidlight'),
 ('orbit',        'ocean',      'elysian'),
 ('orbit',        'io',         'chrome'),
 ('traverse',     'ocean',      'elysian'),
 ('traverse',     'venus',      'toybox'),
 ('traverse',     'shattered',  'faceted'),
 ('traverse',     'rogue',      'voidlight'),
 ('nightwatch',   'terminator', 'cinematic'),
 ('nightwatch',   'rogue',      'voidlight'),
 ('nightwatch',   'europa',     'ashen'),

 # ---- the tower-defence core --------------------------------------------
 ('buildgrid',    'venus',      'chrome'),
 ('buildgrid',    'mars',       'faceted'),
 ('buildgrid',    'verdant',    'elysian'),
 ('buildgrid',    'europa',     'earlycgi'),
 ('buildgrid',    'ocean',      'toybox'),
 ('towerline',    'mars',       'ashen'),
 ('towerline',    'verdant',    'elysian'),
 ('towerline',    'carbon',     'chrome'),
 ('towerline',    'terminator', 'cinematic'),
 ('towerline',    'io',         'faceted'),
 ('waveincoming', 'titan',      'ashen'),
 ('waveincoming', 'terminator', 'cinematic'),
 ('waveincoming', 'mars',       'inkline'),
 ('waveincoming', 'ocean',      'elysian'),
 ('waveincoming', 'rogue',      'voidlight'),
 ('clash',        'io',         'ashen'),
 ('clash',        'mars',       'inkline'),
 ('clash',        'verdant',    'elysian'),
 ('clash',        'europa',     'faceted'),
 ('clash',        'shattered',  'voidlight'),
 ('clash',        'venus',      'toybox'),
 ('swarm',        'mars',       'ashen'),
 ('swarm',        'titan',      'inkline'),
 ('swarm',        'carbon',     'faceted'),
 ('swarm',        'verdant',    'retroanime'),
 ('boss',         'shattered',  'ashen'),
 ('boss',         'io',         'cinematic'),
 ('boss',         'rogue',      'voidlight'),
 ('boss',         'enceladus',  'inkline'),
 ('boss',         'ocean',      'elysian'),
 ('coresiege',    'shattered',  'ashen'),
 ('coresiege',    'reddwarf',   'cinematic'),
 ('coresiege',    'europa',     'voidlight'),
 ('coresiege',    'mars',       'faceted'),
 ('aftermath',    'shattered',  'ashen'),
 ('aftermath',    'reddwarf',   'cinematic'),
 ('aftermath',    'titan',      'inkline'),
 ('aftermath',    'venus',      'clayworld'),
 ('victory',      'verdant',    'elysian'),
 ('victory',      'carbon',     'chrome'),
 ('victory',      'ocean',      'toybox'),
 ('victory',      'terminator', 'retroanime'),

 # ---- Roblox genre archetypes, rendered in the WorldHeart look ----------
 # Whether the style can HOST the platform's whole range is the question the
 # brief actually asks, so each archetype gets three different directions.
 ('petzone',      'verdant',    'elysian'),
 ('petzone',      'ocean',      'toybox'),
 ('petzone',      'enceladus',  'clayworld'),
 ('obby',         'venus',      'toybox'),
 ('obby',         'ocean',      'elysian'),
 ('obby',         'shattered',  'faceted'),
 ('tycoon',       'io',         'earlycgi'),
 ('tycoon',       'mars',       'vinyl'),
 ('tycoon',       'carbon',     'chrome'),
 ('horror',       'rogue',      'cinematic'),
 ('horror',       'europa',     'ashen'),
 ('horror',       'shattered',  'inkline'),
 ('fighter',      'terminator', 'retroanime'),
 ('fighter',      'verdant',    'elysian'),
 ('fighter',      'io',         'inkline'),
 ('racing',       'mars',       'vinyl'),
 ('racing',       'ringmoon',   'chrome'),
 ('racing',       'titan',      'retroanime'),
 ('survival',     'reddwarf',   'ashen'),
 ('survival',     'verdant',    'clayworld'),
 ('survival',     'europa',     'earlycgi'),
 ('mining',       'io',         'voidlight'),
 ('mining',       'rogue',      'cinematic'),
 ('mining',       'carbon',     'vinyl'),

 # ---- deliberate wildcards: directions the spines would never reach -----
 ('towerline',    'reddwarf',   'vinyl'),
 ('survey',       'shattered',  'clayworld'),
 ('victory',      'io',         'earlycgi'),
 ('waveincoming', 'enceladus',  'vinyl'),
 ('buildgrid',    'rogue',      'inkline'),
 ('hub',          'titan',      'earlycgi'),
]


# ---------------------------------------------------------------- LINEUPS ----
# Two beats rendered across ALL TWELVE directions on one fixed world each.
#
# The rest of the catalogue spreads directions across different beats and
# places, which is right for showing range but wrong for CHOOSING: no two
# plates are comparable like for like, so a direction can win on having drawn a
# flattering world. A lineup holds beat and place still and moves only the look.
# One calm composition beat and one combat beat, because a direction that reads
# well standing still can fall apart the moment anything is in motion.
#
# Keys that already exist in the spread above are dropped rather than
# duplicated -- that plate IS this lineup's entry for that direction.
_ALL_DIRS = ['elysian', 'ashen', 'voidlight', 'faceted', 'toybox', 'chrome',
             'retroanime', 'cinematic', 'clayworld', 'earlycgi', 'inkline', 'vinyl']

_seen = set(ROWS)
for _d in _ALL_DIRS:
    for _beat, _place in (('towerline', 'verdant'), ('clash', 'mars')):
        if (_beat, _place, _d) not in _seen:
            ROWS.append((_beat, _place, _d))
            _seen.add((_beat, _place, _d))

# ---- coverage top-up: the places and directions the spread under-served ----
for _row in [
    ('orbit',        'enceladus',  'earlycgi'),
    ('victory',      'ringmoon',   'vinyl'),
    ('landing',      'reddwarf',   'clayworld'),
    ('buildgrid',    'terminator', 'retroanime'),
    ('nightwatch',   'venus',      'voidlight'),
    ('procgen',      'reddwarf',   'chrome'),
    ('survey',       'ringmoon',   'clayworld'),
    ('coresiege',    'titan',      'vinyl'),
    ('swarm',        'enceladus',  'retroanime'),
    ('traverse',     'carbon',     'earlycgi'),
]:
    if _row not in _seen:
        ROWS.append(_row)
        _seen.add(_row)


# ------------------------------------------------- OWNER PICK: RETROANIME ----
# All five plates the owner picked as their favourites came back the same
# direction -- retroanime -- so this block extends it rather than spreading
# further. What those five had in common is worth naming, because it drives the
# choice of beat here: every one of them is a WIDE frame with a single dominant
# light source doing all the work (the fixed red sun, the terminator split, the
# orange dune haze), read against hard cel shading and strong silhouettes.
#
# So these ten go to beats with a big sky or a single lamp, and to the worlds
# whose palette is already one strong graphic colour. Three interiors are
# included on purpose: lamp-lit corridors are the other thing this register has
# always been good at, and a direction the owner may standardise on should be
# tested where it is NOT just painting a sunset.
for _row in [
    ('boss',         'io',         'retroanime'),   # titan silhouette, banded giant sky
    ('waveincoming', 'reddwarf',   'retroanime'),   # swarm darkening the horizon, huge red sun
    ('orbit',        'ringmoon',   'retroanime'),   # gas giant and ring, the classic OVA vista
    ('nightwatch',   'terminator', 'retroanime'),   # sentries on the day-night line
    ('approach',     'titan',      'retroanime'),   # drop pod through orange haze
    ('coresiege',    'shattered',  'retroanime'),   # last ring around the cracked core
    ('traverse',     'shattered',  'retroanime'),   # rope bridge, debris ring overhead
    ('mining',       'io',         'retroanime'),   # interior: ore veins down a shaft
    ('hub',          'ringmoon',   'retroanime'),   # interior: gas giant through the window
    ('horror',       'rogue',      'retroanime'),   # interior: one lamp, bioluminescent dark
]:
    if _row not in _seen:
        ROWS.append(_row)
        _seen.add(_row)


# ------------------------------------------- OWNER-DIRECTED: INKCEL LOOK ----
# The owner asked for the retroanime look made "illustrative yet still polygon,
# cel shade with black outline" -- the Borderlands shader. That became the
# `inkcel` direction (catalogue.py, probes E/F/G).
#
# FIVE of these ten are the owner's five favourite plates re-shot in the new
# look, on the same beat and the same world. That is deliberate: "better" is a
# comparison, and the only way to judge it is the same frame twice. The gallery
# puts them side by side when grouped by game moment.
#
# The other five go where a heavy contour has the most to bite on -- a titan
# silhouette, a mass of bodies, a last stand -- rather than where it merely
# looks pleasant.
for _row in [
    # the five favourites, re-shot
    ('survey',    'reddwarf',   'inkcel'),
    ('racing',    'titan',      'inkcel'),
    ('fighter',   'terminator', 'inkcel'),
    ('clash',     'mars',       'inkcel'),
    ('buildgrid', 'terminator', 'inkcel'),
    # five new moments chosen for what a contour can bite on
    ('boss',      'io',         'inkcel'),   # titan silhouette against acid-yellow sky
    ('towerline', 'verdant',    'inkcel'),   # the lineup shot, so it joins that comparison
    ('swarm',     'mars',       'inkcel'),   # a mass of bodies is all edges
    ('coresiege', 'shattered',  'inkcel'),   # last stand, ember sky
    ('victory',   'verdant',    'inkcel'),   # the heroic wide
]:
    if _row not in _seen:
        ROWS.append(_row)
        _seen.add(_row)


def key_of(row):
    return '%s_%s_%s' % row


def check():
    """Balance audit. Run it before a batch, not after."""
    from collections import Counter
    b, p, d = Counter(), Counter(), Counter()
    for beat, place, direc in ROWS:
        b[beat] += 1; p[place] += 1; d[direc] += 1
    assert len(set(map(key_of, ROWS))) == len(ROWS), 'duplicate key in ROWS'
    return len(ROWS), b, p, d


if __name__ == '__main__':
    n, b, p, d = check()
    print('rows:', n, ' unique keys: ok')
    print('\nbeats   ', dict(b.most_common()))
    print('\nplaces  ', dict(p.most_common()))
    print('\ndirs    ', dict(d.most_common()))
