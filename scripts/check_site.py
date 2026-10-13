"""Check generated pages for broken local links, metadata and accidental exposure."""
import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]; self.ids=set(); self.h1=0; self.title=''; self.in_title=False; self.in_head=False
        self.title_count=0; self.description_count=0; self.robots_count=0; self.canonical_count=0
        self.description=''; self.robots=''; self.canonical=''; self.lang=''
        self.structured_data=[]; self.in_structured_data=False
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='html': self.lang=attrs.get('lang','')
        if tag=='head': self.in_head=True
        if tag=='h1': self.h1+=1
        if tag=='title' and self.in_head:
            self.title_count+=1; self.in_title=True
        if attrs.get('id'): self.ids.add(attrs['id'])
        if tag=='meta' and self.in_head and attrs.get('name')=='description':
            self.description_count+=1; self.description=attrs.get('content','')
        if tag=='meta' and self.in_head and attrs.get('name')=='robots':
            self.robots_count+=1; self.robots=attrs.get('content','')
        if tag=='link' and self.in_head and attrs.get('rel')=='canonical':
            self.canonical_count+=1; self.canonical=attrs.get('href','')
        if tag=='script' and self.in_head and attrs.get('type')=='application/ld+json':
            self.structured_data.append(''); self.in_structured_data=True
        for attr in ('href','src'):
            if attrs.get(attr): self.links.append(attrs[attr])
    def handle_endtag(self,tag):
        if tag=='title' and self.in_head: self.in_title=False
        if tag=='script' and self.in_structured_data: self.in_structured_data=False
        if tag=='head': self.in_head=False
    def handle_data(self,data):
        if self.in_title: self.title+=data
        if self.in_structured_data and self.structured_data: self.structured_data[-1]+=data


