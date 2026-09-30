"""Build the Talk2Nature static site with the Python standard library."""
import argparse
import html
import json
import shutil
from pathlib import Path
from urllib.parse import urlsplit
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
DATE = '2026-09-30'


def esc(value):
    return html.escape(str(value), quote=True)


def load(name):
    return json.loads((ROOT / 'content' / f'{name}.json').read_text())


def validate_origin(value):
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.query or parsed.fragment or parsed.username or parsed.password:
        raise ValueError('Public base URL must be an HTTPS origin/path without credentials, query or fragment.')
    if any(x in parsed.hostname.lower() for x in ('example.', 'your-', 'localhost')):
        raise ValueError('Use the confirmed public URL, not a placeholder.')
    return value.rstrip('/')


def build(output, base_url='', public=False, repo_url=''):
    if public and not base_url:
        raise ValueError('A public build requires --base-url.')
    if base_url:
        base_url = validate_origin(base_url)
    if repo_url:
        repo_url = validate_origin(repo_url)
    prefix = urlsplit(base_url).path.rstrip('/') if base_url else ''
    def url(path=''):
        return f'{prefix}/{path}'

    notes, sources, opportunities = load('research'), load('sources'), load('opportunities')
    source_map = {s['id']: s for s in sources}
    publication = load('publication')
    if len({n['slug'] for n in notes}) != len(notes):
        raise ValueError('Duplicate research slug')
    for n in notes:
        for i in n['source_ids']:
            if i not in source_map:
                raise ValueError(f'Missing source {i}')
    output.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / 'web/assets', output / 'assets', dirs_exist_ok=True)
    pages = []
    nav_items = [('research/', 'Research library'), ('field-notes/', 'Field Notes'), ('approach/', 'Our approach'), ('roadmap/', 'Roadmap'), ('opportunities/', 'Funding')]

    def page(path, title, description, body, active='', noindex=False, extra_head=''):
        canonical = f'{base_url}/{path}' if base_url else ''
        indexing = public and not noindex
        meta = f'<link rel="canonical" href="{esc(canonical)}">' if canonical else ''
        if public and not path and base_url == publication['base_url']:
            meta += f'<meta name="google-site-verification" content="{esc(publication["google_site_verification"])}">'
        if base_url:
            meta += f'<meta property="og:url" content="{esc(canonical)}"><meta property="og:image" content="{esc(base_url)}/assets/social.svg">'
        structured = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': title, 'description': description, 'inLanguage': 'en'}
        if canonical:
            structured['url'] = canonical
        nav = ''.join(f'<a href="{url(p)}"'+(' aria-current="page"' if active == p else '')+f'>{label}</a>' for p, label in nav_items)
        repo = f'<a href="{esc(repo_url)}">Source repository ↗</a>' if repo_url else f'<a href="{url("contribute/")}">Building in the open ↗</a>'
        document = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · Talk2Nature</title><meta name="description" content="{esc(description)}">
<meta name="robots" content="{'index,follow' if indexing else 'noindex,nofollow'}"><meta name="theme-color" content="#193f35">
<meta property="og:type" content="website"><meta property="og:site_name" content="Talk2Nature"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}">{meta}
<link rel="icon" href="{url('assets/mark.svg')}" type="image/svg+xml"><link rel="stylesheet" href="{url('assets/style.css')}">
<script type="application/ld+json">{json.dumps(structured).replace('<', chr(92)+'u003c')}</script><script defer src="{url('assets/site.js')}"></script>{extra_head}</head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="header"><a class="brand" href="{url()}"><img src="{url('assets/mark.svg')}" alt="" width="32" height="32">Talk2Nature<span class="brand-dot" aria-hidden="true">✳</span></a>
<button class="menu-toggle" aria-expanded="false" aria-controls="navigation">Menu <span aria-hidden="true">＋</span></button><nav id="navigation" aria-label="Main navigation">{nav}<a class="nav-cta" href="{url('contribute/')}">Get involved <span aria-hidden="true">↗</span></a></nav></header>
<main id="main">{body}</main>
<footer><div class="footer-top"><a class="brand footer-brand" href="{url()}">Talk2Nature</a><p>A shared curiosity.<br>A careful way forward.</p></div>
<div class="footer-bottom"><span>Independent initiative · Founded 2026</span><div>{repo}<a href="{url('sources/')}">Sources</a><a href="{url('about/')}">About & privacy</a></div></div>
<p class="fine">Original summaries: CC BY 4.0 · Original software: Apache-2.0. Third-party works keep their own rights. Listed organizations are not implied partners.</p></footer></body></html>'''
        target = output / (path + 'index.html' if path.endswith('/') or not path else path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(document)
        if not noindex:
            pages.append(path)

    def card(n):
        return f'''<article class="research-card" data-taxon="{esc(n['taxon'])}" data-search="{esc(' '.join([n['title'],n['taxon'],n['finding'],n['kind']]).lower())}">
