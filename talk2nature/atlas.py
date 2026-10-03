"""Public geographic projection of curated literature, never private observations."""
import math
import re
from datetime import date
from .knowledge import fingerprint, version_id

SCHEMA = 'talk2nature.atlas.v1'
GROUPS = {'birds': 'Birds & parrots', 'mammals': 'Mammals', 'other_animals': 'Other animals',
          'plants_fungi': 'Plants & fungi', 'methods': 'Models & methods'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value, limit=1000):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= limit


def group(taxon):
    if taxon in {'Birds', 'Parrots'}:
        return 'birds'
    if taxon in {'Marine mammals', 'Companion animals', 'Bats', 'Mammals', 'Elephants', 'Cats', 'Farm animals'}:
        return 'mammals'
    if taxon == 'Plants & fungi':
        return 'plants_fungi'
    if taxon in {'Machine learning', 'Research tools', 'Cross-species', 'Across animals', 'Scientific method'}:
        return 'methods'
    return 'other_animals'


def public_atlas(notes, sources, place_file):
    require(place_file.get('schema') == 'talk2nature.atlas-places.v1', 'Unknown atlas places schema.')
    places = place_file.get('places', [])
    require(isinstance(places, list) and 0 < len(places) <= 500, 'Invalid place registry.')
    place_ids = set()
    for p in places:
        require(set(p) == {'id', 'label', 'precision', 'latitude', 'longitude'}, 'Unexpected place fields; public points must be explicit.')
        require(isinstance(p['id'], str) and re.fullmatch(r'[a-z][a-z0-9-]{0,79}', p['id']) and p['id'] not in place_ids and text(p['label'], 160), 'Invalid or duplicate atlas place.')
        require(p['precision'] in {'region', 'country'}, 'Exact locations are not allowed in this public atlas.')
        for key, limit in [('latitude', 90), ('longitude', 180)]:
            x = p[key]
            require(type(x) in {int, float} and math.isfinite(x) and abs(x) <= limit and abs(x*10-round(x*10)) < 1e-8, 'Use coarse display coordinates, to at most one decimal place.')
        place_ids.add(p['id'])
    place_map = {p['id']: p for p in places}
    source_map = {s['id']: s for s in sources}
    records, seen, used_places = [], set(), set()
    for n in notes:
        require(n['slug'] not in seen, 'Duplicate atlas evidence note.')
        seen.add(n['slug'])
        years = [int(y) for y in re.findall(r'\b(?:18|19|20)\d{2}\b', n['year'])]
        require(bool(years), 'A note needs a source/documentation year.')
        atlas = n.get('atlas', {'reviewed': None, 'location_status': 'pending', 'location_note': 'Location has not yet been checked in primary sources.', 'locations': [], 'observation_period': None})
        require(isinstance(atlas, dict) and set(atlas) == {'reviewed', 'location_status', 'location_note', 'locations', 'observation_period'}, 'Unexpected public atlas metadata.')
        require(atlas['location_status'] in {'mapped', 'pending', 'not_applicable'} and text(atlas['location_note']), 'Invalid location review status.')
        if 'atlas' in n:
            require(isinstance(atlas['reviewed'], str), 'Location review date is required.')
            date.fromisoformat(atlas['reviewed'])
        locations = atlas['locations']
        require(isinstance(locations, list) and len(locations) <= 20 and (bool(locations) == (atlas['location_status'] == 'mapped')), 'Location status and mapped places disagree.')
        references = set(n['source_ids'])
        require(references <= set(source_map), 'An atlas note cites a missing source.')
        locations_seen = set()
        for loc in locations:
            require(isinstance(loc, dict) and set(loc) == {'place_id', 'role', 'source_id', 'locator', 'basis'}, 'Unexpected location evidence fields.')
            require(loc['place_id'] in place_ids and loc['place_id'] not in locations_seen, 'Unknown or duplicate mapped place.')
            require(loc['role'] in {'study_region', 'animal_origin'}, 'Do not map an author affiliation as a study site.')
            require(type(loc['source_id']) is int and loc['source_id'] in references and text(loc['locator'], 400) and text(loc['basis']), 'A mapped location needs a cited primary-source passage.')
            locations_seen.add(loc['place_id']); used_places.add(loc['place_id'])
        observed = atlas['observation_period']
        if observed is not None:
            require(isinstance(observed, dict) and set(observed) == {'label', 'start_year', 'end_year', 'source_id', 'locator'}, 'Unexpected observation-period fields.')
            require(type(observed['start_year']) is int and type(observed['end_year']) is int and 1800 <= observed['start_year'] <= observed['end_year'] <= max(years), 'Invalid observation years; do not substitute publication dates.')
            require(type(observed['source_id']) is int and observed['source_id'] in references and text(observed['label'], 200) and text(observed['locator'], 400), 'Observation dates need a cited passage.')
        key = 'note:' + n['slug']
        # Reuse the exact catalog version: private catalog snapshots keep these
        # public location assertions together with their original evidence note.
        records.append({'id': n['slug'], 'evidence_key': key, 'evidence_version': version_id(key, fingerprint(n)),
                        'title': n['title'], 'taxon': n['taxon'], 'group': group(n['taxon']),
                        'kind': n['kind'], 'source_year': max(years), 'source_year_label': n['year'],
                        'year_basis': n['year_label'], 'finding': n['finding'], 'limitations': n['limitations'],
                        'review_depth': n['review_depth'], 'source_ids': n['source_ids'],
                        'location_status': atlas['location_status'], 'location_note': atlas['location_note'],
                        'location_reviewed': atlas['reviewed'], 'locations': locations,
                        'place_labels': [place_map[l['place_id']]['label'] for l in locations],
                        'observation_period': observed})
    require(used_places == place_ids, 'A place without a cited note must not appear on the map.')
    source_ids = {i for r in records for i in r['source_ids']}
    # No source free text, private payload, recording path or household metadata.
    body = {'schema': SCHEMA, 'visibility': 'public_literature_metadata',
            'notice': 'Curated literature notes, not individual observations, research coverage or animal abundance. Display points are approximate. No private records or recordings.',
            'places': sorted(places, key=lambda p: p['id']), 'groups': GROUPS,
            'records': sorted(records, key=lambda r: (r['source_year'], r['id'])),
            'sources': [{'id': i, 'title': source_map[i]['title'], 'url': source_map[i]['url']} for i in sorted(source_ids)]}
    return {**body, 'fingerprint': fingerprint(body)}
