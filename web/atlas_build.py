"""Build a progressively enhanced world atlas from public literature metadata."""
import html
import json
from talk2nature.atlas import public_atlas, GROUPS


def build_atlas(root, output, base, page, notes, sources):
    atlas = public_atlas(notes, sources, json.loads((root/'content/atlas-places.json').read_text()))
    target = output/'research/atlas'; target.mkdir(parents=True, exist_ok=True)
    (target/'catalog.json').write_text(json.dumps(atlas, ensure_ascii=False, indent=2)+'\n')
    esc = lambda x: html.escape(str(x), quote=True)
    place_map = {p['id']: p for p in atlas['places']}
    source_map = {s['id']: s for s in atlas['sources']}
    cards = []
    for r in atlas['records']:
        location_names = ' · '.join(('Animal origin · ' if l['role']=='animal_origin' else '') + place_map[l['place_id']]['label'] for l in r['locations'])
        location_label = location_names or ('No single mapped site' if r['location_status']=='not_applicable' else 'Location awaiting review')
        timing = r['observation_period']['label'] if r['observation_period'] else 'Observation dates not established here'
        proof = ''.join(f'<li><strong>{esc(place_map[l["place_id"]]["label"])}</strong> · {"Animal origin, not recording site" if l["role"]=="animal_origin" else "Study region"}<p>{esc(l["basis"])}</p><a href="{esc(source_map[l["source_id"]]["url"])}">Location source ↗</a> · {esc(l["locator"])}</li>' for l in r['locations'])
        citations = ''.join(f'<li><a href="{esc(source_map[i]["url"])}">{esc(source_map[i]["title"])} ↗</a></li>' for i in r['source_ids'])
        observed = r['observation_period']
        time_proof = f'<p><a href="{esc(source_map[observed["source_id"]]["url"])}">Observation-date source ↗</a> · {esc(observed["locator"])}</p>' if observed else ''
        cards.append(f'''<article class="atlas-record" id="atlas-note-{esc(r['id'])}" data-id="{esc(r['id'])}"><div class="atlas-date"><strong>{esc(r['source_year_label'])}</strong><span>{esc(r['year_basis'])}</span></div><div class="atlas-record-body"><p class="atlas-record-meta">{esc(r['taxon'])} / {esc(r['kind'])}</p><h3><a href="{base}/research/{esc(r['id'])}/">{esc(r['title'])} ↗</a></h3><p>{esc(r['finding'])}</p><div class="atlas-record-location"><span aria-hidden="true">◎</span> {esc(location_label)}</div><p class="atlas-observed">{esc(timing)}</p><details><summary>Evidence, location & limits</summary><p>{esc(r['limitations'])}</p><p>{esc(r['review_depth'])}</p><p>{esc(r['location_note'])}</p>{'<ul>'+proof+'</ul>' if proof else ''}{time_proof}<p>Location metadata reviewed: {esc(r['location_reviewed'] or 'Not yet reviewed')}. Map points are approximate locators, not sample coordinates.</p><strong>Follow the sources</strong><ul>{citations}</ul><a href="{base}/research/map/#evidence-{esc(r['id'])}">See this note’s evidence connections →</a></details></div></article>''')
    group_options=''.join(f'<option value="{k}">{v}</option>' for k,v in GROUPS.items())
    place_options=''.join(f'<option value="{esc(p["id"])}">{esc(p["label"])}</option>' for p in atlas['places'])
    located=sum(bool(r['locations']) for r in atlas['records'])
    body=(root/'web/templates/atlas.html').read_text()
    replacements={'base':base,'records':'\n'.join(cards),'record_count':len(atlas['records']),'mapped_count':located,
                  'unmapped_count':len(atlas['records'])-located,'place_count':len(atlas['places']),
                  'groups':group_options,'places':place_options,
                  'first_year':min(r['source_year'] for r in atlas['records']), 'last_year':max(r['source_year'] for r in atlas['records'])}
    for key,value in replacements.items(): body=body.replace('{{'+key+'}}',str(value))
    page('research/atlas/','A world atlas of nature communication research','Explore published work across places and time, with primary sources, approximate locations and explicit gaps. No private observations or recordings.',body,active='research/',extra_head=f'<link rel="stylesheet" href="{base}/assets/atlas.css"><script type="module" src="{base}/assets/atlas.js"></script>')
    return atlas