<div class="card-meta"><span>{esc(n['taxon'])}</span><span>{esc(n['year'])}</span></div><h3><a href="{url('research/'+n['slug']+'/')}">{esc(n['title'])}</a></h3><p>{esc(n['finding'])}</p><p class="review-stage">{esc(n['review_stage'])}</p><div class="card-foot"><span>{esc(n['kind'])}</span><a href="{url('research/'+n['slug']+'/')}" aria-label="Read {esc(n['title'])}">Read note ↗</a></div></article>'''

    page('', 'Understanding the living world', 'Explore the science of animal communication, bioacoustic AI and nature’s signals. A research library and open tools, built with evidence.', f'''
<section class="hero"><div class="hero-copy"><p class="eyebrow"><span class="status-dot"></span> An open invitation to listen</p><h1>The living world<br> has a lot<br>to <em>say.</em></h1><p class="hero-intro">What could we understand if we listened more closely? We’re bringing research, people and open tools together to explore communication beyond our own species.</p><div class="actions"><a class="button" href="{url('research/')}">Explore the research <span>↗</span></a><a class="text-link" href="{url('approach/')}">Discover our approach →</a></div><p class="hero-note">A bold question. A careful, evidence-led beginning.</p></div>
<div class="hero-art"><img src="{url('assets/listening.svg')}" alt="An abstract bird and leaf connected by illustrated sound waves" width="620" height="690"><div class="art-caption"><span>FIELD NOTE 001</span><p>Understanding starts<br>with paying attention.</p><span class="caption-star" aria-hidden="true">✳</span></div></div></section>
<div class="species-strip" aria-label="Research interests"><span>Birds</span><i>✳</i><span>Animals</span><i>✳</i><span>Marine life</span><i>✳</i><span>Plants</span><i>✳</i><span>Fungi</span></div>
<section class="intro-section section"><p class="eyebrow">THE QUESTION THAT BRINGS US HERE</p><h2>Can we learn to understand<br>the nature around us?</h2><div class="intro-grid"><p>Animals exchange signals. Plants respond to their environments. Researchers are uncovering patterns we once missed. Our ambition is to help turn curiosity into shared, testable understanding.</p><p>We begin with a simple discipline: document what is known, be clear about what isn’t, and build on the work of others. A translation claim needs more than a convincing prediction.</p></div></section>
<section class="library-section section"><div class="section-heading"><div><p class="eyebrow">THE RESEARCH LIBRARY</p><h2>Follow the evidence.</h2></div><a class="text-link" href="{url('research/')}">All research notes ↗</a></div><div class="cards">{''.join(card(n) for n in (notes[0],notes[3],notes[10]))}</div><p class="quiet">{len(notes)} starting notes · {len(sources)} sources in the research inventory · Review depth shown on every note</p></section>
<section class="approach-band section"><div><p class="eyebrow">OUR FIRST STEPS</p><h2>Listen. Observe.<br>Test. Share.</h2><p>One species. One clear question. A result others can examine and build on.</p><a class="button light" href="{url('roadmap/')}">See the roadmap ↗</a></div><ol><li><span>01</span><div><h3>Map what’s known</h3><p>Bring studies, models and methods into an honest, useful research library.</p></div></li><li><span>02</span><div><h3>Start with birds</h3><p>Define a passive observation pilot with a scientific collaborator. A parrot study is one candidate.</p></div></li><li><span>03</span><div><h3>Build something testable</h3><p>Use transparent data practices and meaningful baselines before making claims about meaning.</p></div></li></ol></section>
<section class="join-section section"><p class="eyebrow">THERE’S ROOM FOR YOUR CURIOSITY</p><h2>A question this big<br>takes <em>many minds.</em></h2><p>Researchers, developers, naturalists and thoughtful skeptics: help shape the next experiment.</p><a class="button" href="{url('contribute/')}">Find your way to contribute ↗</a></section>''')

    page('field-notes/', 'Field Notes: an animal observation research app', 'A mobile-first web app in development for guided animal observations, study protocols and reviewed research contributions.', f'''
