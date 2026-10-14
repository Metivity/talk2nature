"""Verify core routes and crawl metadata after a GitHub Pages deployment."""
import argparse
import json
import time
import urllib.error
import urllib.request
from urllib.parse import urljoin, urlsplit, urlunsplit
from xml.etree import ElementTree

try:
    from scripts.check_site import PageParser
except ModuleNotFoundError:
    # Support both `python3 -m scripts.check_live_site` and direct script execution.
    from check_site import PageParser


HTML_PATHS = ("", "app/", "research/resources/")


class LiveCheckError(RuntimeError):
    """A deployed route does not yet satisfy the public release contract."""


def normalize_base_url(value):
    parsed = urlsplit(value.strip())
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("base URL must be an HTTPS origin/path without credentials, query or fragment")
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", ""))


def fetch_text(url, timeout):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Talk2Nature-live-release-check/1.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8")
        return response.status, response.headers.get_content_type(), body, response.geturl()


def _read(fetch, url, expected_type, timeout):
    status, content_type, body, final_url = fetch(url, timeout)
    if status != 200:
        raise LiveCheckError(f"{url}: expected HTTP 200, received {status}")
    if final_url != url:
        raise LiveCheckError(f"{url}: unexpected redirect to {final_url}")
    if content_type not in expected_type:
        raise LiveCheckError(f"{url}: unexpected content type {content_type}")
    return body


def check_once(base_url, fetch=fetch_text, timeout=8):
    base_url = normalize_base_url(base_url)
    root_url = base_url + "/"
    checked_pages = []
    for path in HTML_PATHS:
        url = urljoin(root_url, path)
        body = _read(fetch, url, {"text/html"}, timeout)
        page = PageParser()
        page.feed(body)
        if page.title_count != 1 or not page.title.strip():
            raise LiveCheckError(f"{url}: missing a unique, non-empty title")
        if page.description_count != 1 or not page.description.strip():
            raise LiveCheckError(f"{url}: missing a unique, non-empty description")
        if page.canonical_count != 1 or page.canonical != url:
            raise LiveCheckError(f"{url}: canonical URL is missing or does not match the live route")
        if page.robots_count != 1 or page.robots != "index,follow":
            raise LiveCheckError(f"{url}: route is not explicitly indexable")
        checked_pages.append(url)

    sitemap_url = urljoin(root_url, "sitemap.xml")
    sitemap_body = _read(fetch, sitemap_url, {"application/xml", "text/xml"}, timeout)
    try:
        sitemap_root = ElementTree.fromstring(sitemap_body)
    except ElementTree.ParseError as exc:
        raise LiveCheckError(f"{sitemap_url}: invalid XML ({exc})") from exc
    if sitemap_root.tag.rsplit("}", 1)[-1] != "urlset":
        raise LiveCheckError(f"{sitemap_url}: expected a sitemap urlset")
    sitemap_urls = {
        (element.text or "").strip()
        for element in sitemap_root.iter()
        if element.tag.rsplit("}", 1)[-1] == "loc"
    }
    missing = sorted(set(checked_pages) - sitemap_urls)
    if missing:
        raise LiveCheckError(f"{sitemap_url}: missing required routes: {', '.join(missing)}")

    robots_url = urljoin(root_url, "robots.txt")
    robots_body = _read(fetch, robots_url, {"text/plain"}, timeout)
    expected_sitemap_line = f"Sitemap: {sitemap_url}"
    if expected_sitemap_line not in {line.strip() for line in robots_body.splitlines()}:
        raise LiveCheckError(f"{robots_url}: does not name {sitemap_url}")
    if "Disallow: /" in {line.strip() for line in robots_body.splitlines()}:
        raise LiveCheckError(f"{robots_url}: blocks all crawlers")

    return {
        "base_url": base_url,
        "pages_verified": len(checked_pages),
        "sitemap_urls": len(sitemap_urls),
        "robots_names_sitemap": True,
    }


def verify_live_site(base_url, attempts=8, interval=5, timeout=5, fetch=fetch_text, sleep=time.sleep):
    base_url = normalize_base_url(base_url)
    if attempts < 1 or interval < 0 or timeout <= 0:
        raise ValueError("attempts must be positive; interval must be nonnegative; timeout must be positive")
    last_error = None
    for attempt in range(attempts):
        try:
            return check_once(base_url, fetch=fetch, timeout=timeout)
        except (OSError, LiveCheckError, UnicodeDecodeError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                sleep(interval)
    raise LiveCheckError(f"live check failed after {attempts} attempts: {last_error}") from last_error


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="HTTPS GitHub Pages deployment URL")
    parser.add_argument("--attempts", type=int, default=8)
    parser.add_argument("--interval", type=float, default=5)
    parser.add_argument("--timeout", type=float, default=5)
    args = parser.parse_args(argv)
    try:
        result = verify_live_site(
            args.base_url,
            attempts=args.attempts,
            interval=args.interval,
            timeout=args.timeout,
        )
    except (ValueError, LiveCheckError) as exc:
        parser.exit(1, f"Live site verification failed: {exc}\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
