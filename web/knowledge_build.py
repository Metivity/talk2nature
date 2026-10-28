"""Public evidence map built only from the explicit public catalog inputs."""
import html
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from talk2nature.knowledge import catalog_graph


def build_knowledge(root, output, base, page, notes, sources):
    resources = json.loads((root / 'research/resources.json').read_text())['resources']
    records = [
        {'kind': 'note', 'key': row['slug'], 'row': row} for row in notes
    ] + [
        {'kind': 'resource', 'key': row['id'], 'row': row} for row in resources
    ] + [
        {'kind': 'source', 'key': row['id'], 'row': row} for row in sources
    ]
    entries = [{'key': f"{item['kind']}:{item['key']}", 'kind': item['kind'],
                'title': item['row']['title'], 'payload': item['row']} for item in records]
    graph = catalog_graph(entries)
    target = output / 'research/map'
    target.mkdir(parents=True, exist_ok=True)
    (target / 'catalog.json').write_text(json.dumps(graph, indent=2, ensure_ascii=False) + '\n')

    esc = lambda value: html.escape(str(value), quote=True)
    source_map = {item['id']: item for item in sources}
    referenced_by = {source_id: [] for source_id in source_map}
    for item in records:
        if item['kind'] not in {'note', 'resource'}:
            continue
        for source_id in item['row'].get('source_ids', []):
            referenced_by[source_id].append(item)

    def safe_link(url, label):
        parsed = urlsplit(str(url or ''))
        if parsed.scheme not in {'http', 'https'} or not parsed.netloc:
            return ''
        return f'<a href="{esc(url)}" rel="noreferrer">{esc(label)} ↗</a>'

    def text(value):
        if value is None or value == '':
            return ''
        if isinstance(value, (dict, list)):
            return json.dumps(value, sort_keys=True, ensure_ascii=False)
        return str(value)

    def para(label, value):
        value = text(value)
        return f'<p><strong>{esc(label)}:</strong> {esc(value)}</p>' if value else ''

    def source_links(source_ids):
        links = []
        for source_id in source_ids:
            source = source_map[source_id]
            links.append(f'<li><a href="#source-{source_id}">Source {source_id}: {esc(source["title"])}</a></li>')
        return '<strong>Linked sources</strong><ul>' + ''.join(links) + '</ul>' if links else ''

    def record_card(item):
        kind, row = item['kind'], item['row']
        title = esc(row['title'])
        if kind == 'note':
            key = esc(row['slug'])
            record_id = f'evidence-{key}'
            kind_label = 'Research note'
            meta = ' · '.join(filter(None, [text(row.get('taxon')), text(row.get('kind')), text(row.get('year_label') or row.get('year'))]))
            search_fields = [row.get(field) for field in ('title', 'taxon', 'kind', 'year', 'year_label',
                                                           'purpose', 'finding', 'lesson', 'limitations',
                                                           'review_depth', 'review_stage', 'next_review')]
            content = (
                para('Question / purpose', row.get('purpose')) + para('Finding', row.get('finding'))
                + para('What this contributes', row.get('lesson')) + para('Review depth', row.get('review_depth'))
                + para('Limits', row.get('limitations'))
                + f'<p><a href="{esc(base)}/research/{key}/">Read the research note and its limits →</a></p>'
                + source_links(row.get('source_ids', []))
            )
        elif kind == 'resource':
            key = esc(row['id'])
            record_id = f'resource-{key}'
            kind_label = f'Resource · {text(row.get("kind", "unspecified"))}'
            meta = ' · '.join(filter(None, [text(row.get('version')), text(row.get('reviewed'))]))
            rights = row.get('rights') if isinstance(row.get('rights'), dict) else {}
            search_fields = [row.get(field) for field in ('id', 'title', 'kind', 'version', 'task', 'decision',
                                                           'review_depth', 'reviewed', 'access', 'acquisition',
                                                           'limitations', 'priority')]
            search_fields += [rights.get(field) for field in ('license', 'scope', 'conditions', 'research_use',
                                                               'commercial_use', 'redistribution')]
            right_lines = ''.join(para(label, rights.get(field)) for label, field in (
                ('License', 'license'), ('Rights scope', 'scope'), ('Reuse conditions', 'conditions'),
                ('Research use', 'research_use'), ('Commercial use', 'commercial_use'),
                ('Redistribution', 'redistribution')))
            external = safe_link(row.get('url') or row.get('landing_url'), 'Open the recorded resource')
            content = (
                para('Task', row.get('task')) + para('Review depth', row.get('review_depth'))
                + para('Access', row.get('access')) + para('Acquisition status', row.get('acquisition'))
                + para('Decision', row.get('decision')) + para('Limitations', row.get('limitations'))
                + right_lines + (f'<p>{external}</p>' if external else '')
                + source_links(row.get('source_ids', []))
            )
        else:
            key = str(row['id'])
            record_id = f'source-{key}'
            kind_label = 'Source citation'
            meta = text(row.get('checked'))
            search_fields = [row.get(field) for field in ('id', 'title', 'description', 'origin', 'checked')]
            external = safe_link(row.get('url'), 'Open the original source')
            refs = referenced_by[row['id']]
            reverse = ''.join(
                f'<li><a href="#{"evidence-" + esc(ref["key"]) if ref["kind"] == "note" else "resource-" + esc(ref["key"])}">'
                f'{"Research note" if ref["kind"] == "note" else "Resource"}: {esc(ref["row"]["title"])}</a></li>'
                for ref in refs
            )
            content = (
                para('Description', row.get('description')) + para('Source review / provenance', row.get('origin'))
                + (f'<p>{external}</p>' if external else '')
                + (f'<strong>Referenced by {len(refs)} catalog record(s)</strong><ul>{reverse}</ul>' if refs else
                   '<p>This citation is not linked from a research note or reusable resource in the current catalog.</p>')
            )

        search_text = ' '.join(text(value) for value in search_fields if value is not None).lower()
        return (f'<details id="{esc(record_id)}" class="graph-record" data-kind="{esc(kind)}" '
                f'data-search="{esc(search_text)}"><summary><span class="graph-kind">{esc(kind_label)}</span> '
                f'<span class="graph-title">{title}</span>{f" <span class=\"graph-meta\">{esc(meta)}</span>" if meta else ""}'
                f'</summary><div class="graph-detail">{content}</div></details>')

    cards = ''.join(record_card(item) for item in records)
    count_by_kind = {kind: sum(item['kind'] == kind for item in records)
                     for kind in ('note', 'resource', 'source')}
    page('research/map/', 'Explore the evidence map',
         'Search source-linked research notes, datasets, code, models and original citations. Each record states its review depth and limits.', f'''
<section class="page-intro section"><p><a href="{base}/research/atlas/">World atlas: explore places and history →</a></p><p class="eyebrow">THE KNOWLEDGE GRAPH · PUBLIC CATALOG</p><h1>See the connections.<br><em>Keep the evidence.</em></h1><p class="lede">Find what has been studied, what resources exist and what each record can—and cannot—support.</p><div class="graph-summary"><span>{count_by_kind['note']} research notes</span><span>{count_by_kind['resource']} linked research resources</span><span>{count_by_kind['source']} original source citations</span><span>{len(graph['edges'])} explicit catalog links</span></div><p class="quiet">Public metadata only. No recordings, participant observations or private records.</p></section>
<section class="section library-browser"><div class="graph-controls"><div><label for="graph-search">Search all records</label><input id="graph-search" type="search" placeholder="Try parrots, receiver response, dataset rights…" autocomplete="off"></div><div><label for="graph-kind-filter">Record type</label><select id="graph-kind-filter"><option value="all">All record types</option><option value="note">Research notes</option><option value="resource">Papers, data, code &amp; models</option><option value="source">Original citations</option></select></div></div><p id="graph-count" class="quiet" role="status" aria-live="polite">{len(records)} catalog records · Search by topic, task, review depth or rights.</p><div id="graph-records">{cards}</div><p id="graph-empty" hidden>No matching records. Try another search or choose all record types.</p></section>
<section class="section paper-panel"><h2>Connections are provenance.</h2><p>A citation or catalog link shows where a record points; it does not mean that sources agree or that a result has been independently reproduced. Each graph node is versioned from the public catalog metadata.</p><p>A resource's permissions apply only to the named component and scope in its rights record. Article, data, code, recordings and model weights can have different terms. A public listing is not training permission.</p><details><summary>Advanced · machine-readable catalog</summary><p><a href="{base}/research/map/catalog.json" download>Download the public graph · JSON</a></p><p>Schema: talk2nature.knowledge.v1. This metadata graph is not a training dataset or permission to reuse third-party works. Citation targets reflect the catalog at build time, not a verified historical snapshot of the original webpage.</p></details><a href="{base}/research/frontiers/">Explore the scientific direction →</a></section>''', active='research/', extra_head=f'<script defer src="{base}/assets/knowledge.js"></script>')
    body = (root / 'web/templates/frontiers.html').read_text().replace('{{base}}', base)
    page('research/frontiers/', 'Sound, movement, plants and fungi: our next questions',
         'Explore a grounded research direction for multimodal animal communication, plant signaling and fungal measurements.',
         body, active='research/')