<section class="page-intro section"><p class="eyebrow">FIELD NOTES · IN DEVELOPMENT</p><h1>Notice a moment.<br><em>Build understanding.</em></h1><p class="lede">A companion for observing animals carefully, following a study protocol and turning everyday moments into evidence researchers can examine.</p><div class="actions"><a class="button" href="{url('field-notes/demo/')}">Try the Field Notes demo <span aria-hidden="true">↗</span></a><span class="quiet">Invented examples · No account needed</span></div><aside class="review-box"><strong>Try the public demo; the research app is still a private, local prototype.</strong><p>The demo runs in your browser and saves nothing to our research database. Public accounts, recording uploads and animal translation are not available.</p></aside></section>
<section class="section cards contribution-cards"><article><p class="eyebrow">01 / CHOOSE A QUESTION</p><h2>One study at a time.</h2><p>A defined species, observable behavior and short protocol. Know what to observe, what to leave unknown and when to stop.</p></article><article><p class="eyebrow">02 / OBSERVE FIRST</p><h2>Describe what happened.</h2><p>Keep the animal, session and observation connected. Record visible behavior before seeing any model prediction. Short, reviewed clips are a later step.</p></article><article><p class="eyebrow">03 / LEARN TOGETHER</p><h2>Review before reuse.</h2><p>Check rights, privacy and label quality. Separate permission for private review, research training and possible publication. Make withdrawal part of the workflow.</p></article></section>
<section class="section paper-panel"><p class="eyebrow">A USEFUL FIRST EXPERIMENT</p><h2>Does sound add information?</h2><p>Our first proposed question is whether acoustic features improve prediction of an independently observed behavior on animals and sessions the model has never seen. A parrot dataset is being assessed for this purpose.</p><p>A model associating a sound with feeding would not establish that the animal said “I am hungry.” Claims about meaning need additional controlled evidence.</p><a class="text-link" href="{url('research/parrot-data-feasibility/')}">Read the parrot data assessment →</a></section>
<section class="section intro-section"><p class="eyebrow">BUILT AROUND A RESEARCH RECORD</p><h2>Keep the evidence connected.</h2><div class="intro-grid"><p>The planned research database connects papers, code, datasets, study protocols, sessions, observations, permissions and review decisions. Recordings will need separate private storage, linked to those records by checksums and access rules.</p><p>We start with a phone-friendly web app. Native background recording, spare-phone stations and a paired TV display are later options, each with its own device and welfare testing. Initial studies use passive observation; no automatic playback.</p></div></section>
<section class="section join-section"><p class="eyebrow">HELP SHAPE THE FIRST STUDY</p><h2>Make the next step<br><em>worth measuring.</em></h2><p>Research protocols, annotation workflows and careful code reviews are useful contributions now. Please keep private recordings and personal information out of public issues.</p><a class="button" href="{url('contribute/')}">Help build Field Notes ↗</a></section>''', active='field-notes/')

    demo_body = (ROOT / 'web/templates/field-notes-demo.html').read_text().replace('{{base}}', prefix)
    page('field-notes/demo/', 'Try Field Notes: a guided observation demo', 'Explore an invented animal observation, separate reuse permissions, human review and withdrawal in the Field Notes interactive demo.', demo_body, active='field-notes/', extra_head=f'<link rel="stylesheet" href="{url("assets/demo.css")}"><script type="module" src="{url("assets/demo.js")}"></script>')

    taxons = sorted({n['taxon'] for n in notes})
    page('research/', 'Animal communication research library', 'Cited evidence notes on birds, whales, plants, fungi and bioacoustic machine learning, with study limitations and transparent review depth.', f'''
