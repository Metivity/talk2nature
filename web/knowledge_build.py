"""Public evidence map built only from the explicit public catalog inputs."""
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from talk2nature.knowledge import catalog_graph


def build_knowledge(root, output, base, page, notes, sources):
    resources = json.loads((root / 'research/resources.json').read_text())['resources']
    entries = [{'key': f'{kind}:{r[key]}', 'kind': kind, 'title': r['title'], 'payload': r}
               for kind, rows, key in [('source', sources, 'id'), ('note', notes, 'slug'), ('resource', resources, 'id')] for r in rows]
    graph = catalog_graph(entries)
    target = output / 'research/map'; target.mkdir(parents=True, exist_ok=True)
    (target / 'catalog.json').write_text(json.dumps(graph, indent=2, ensure_ascii=False) + '\n')
    esc = lambda v: html.escape(str(v), quote=True)
    source_map = {s['id']: s for s in sources}
    records = ''
    for note in notes:
        links = ''.join(f'<li><a href="{esc(source_map[i]["url"])}">{esc(source_map[i]["title"])} ↗</a></li>' for i in note['source_ids'])
        search = ' '.join([note['title'], note['taxon'], *[source_map[i]['title'] for i in note['source_ids']]])
        records += f'<details class="graph-record" data-search="{esc(search.lower())}"><summary>{esc(note["title"])}</summary><p>{esc(note["review_depth"])}</p><p><a href="{base}/research/{esc(note["slug"])}/">Read our interpretation and limits →</a></p><strong>This note cites:</strong><ul>{links}</ul></details>'
    page('research/map/', 'Explore the evidence map', 'A versioned knowledge graph connects original research notes to their sources. Explore the connections and review depth.', f'''
<section class="page-intro section"><p class="eyebrow">THE KNOWLEDGE GRAPH · FIRST FOUNDATION</p><h1>See the connections.<br><em>Keep the evidence.</em></h1><p class="lede">Every note should lead back to a source. Every interpretation should keep its limits.</p><div class="graph-summary"><span>{len(graph['nodes'])} catalog records</span><span>{len(graph['edges'])} explicit citation links</span><span>No recordings or private records</span></div></section>
<section class="section library-browser"><label for="graph-search">Find a subject, method or source</label><input id="graph-search" type="search" placeholder="Try movement, fungi or bird…"><p id="graph-count" class="quiet" role="status">{len(notes)} evidence notes · Open a note to follow its sources.</p><div id="graph-records">{records}</div><p id="graph-empty" hidden>No matches. Try another word or clear the search.</p></section>
<section class="section paper-panel"><h2>A foundation for shared research.</h2><p>These connections are citation records, not statements that every source agrees. Each record has a content fingerprint; a changed source record produces a different version.</p><p>The private prototype also connects frozen study references, sessions, observations and releases. It excludes withdrawn observations from its graph. Media storage and model-run records are the next schema extensions, not live public services.</p><details><summary>Advanced · machine-readable catalog</summary><p><a href="{base}/research/map/catalog.json" download>Download the public graph · JSON</a></p><p>Schema: talk2nature.knowledge.v1. Original catalog metadata only; this file is not a training dataset or permission to reuse third-party works. Citation targets reflect the catalog at build time, not a verified historical version of the original webpage.</p></details><a href="{base}/research/frontiers/">Explore the scientific direction →</a></section>''', active='research/', extra_head=f'<script defer src="{base}/assets/knowledge.js"></script>')
    body = (root / 'web/templates/frontiers.html').read_text().replace('{{base}}', base)
    page('research/frontiers/', 'Sound, movement, plants and fungi: our next questions', 'Explore a grounded research direction for multimodal animal communication, plant signaling and fungal measurements.', body, active='research/')
