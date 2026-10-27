"""Build a public, source-linked directory from the reviewed resource catalog."""
import html
import json
from pathlib import Path
from urllib.parse import urlsplit


def esc(value):
    return html.escape(str(value), quote=True)


def https_href(value):
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Resource directory links must use HTTPS without credentials.')
    return esc(value)


def rights_status(value):
    labels = {
        'conditional': 'Conditional; check the license, scope and stated conditions for your intended use.',
        'not_admitted': 'Not admitted for this project.',
        'unresolved': 'Unresolved; treat as not cleared.',
    }
    if value not in labels:
        raise ValueError(f'Unknown resource-rights decision: {value}')
    return labels[value]


def acquisition_status(value):
    labels = {
        'metadata_only': 'Metadata only; no files are included in this public directory.',
        'sample_approved': 'A bounded sample path is approved by the collection rules; this is not scientific or training admission.',
    }
    if value not in labels:
        raise ValueError(f'Unknown resource-acquisition decision: {value}')
    return labels[value]


def build_resource_directory(root: Path, base: str, page):
    catalog = json.loads((root / 'research/resources.json').read_text())
    resources = catalog['resources']
    kind_labels = {'paper': 'Paper', 'dataset': 'Dataset', 'code': 'Code', 'model': 'Model', 'standard': 'Standard', 'project': 'Project'}
    acquisition_labels = {'metadata_only': 'Metadata only', 'sample_approved': 'Limited sample route'}
    kind_options = ''.join(
        f'<option value="{kind}">{kind_labels[kind]}</option>'
        for kind in ('paper', 'dataset', 'code', 'model', 'standard', 'project')
    )

    entries = []
    for item in resources:
        rights = item['rights']
        title = esc(item['title'])
        source_url = item.get('landing_url', item['url'])
        acquisition_label = acquisition_labels.get(item['acquisition'])
        if acquisition_label is None:
            raise ValueError(f"Unknown resource-acquisition label: {item['acquisition']}")
        entries.append(f'''<article class="resource-entry" data-kind="{esc(item['kind'])}" data-research-use="{esc(rights['research_use'])}">
<div class="resource-heading"><div><p class="eyebrow">{kind_labels[item['kind']]} · Catalog reviewed {esc(item['reviewed'])}</p><h2><a href="{https_href(source_url)}" rel="external noopener">{title} <span aria-hidden="true">↗</span></a></h2></div><span class="resource-status">{esc(acquisition_label)}</span></div>
<p class="resource-task">{esc(item['task'])}</p>
<details class="resource-details"><summary>Review, rights and research limits</summary>
<dl class="resource-facts">
<div><dt>Version or release</dt><dd>{esc(item['version'])}</dd></div>
<div><dt>What we reviewed</dt><dd>{esc(item['review_depth'])}</dd></div>
<div><dt>Access described in the record</dt><dd>{esc(item['access'])}</dd></div>
<div><dt>Current research decision</dt><dd>{esc(item['decision'])}</dd></div>
<div><dt>Limitations</dt><dd>{esc(item['limitations'])}</dd></div>
<div><dt>Attribution</dt><dd>{esc(item['attribution'])}</dd></div>
<div><dt>Declared license</dt><dd>{esc(rights['license'])}</dd></div>
<div><dt>License scope</dt><dd>{esc(rights['scope'])}</dd></div>
<div><dt>Stated conditions</dt><dd>{esc(rights['conditions'])}</dd></div>
<div><dt>Research use</dt><dd>{rights_status(rights['research_use'])}</dd></div>
<div><dt>Commercial use</dt><dd>{rights_status(rights['commercial_use'])}</dd></div>
<div><dt>Redistribution</dt><dd>{rights_status(rights['redistribution'])}</dd></div>
<div><dt>Rights evidence</dt><dd><a href="{https_href(rights['evidence_url'])}" rel="external noopener">Open the record used for this rights note ↗</a></dd></div>
<div><dt>Collection status</dt><dd>{acquisition_status(item['acquisition'])}</dd></div>
</dl></details></article>''')

    body = f'''<section class="page-intro section library-intro"><p class="eyebrow">THE RESOURCE DIRECTORY · {len(resources)} RECORDS</p><h1>Find what exists.<br><em>Know what it permits.</em></h1><p class="lede">Papers, datasets, code, models, standards and research projects connected to questions in animal communication and the wider living world. Each record shows what we reviewed, the next research decision and the limits we found.</p><p class="quiet">This is a curated working catalog, not a systematic review or legal clearance. A public link is not permission to download, redistribute, train on, or commercially use the underlying work.</p></section>
<nav class="section hub-nav" aria-label="Research library navigation"><a href="{base}/research/">Research notes</a><a href="{base}/research/starting-points/">Reading paths</a><a href="{base}/research/map/">Evidence connections</a><a href="{base}/contribute/source/">Suggest a resource</a></nav>
<section class="section resource-directory"><div class="resource-filters"><div><label for="resource-search">Search all resource details</label><input id="resource-search" type="search" placeholder="Try parrot, annotation, fungi…"></div><div><label for="resource-kind">Resource type</label><select id="resource-kind"><option value="all">All types</option>{kind_options}</select></div><div><label for="resource-research-use">Research-use assessment</label><select id="resource-research-use" aria-describedby="resource-rights-help"><option value="all">All assessments</option><option value="conditional">Conditional</option><option value="not_admitted">Not admitted to project</option><option value="unresolved">Unresolved · not cleared</option></select><small id="resource-rights-help">These are catalog notes, not permission. Conditional requires a scope and terms check; unresolved means not cleared.</small></div></div><div class="library-results-bar"><p id="resource-count" class="quiet" role="status" aria-live="polite">{len(resources)} resources · Search and filters are optional; all records are listed below.</p><button id="resource-reset" type="button" hidden>Clear filters</button></div><div id="resource-results">{''.join(entries)}</div><p id="resource-empty" hidden>No resources match. Clear the filters or try another phrase.</p></section>
<section class="section paper-panel resource-note"><h2>How to read these records.</h2><p>“Catalog reviewed” is the date our record was checked; it does not mean the paper or artifact received independent peer review from Talk2Nature. The review-depth field says exactly what was inspected.</p><p>Rights declarations apply only to the component and scope named in that record. “Conditional” is not blanket permission; “unresolved” means we have not established the terms; “not admitted” means this project has not cleared that use. Check current upstream terms and seek rights-holder guidance before reuse.</p><p>Sample approval controls a bounded metadata-collection workflow. It does not establish biological labels, participant consent, model-training suitability or benchmark readiness. We keep these separate from scientific admission.</p><p><a href="{base}/research/starting-points/">Follow a reading path to the next experiment →</a></p></section>'''
    page(
        'research/resources/',
        'Animal communication papers, datasets and methods',
        'Browse papers, datasets, code, models and standards for reproducible research on animal communication, with review depth, limits and reuse-rights notes.',
        body,
        active='research/',
        extra_head=f'<link rel="stylesheet" href="{base}/assets/resources.css"><script defer src="{base}/assets/resources.js"></script>',
    )