<section class="page-intro section"><p class="eyebrow">THE RESEARCH LIBRARY</p><h1>What we know.<br><em>What we’re learning.</em></h1><p class="lede">A growing map of nonhuman communication research. Each note separates a finding from its limits and asks what we can learn from it.</p><p class="quiet">This is a curated starting collection, not a systematic review. Most primary papers still need a full methods review and specialist checking.</p></section>
<section class="section library-browser"><div class="filters"><div><label for="research-search">Search the library</label><input id="research-search" type="search" placeholder="Try birds, signals, machine learning…"></div><div><label for="taxon-filter">Research area</label><select id="taxon-filter"><option value="all">All research areas</option>{''.join(f'<option>{esc(t)}</option>' for t in taxons)}</select></div></div><p id="result-count" class="quiet" role="status" aria-live="polite">{len(notes)} research notes</p><div class="cards" id="research-results">{''.join(card(n) for n in notes)}</div><p id="no-results" hidden>No notes match this search. Try another phrase or choose all research areas.</p><a class="text-link" href="{url('sources/')}">Browse the full source inventory →</a></section>''', active='research/')
    for n in notes:
        refs = ''
        for i in n['source_ids']:
            source = source_map[i]
            review_link = f'<p><a href="{esc(source["review_url"])}">{esc(source["review_url_label"])} ↗</a></p>' if source.get('review_url') else ''
            refs += f'<li><a href="{esc(source["url"])}">{esc(source["title"])} ↗</a><p>{esc(source["description"])}</p>{review_link}</li>'
        study = ''
        if n.get('study_snapshot'):
            rows = ''.join(f'<div><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>' for label,value in n['study_snapshot'])
            study = f'<section class="study-snapshot"><h2>Study at a glance</h2><dl>{rows}</dl><p class="fine">Reading location: {esc(n["review_locator"])}</p></section>'
        page(f'research/{n["slug"]}/', n['title'], n['finding'], f'''
<article class="article section"><a class="back-link" href="{url('research/')}">← Research library</a><p class="eyebrow">{esc(n['taxon'])} / {esc(n['kind'])}</p><h1>{esc(n['title'])}</h1><p class="article-date">{esc(n['year_label'])} {esc(n['year'])} · Note reviewed {esc(n['reviewed'])}</p><p class="lede">{esc(n['finding'])}</p><aside class="review-box"><strong>What we reviewed · {esc(n['review_stage'])}</strong><p>{esc(n['review_depth'])}</p><p>{esc(n['expert_review'])}</p></aside>{study}<h2>What this does — and doesn’t — establish</h2><p>{esc(n['limitations'])}</p><h2>What we can build on</h2><p>{esc(n['lesson'])}</p><h2>The next reading task</h2><p>{esc(n['next_review'])}</p><h2>Go to the sources</h2><ol class="source-list">{refs}</ol><p class="fine">Original editorial note by Talk2Nature contributors. AI-assisted, source-grounded synthesis; not a peer review or an independent replication. Linked works retain their own rights.</p></article>''', active='research/')

    levels = [('Detection','A signal occurred.'),('Identification','A model or observer identifies the source.'),('Association','A signal is associated with an observed context.'),('Meaning','Controlled receiver responses support a bounded interpretation.'),('Shared exchange','A specific two-way interaction is demonstrated.'),('General translation','An ambitious goal, not a capability established by this project.')]
    page('approach/', 'Our approach to animal communication AI', 'How Talk2Nature separates signal detection, association and meaning, and designs reproducible, welfare-conscious bioacoustic research.', f'''
<section class="page-intro section"><p class="eyebrow">OUR APPROACH</p><h1>Big curiosity.<br><em>Careful claims.</em></h1><p class="lede">Progress starts by asking a question that can be answered — and being willing to hear an unexpected result.</p></section><section class="section two-column"><div><h2>Not every pattern<br>is a translation.</h2><p>A recording can reveal identity, timing or context without revealing what an animal means. We use an evidence ladder to make those differences visible.</p><p>Our initial experiment will study observable context. Any later test of meaning needs receiver behavior and qualified scientific oversight.</p></div><ol class="evidence-ladder">{''.join(f'<li><span>0{i}</span><div><h3>{name}</h3><p>{text}</p></div></li>' for i,(name,text) in enumerate(levels,1))}</ol></section>
<section class="section paper-panel"><p class="eyebrow">THE FIRST TECHNICAL QUESTION</p><h2>Does sound add useful information?</h2><p class="lede">For one chosen species, can acoustic features improve prediction of a pre-defined observable context on held-out recordings?</p><div class="cards"><div><h3>Observe independently</h3><p>Label behavior from synchronized observations. Retain disagreement and unknowns; avoid deriving labels from the same sound a model sees.</p></div><div><h3>Keep evaluation honest</h3><p>Separate related recordings, individuals and sessions. Compare context-only, background and shuffled-label baselines.</p></div><div><h3>Publish the limits</h3><p>Report per-class errors, coverage, uncertainty and review effort. A failed hypothesis is still a useful result.</p></div></div></section>
<section class="section two-column"><div><h2>Open tools.<br>Responsible data.</h2><p>Our original code is licensed under Apache-2.0. Original research summaries use CC BY 4.0. Recordings and model weights require their own rights checks.</p></div><div><h3>Passive observation first</h3><p>No automated playback in the initial public tools. No disturbing an animal to produce a label. A pilot needs a scientific collaborator, a stopping protocol and consent for any human data.</p><h3>Start with a trustworthy manifest</h3><p>The first code milestone validates recording metadata and keeps connected individuals, sessions and source hashes together when splitting data. Synthetic examples test the software; no animal model has been trained.</p><a class="text-link" href="{url('contribute/')}">Help improve the method →</a></div></section>''', active='approach/')
    milestones = [('Now','Establish the foundation','An evidence library, working brand, project scope and tested metadata tools. The public research library and repository provide the starting point for collaboration.'),('Next','Choose one question','Recruit a scientific collaborator, review the highest-value papers and compare existing workflows. Confirm species, data rights and an observable outcome.'),('Pilot','Collect and learn','Start with a small passive observation study. Review labels, compare simple baselines and test generalization on independent recordings.'),('Then','Share what holds up','Publish the protocol, evaluation and limitations. Seek a funded continuation if the evidence and user need support it.')]
    page('roadmap/', 'Roadmap and open research questions', 'The Talk2Nature plan: a research library, a focused bird-communication pilot, reproducible evaluation and a path to funded open work.', f'''
