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
        self.links=[]; self.ids=set(); self.h1=0; self.title=''; self.in_title=False
        self.description=''; self.robots=''; self.canonical=''; self.lang=''
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='html': self.lang=attrs.get('lang','')
        if tag=='h1': self.h1+=1
        if tag=='title': self.in_title=True
        if attrs.get('id'): self.ids.add(attrs['id'])
        if tag=='meta' and attrs.get('name')=='description': self.description=attrs.get('content','')
        if tag=='meta' and attrs.get('name')=='robots': self.robots=attrs.get('content','')
        if tag=='link' and attrs.get('rel')=='canonical': self.canonical=attrs.get('href','')
        for attr in ('href','src'):
            if attrs.get(attr): self.links.append(attrs[attr])
    def handle_endtag(self,tag):
        if tag=='title': self.in_title=False
    def handle_data(self,data):
        if self.in_title: self.title+=data


def check_site(root):
    root=Path(root)
    info=json.loads((root/'build-info.json').read_text())
    base=urlsplit(info['base_url']); prefix=base.path.rstrip('/')
    parsed={}
    errors=[]
    for path in root.rglob('*.html'):
        doc=PageParser(); doc.feed(path.read_text()); parsed[path.resolve()]=doc
        if doc.h1 != 1: errors.append(f'{path}: expected one h1, got {doc.h1}')
        if not doc.title or not doc.description or doc.lang!='en': errors.append(f'{path}: missing title, description or language')
        rel=path.relative_to(root).as_posix()
        public_page=info['public'] and rel!='404.html'
        if doc.robots!=('index,follow' if public_page else 'noindex,nofollow'): errors.append(f'{path}: incorrect robots metadata')
        if info['base_url']:
            expected=info['base_url']+'/'+(rel[:-10] if rel.endswith('index.html') else rel)
            if doc.canonical!=expected: errors.append(f'{path}: incorrect canonical URL')
    titles=[d.title for d in parsed.values()]
    if len(set(titles))!=len(titles): errors.append('Duplicate page titles')
    for path,doc in parsed.items():
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
            if ref.fragment and target.suffix=='.html':
                target_doc=parsed.get(target.resolve())
                if target_doc and unquote(ref.fragment) not in target_doc.ids: errors.append(f'{path}: broken anchor {link}')
    xml=ElementTree.parse(root/'sitemap.xml')
    locations=[n.text for n in xml.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    if info['public'] and len(locations)!=info['pages']: errors.append('Sitemap page count mismatch')
    if info['public'] and 'Disallow: /' in (root/'robots.txt').read_text(): errors.append('Public site blocks crawlers')
    if not info['public'] and 'Disallow: /' not in (root/'robots.txt').read_text(): errors.append('Preview permits crawlers')
    forbidden={'.env','AGENTS.md','CLAUDE.md','build_audit.py'}
    for path in root.rglob('*'):
        if path.name in forbidden or path.suffix in {'.wav','.mp3','.mp4','.pdf','.py','.toml'} or 'funding' in path.relative_to(root).parts:
            errors.append(f'Unexpected private/source artifact in public output: {path}')
    if errors: raise ValueError('\n'.join(errors))
    return {'html_pages':len(parsed),'links_checked':sum(len(d.links) for d in parsed.values()),'public':info['public']}


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('directory',nargs='?',type=Path,default=Path(__file__).resolve().parents[1]/'dist')
    args=parser.parse_args()
    try: print(json.dumps(check_site(args.directory),indent=2))
    except (ValueError,OSError) as error: parser.exit(1,str(error)+'\n')