def check_site(root):
    root=Path(root)
    resolved_root=root.resolve()
    info=json.loads((root/'build-info.json').read_text())
    base=urlsplit(info['base_url']); prefix=base.path.rstrip('/')
    parsed={}
    link_graph={}
    errors=[]
    for path in root.rglob('*.html'):
        doc=PageParser(); doc.feed(path.read_text()); parsed[path.resolve()]=doc
        if doc.h1 != 1: errors.append(f'{path}: expected one h1, got {doc.h1}')
        if not doc.title or not doc.description or doc.lang!='en': errors.append(f'{path}: missing title, description or language')
        if doc.title_count!=1: errors.append(f'{path}: expected one head title, got {doc.title_count}')
        if doc.description_count!=1: errors.append(f'{path}: expected one description meta tag, got {doc.description_count}')
        if doc.robots_count!=1: errors.append(f'{path}: expected one robots meta tag, got {doc.robots_count}')
        expected_canonical_count=1 if info['base_url'] else 0
        if doc.canonical_count!=expected_canonical_count: errors.append(f'{path}: expected {expected_canonical_count} canonical links, got {doc.canonical_count}')
        rel=path.relative_to(root).as_posix()
        public_page=info['public'] and rel!='404.html'
        if doc.robots!=('index,follow' if public_page else 'noindex,nofollow'): errors.append(f'{path}: incorrect robots metadata')
        if info['base_url']:
            expected=info['base_url']+'/'+(rel[:-10] if rel.endswith('index.html') else rel)
            if doc.canonical!=expected: errors.append(f'{path}: incorrect canonical URL')
        if public_page and not doc.structured_data: errors.append(f'{path}: missing JSON-LD structured metadata')
        for structured in doc.structured_data:
            try: json.loads(structured)
            except json.JSONDecodeError: errors.append(f'{path}: invalid JSON-LD structured metadata')
    titles=[d.title for d in parsed.values()]
    if len(set(titles))!=len(titles): errors.append('Duplicate page titles')
    public_descriptions=[doc.description for path,doc in parsed.items() if info['public'] and path.relative_to(resolved_root).as_posix()!='404.html']
    if len(set(public_descriptions))!=len(public_descriptions): errors.append('Duplicate public meta descriptions')
    for path,doc in parsed.items():
        linked_pages=set()
        for link in doc.links:
            ref=urlsplit(link)
            if ref.scheme or ref.netloc:
                if ref.scheme in ('javascript','data'): errors.append(f'{path}: unsafe link scheme')
                if ref.netloc != base.netloc or not base.netloc: continue
            if ref.path.startswith('/'):
                if prefix and not (ref.path==prefix or ref.path.startswith(prefix+'/')):
                    errors.append(f'{path}: link loses deployment prefix: {link}'); continue
                local=ref.path[len(prefix):].lstrip('/')
                target=root/local
            else:
                target=path.parent/unquote(ref.path) if ref.path else path
            if target.is_dir(): target=target/'index.html'
            if not target.exists(): errors.append(f'{path}: broken link {link}'); continue
            if target.suffix=='.html' and target.resolve() in parsed:
                linked_pages.add(target.resolve())
            if ref.fragment and target.suffix=='.html':
                target_doc=parsed.get(target.resolve())
                if target_doc and unquote(ref.fragment) not in target_doc.ids: errors.append(f'{path}: broken anchor {link}')
        link_graph[path]=linked_pages
    xml=ElementTree.parse(root/'sitemap.xml')
    sitemap_ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
    locations=[n.text or '' for n in xml.findall(f'.//{sitemap_ns}loc')]
    if info['public']:
        expected_locations={doc.canonical for path,doc in parsed.items() if path.relative_to(resolved_root).as_posix()!='404.html'}
        if len(locations)!=info['pages']: errors.append('Sitemap page count mismatch')
        if len(locations)!=len(set(locations)): errors.append('Sitemap contains duplicate URLs')
        if set(locations)!=expected_locations: errors.append('Sitemap URLs do not match canonical public HTML pages')
        home=(resolved_root/'index.html').resolve()
        public_pages={path for path in parsed if path.relative_to(resolved_root).as_posix()!='404.html'}
        if home not in public_pages:
            errors.append('Public homepage is missing')
            reachable=set()
        else:
            reachable={home}; pending=[home]
            while pending:
                current=pending.pop()
                for target in link_graph.get(current,()):
                    if target in public_pages and target not in reachable:
                        reachable.add(target); pending.append(target)
        unreachable=sorted(public_pages-reachable)
        for path in unreachable:
            errors.append(f'Public page is not reachable from homepage: {path.relative_to(resolved_root).as_posix()}')
    robots_lines=(root/'robots.txt').read_text().splitlines()
    if info['public']:
        if 'Disallow: /' in robots_lines: errors.append('Public site blocks crawlers')
        expected_sitemap=f'Sitemap: {info["base_url"]}/sitemap.xml'
        if expected_sitemap not in robots_lines: errors.append('Public robots.txt does not name the exact sitemap URL')
    elif 'Disallow: /' not in robots_lines:
        errors.append('Preview permits crawlers')
    forbidden={'.env','AGENTS.md','CLAUDE.md','build_audit.py'}
    for path in root.rglob('*'):
        if path.name in forbidden or path.suffix in {'.wav','.mp3','.mp4','.pdf','.py','.toml'} or 'funding' in path.relative_to(root).parts:
            errors.append(f'Unexpected private/source artifact in public output: {path}')
    if errors: raise ValueError('\n'.join(errors))
    result={'html_pages':len(parsed),'links_checked':sum(len(d.links) for d in parsed.values()),'public':info['public']}
    if info['public']:
        result['reachable_public_pages']=len(reachable)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('directory',nargs='?',type=Path,default=Path(__file__).resolve().parents[1]/'dist')
    args=parser.parse_args()
    try: print(json.dumps(check_site(args.directory),indent=2))
    except (ValueError,OSError) as error: parser.exit(1,str(error)+'\n')