<section class="page-intro section"><p class="eyebrow">THE ROADMAP</p><h1>A long view.<br><em>A concrete beginning.</em></h1><p class="lede">We’re at the foundation stage. No scientific partnership, funded grant, real dataset or trained Talk2Nature model is being claimed.</p></section><section class="section timeline">{''.join(f'<article><span class="pill">{phase}</span><div><h2>{title}</h2><p>{text}</p></div></article>' for phase,title,text in milestones)}</section><section class="section paper-panel"><h2>Questions still open</h2><ul class="readable-list"><li>Which species and observation setting give us reliable access and a meaningful scientific question?</li><li>Can existing tools already solve the workflow problem? Would contributing upstream help more?</li><li>Is a parrot study a useful starting point? An existing Kiki app has been mentioned but not inspected or incorporated.</li><li>What value would a research group fund: annotation support, a managed pilot or a hosted workspace?</li></ul><p>Plants and fungi stay in the library. Our first experiment will have a narrower scope.</p></section>''', active='roadmap/')
    opp_cards = ''.join(f'''<article class="opportunity"><div><span class="pill">{esc(o['status'])}</span><h2>{esc(o['name'])}</h2><p class="quiet">{esc(o['type'])} · {'Deadline '+esc(o['deadline']) if o['deadline'] else 'No fixed open deadline verified'}</p></div><div><p><strong>{esc(o['amount'])}</strong></p><p>{esc(o['fit'])}</p><p>{esc(o['next_action'])}</p><a class="text-link" href="{esc(source_map[o['source_id']]['url'])}">Official program ↗</a><p class="fine">Checked {esc(o['verified'])} · {esc(o['application_status'])}</p></div></article>''' for o in opportunities)
    page('opportunities/', 'Funding and prizes for animal communication research', 'A dated register of research prizes, grants, crowdfunding and compute credits, with eligibility and closed-call distinctions.', f'''
<section class="page-intro section"><p class="eyebrow">FUNDING THE WORK</p><h1>Ambition needs<br><em>room to grow.</em></h1><p class="lede">A practical register of opportunities that could support careful research. Availability and eligibility are different questions.</p><aside class="review-box"><strong>Snapshot: September 30, 2026</strong><p>Program terms can change. Follow the official source before applying. No application has been submitted and no funding is secured. Credits are not cash.</p></aside></section><section class="section opportunity-list">{opp_cards}</section>''', active='opportunities/')
    repo_action = f'<a class="button" href="{esc(repo_url)}/issues">Open an issue ↗</a>' if repo_url else '<p class="quiet">The public repository and contribution channel are being prepared. This preview does not collect personal details.</p>'
    page('contribute/', 'Contribute to Talk2Nature', 'Help review evidence, improve research tools or shape a focused nonhuman communication pilot.', f'''
