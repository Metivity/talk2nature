"""Version public assets and their relative dependencies as one compatible set."""
import hashlib
import re


def copy_assets(source, target):
    files = sorted(p for p in source.iterdir() if p.is_file())
    revision = hashlib.sha256(b'asset-urls-v1\0' + b''.join(
        p.name.encode() + b'\0' + p.read_bytes() + b'\0' for p in files)).hexdigest()[:16]
    names = {p.name for p in files}
    target.mkdir(parents=True, exist_ok=True)
    for path in files:
        if path.suffix in {'.js', '.mjs', '.css'}:
            def dependency(match):
                quote, name = match.groups()
                if name not in names:
                    raise ValueError(f'Missing asset dependency: {name}')
                return f'{quote}./{name}?v={revision}{quote}'
            text = re.sub(r'''(['"])\./([\w.-]+\.(?:m?js|css|svg))\1''', dependency, path.read_text())
            (target/path.name).write_text(text)
        else:
            (target/path.name).write_bytes(path.read_bytes())
    return revision


def version_html(document, prefix, revision):
    pattern = r'((?:href|src)="' + re.escape(prefix+'/assets/') + r'[\w.-]+)(")'
    return re.sub(pattern, lambda m: f'{m[1]}?v={revision}{m[2]}', document)