<section class="page-intro section"><p class="eyebrow">GET INVOLVED</p><h1>Bring a skill.<br><em>Bring a question.</em></h1><p class="lede">The most useful first contribution is small, specific and something another person can verify.</p>{repo_action}</section><section class="section cards contribution-cards"><article><span class="eyebrow">RESEARCHERS</span><h2>Review a claim.</h2><p>Help examine a study’s methods, boundaries and relevance to a possible bird-communication pilot. Specialist review is still needed.</p></article><article><span class="eyebrow">DEVELOPERS</span><h2>Strengthen a tool.</h2><p>Improve metadata validation, reproducibility or compatibility with existing annotation tools. Begin with a testable issue.</p></article><article><span class="eyebrow">NATURALISTS & SUPPORTERS</span><h2>Ground the question.</h2><p>Describe a real observation workflow or a research need. We are not yet accepting raw animal recordings or donations.</p></article></section><section class="section paper-panel"><h2>How we work together</h2><p>Credit the people and studies behind the work. Share original summaries, not copied articles. State uncertainty. Respect animal welfare, privacy and sensitive locations. Correct mistakes openly.</p><p>Organizations in the library are references and possible connections; none is presented as a confirmed Talk2Nature partner.</p></section>''')
    page('sources/', 'Source inventory', f'The Talk2Nature inventory of {len(sources)} research papers, organizations, model documentation and funding sources.', f'''
<section class="page-intro section"><p class="eyebrow">PROVENANCE</p><h1>Follow every<br><em>thread back.</em></h1><p class="lede">{len(sources)} sources from the founding audit and subsequent reading. Inclusion does not mean a full paper was read or a claim independently replicated. Review depth is recorded in the research notes.</p></section><section class="section"><ol class="source-list inventory">{''.join(f'<li id="source-{s["id"]}"><a href="{esc(s["url"])}">{esc(s["title"])} ↗</a><p>{esc(s["description"])}</p></li>' for s in sources)}</ol></section>''')
    page('about/', 'About, editorial policy and privacy', 'Who Talk2Nature is for, how evidence is documented, and how this early-stage site handles privacy and attribution.', f'''
<article class="article section"><p class="eyebrow">ABOUT THE PROJECT</p><h1>Curiosity, with<br><em>care.</em></h1><p class="lede">Talk2Nature is an early-stage independent initiative founded by Raviv to explore a question: how can people better understand communication in the living world?</p><h2>Where we stand</h2><p>The project is establishing its scope, tools and scientific connections. Talk2Nature is a working name; no registered legal entity, scientific advisory board or confirmed institutional partnership is represented here.</p><h2>Our editorial promise</h2><p>Each research note links to its sources, describes what was actually reviewed and separates findings from limitations. AI helps draft and organize material; that is not a substitute for specialist review. The initial notes have not yet received independent scientific review.</p><h2>Open work and a sustainable project</h2><p>Original code uses Apache-2.0 and original public summaries use CC BY 4.0. Third-party works and model weights retain separate terms. Managed research pilots or hosting may eventually support the project; no paid service or donation program is currently offered.</p><h2>Privacy</h2><p>This version has no sign-up form, analytics script, advertising, cookies set by the site, or audio-upload function. Search runs in your browser. The public website is hosted by GitHub Pages. GitHub may process technical request information, including IP addresses, under its <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">privacy statement</a>. External links take you to independently operated websites.</p><h2>Corrections</h2><p>Report a correction through the <a href="{esc(repo_url) + "/issues" if repo_url else url("contribute/")}">project contribution channel</a>. Please include the claim, a primary source and the proposed correction. Do not submit private recordings, sensitive locations or personal information in public issues.</p></article>''')
    page('404.html', 'Page not found', 'This Talk2Nature page could not be found.', f'<section class="page-intro section"><p class="eyebrow">404 / AN UNFAMILIAR PATH</p><h1>Let’s find<br><em>our way back.</em></h1><p><a class="button" href="{url()}">Back to the project →</a></p></section>', noindex=True)
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{xml_escape(base_url+"/"+p)}</loc><lastmod>{DATE}</lastmod></url>' for p in pages if base_url) + '</urlset>\n'
    (output/'sitemap.xml').write_text(sitemap)
    (output/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n' if public else 'User-agent: *\nDisallow: /\n')
    (output/'.nojekyll').write_text('')
    (output/'build-info.json').write_text(json.dumps({'public':public,'base_url':base_url,'repo_url':repo_url,'editorial_date':DATE,'pages':len(pages),'research_notes':len(notes),'sources':len(sources)},indent=2)+'\n')
    return len(pages)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'dist')
    parser.add_argument('--base-url',default='')
    parser.add_argument('--repo-url',default='')
    parser.add_argument('--public',action='store_true')
    args = parser.parse_args()
    try:
        count = build(args.output,args.base_url,args.public,args.repo_url)
    except ValueError as error:
        parser.error(str(error))
    print(f'Built {count} pages plus 404 in {args.output} ({"public" if args.public else "local noindex"}).')
