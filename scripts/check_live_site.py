"""Verify core routes and every sitemap page after a GitHub Pages deployment."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, urlunsplit
from xml.etree import ElementTree

try:
    from scripts.check_site import PageParser
except ModuleNotFoundError:
    # Support both `python3 -m scripts.check_live_site` and direct script execution.
    from check_site import PageParser


HTML_PATHS = (
    "",
    "contribute/",
    "app/",
    "app/station/",
    "app/compare/",
    "tools/listen/",
    "tools/annotation-compare/",
    "research/resources/",
)


class LiveCheckError(RuntimeError):
    """A deployed route does not yet satisfy the public release contract."""


class _VisibleContentParser(HTMLParser):
    """Collect visible page copy and links for small post-deploy contracts."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text = []
        self.anchors = []
        self.controls = {}
        self._anchor = None
        self._control = None
        self._hidden_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"script", "style", "template"}:
            self._hidden_depth += 1
        if tag == "a":
            self._anchor = {
                "href": attrs.get("href", ""),
                "classes": set(attrs.get("class", "").split()),
                "text": [],
            }
        if tag in {"button", "input"} and attrs.get("id"):
            self._control = {
                "tag": tag,
                "attributes": attrs,
                "text": [],
            }
            self.controls[attrs["id"]] = self._control

    def handle_endtag(self, tag):
        if tag in {"script", "style", "template"} and self._hidden_depth:
            self._hidden_depth -= 1
        if tag == "a" and self._anchor is not None:
            self._anchor["text"] = _normalize_copy(" ".join(self._anchor["text"]))
            self.anchors.append(self._anchor)
            self._anchor = None
        if tag == "button" and self._control is not None and self._control["tag"] == "button":
            self._control["text"] = _normalize_copy(" ".join(self._control["text"]))
            self._control = None

    def handle_data(self, data):
        if self._hidden_depth:
            return
        self.text.append(data)
        if self._anchor is not None:
            self._anchor["text"].append(data)
        if self._control is not None:
            self._control["text"].append(data)


def _normalize_copy(value):
    return re.sub(r"\s+", " ", value).strip()


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


def _verify_live_page(url, fetch, timeout):
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
    return body


def _validate_sitemap_route(url, base_url):
    route = urlsplit(url)
    base = urlsplit(base_url)
    prefix = base.path.rstrip("/")
    if (
        route.scheme != "https"
        or route.netloc.lower() != base.netloc.lower()
        or route.username
        or route.password
        or route.query
        or route.fragment
        or (prefix and route.path != prefix and not route.path.startswith(prefix + "/"))
    ):
        raise LiveCheckError(f"sitemap contains a non-canonical or out-of-project URL: {url}")


def _check_core_contract(path, url, body, root_url):
    if path == "":
        content = _VisibleContentParser()
        content.feed(body)
        visible_copy = _normalize_copy(" ".join(content.text))
        if "Less scrolling. More noticing." in visible_copy:
            raise LiveCheckError(f"{url}: internal feedback copy is still visible")
        join_url = urljoin(root_url, "contribute/")
        if not any(urljoin(root_url, anchor["href"]) == join_url for anchor in content.anchors):
            raise LiveCheckError(f"{url}: homepage does not link to the contributor invitation")
    elif path == "contribute/":
        content = _VisibleContentParser()
        content.feed(body)
        visible_copy = _normalize_copy(" ".join(content.text))
        required_copy = (
            "Review a research workflow.",
            "Improve a tool.",
            "Ground the question.",
            "Try the Field Companion with the microphone off.",
        )
        missing_copy = [phrase for phrase in required_copy if phrase not in visible_copy]
        if missing_copy:
            raise LiveCheckError(f"{url}: contributor invitation is missing a direct first step: {missing_copy[0]}")
        if "Less scrolling. More noticing." in visible_copy:
            raise LiveCheckError(f"{url}: internal feedback copy is still visible")
        expected_quick_links = {
            ("#contribute-researchers", "I’m a researcher"),
            ("#contribute-developers", "I’m a developer"),
            ("#contribute-naturalists", "I’m a naturalist or supporter"),
        }
        actual_quick_links = {
            (anchor["href"], anchor["text"])
            for anchor in content.anchors
            if anchor["href"].startswith("#")
        }
        if not expected_quick_links.issubset(actual_quick_links):
            raise LiveCheckError(f"{url}: direct researcher, developer and naturalist paths are incomplete")
        expected_routes = {
            urljoin(root_url, "community/university/"),
            "https://github.com/Metivity/talk2nature/issues",
            urljoin(root_url, "contribute/source/"),
        }
        linked_routes = {urljoin(root_url, anchor["href"]) for anchor in content.anchors}
        if not expected_routes.issubset(linked_routes):
            raise LiveCheckError(f"{url}: researcher, developer and source-suggestion routes are incomplete")
    elif path == "tools/listen/":
        content = _VisibleContentParser()
        content.feed(body)
        visible_copy = _normalize_copy(" ".join(content.text))
        required_copy = (
            "Open a sound or notebook",
            "Tap to open Files on your device",
            "Browse here or drop one file",
            "WAV up to 2 min / 25 MB",
            "MP3/M4A not supported",
        )
        missing_copy = [phrase for phrase in required_copy if phrase not in visible_copy]
        if missing_copy:
            raise LiveCheckError(f"{url}: file-opening guidance is incomplete: {missing_copy[0]}")
        picker = content.controls.get("wav-file")
        if (
            picker is None
            or picker["tag"] != "input"
            or picker["attributes"].get("type") != "file"
            or ".wav" not in picker["attributes"].get("accept", "")
        ):
            raise LiveCheckError(f"{url}: the local WAV file picker is missing")
    elif path == "app/compare/":
        content = _VisibleContentParser()
        content.feed(body)
        visible_copy = _normalize_copy(" ".join(content.text))
        required_copy = (
            "Open a session ZIP",
            "Tap to open Files on your device",
            "Browse here or drop one file",
            "ZIP up to 27 MB",
        )
        missing_copy = [phrase for phrase in required_copy if phrase not in visible_copy]
        if missing_copy:
            raise LiveCheckError(f"{url}: saved-session file guidance is incomplete: {missing_copy[0]}")
        for control_id in ("file-a", "file-b"):
            picker = content.controls.get(control_id)
            if (
                picker is None
                or picker["tag"] != "input"
                or picker["attributes"].get("type") != "file"
                or ".zip" not in picker["attributes"].get("accept", "")
            ):
                raise LiveCheckError(f"{url}: the {control_id} session ZIP picker is missing")
    elif path == "tools/annotation-compare/":
        content = _VisibleContentParser()
        content.feed(body)
        visible_copy = _normalize_copy(" ".join(content.text))
        if "Tap to open Files on your device" not in visible_copy or "Browse here or drop one file" not in visible_copy:
            raise LiveCheckError(f"{url}: annotation file-opening guidance is incomplete")
        if "Open observer A labels" not in visible_copy or "Open observer B labels" not in visible_copy:
            raise LiveCheckError(f"{url}: the two observer-label file actions are missing")
        for control_id in ("annotation-file-a", "annotation-file-b"):
            picker = content.controls.get(control_id)
            if (
                picker is None
                or picker["tag"] != "input"
                or picker["attributes"].get("type") != "file"
                or ".json" not in picker["attributes"].get("accept", "")
            ):
                raise LiveCheckError(f"{url}: the {control_id} JSON picker is missing")
    elif path == "app/":
        content = _VisibleContentParser()
        content.feed(body)
        primary_actions = [anchor for anchor in content.anchors if "primary" in anchor["classes"]]
        expected_href = urljoin(root_url, "app/station/?mode=demo#station-console")
        if not primary_actions or urljoin(root_url, primary_actions[0]["href"]) != expected_href:
            raise LiveCheckError(
                f"{url}: first primary action must open the invented, microphone-free example"
            )
        if primary_actions[0]["text"] != "Try an example · no microphone":
            raise LiveCheckError(f"{url}: the first primary action does not identify the invented example")
        visible_copy = _normalize_copy(" ".join(content.text))
        if "We don't call, imitate or prompt animals." not in visible_copy:
            raise LiveCheckError(f"{url}: the Zero Command statement is missing")
        if "Try without a microphone" in visible_copy or "Start a 30-second moment" in visible_copy:
            raise LiveCheckError(f"{url}: stale first-action copy is still published")
    elif path == "app/station/":
        content = _VisibleContentParser()
        content.feed(body)
        visible_copy = _normalize_copy(" ".join(content.text))
        required_copy = (
            "Listen-only by design.",
            "We do not call, imitate or prompt animals.",
            "You choose when recording starts and can stop it at any time.",
            "In the browser, recording ends if you leave this page.",
        )
        missing_copy = [phrase for phrase in required_copy if phrase not in visible_copy]
        if missing_copy:
            raise LiveCheckError(f"{url}: Zero Command setup disclosure is incomplete: {missing_copy[0]}")
        speech_marker = content.controls.get("station-voice")
        if (
            speech_marker is None
            or speech_marker["tag"] != "button"
            or speech_marker["text"] != "Mark heard speech"
            or speech_marker["attributes"].get("aria-describedby") != "station-voice-guidance"
            or "Only mark nearby human speech when it occurs naturally." not in visible_copy
            or "Do not speak, call or imitate to elicit a response." not in visible_copy
        ):
            raise LiveCheckError(f"{url}: observational speech marker or its guidance is missing")
        permission = content.controls.get("station-permission")
        if (
            permission is None
            or permission["tag"] != "input"
            or permission["attributes"].get("type") != "checkbox"
            or "checked" in permission["attributes"]
        ):
            raise LiveCheckError(f"{url}: microphone permission must be unchecked by default")
        start = content.controls.get("station-start")
        if start is None or start["tag"] != "button" or "disabled" not in start["attributes"]:
            raise LiveCheckError(f"{url}: microphone Start must be disabled by default")
        demo = content.controls.get("station-demo")
        if (
            demo is None
            or demo["tag"] != "button"
            or demo["text"] != "Try invented example · no microphone"
            or "disabled" in demo["attributes"]
        ):
            raise LiveCheckError(f"{url}: the enabled invented, microphone-free action is missing")


def check_once(base_url, fetch=fetch_text, timeout=8):
    base_url = normalize_base_url(base_url)
    root_url = base_url + "/"
    errors = []
    checked_pages = []
    attempted_core_urls = set()
    route_checks_attempted = 0
    robots_checked = False
    for path in HTML_PATHS:
        url = urljoin(root_url, path)
        checked_pages.append(url)
        attempted_core_urls.add(url)
        try:
            body = _verify_live_page(url, fetch, timeout)
            _check_core_contract(path, url, body, root_url)
        except (LiveCheckError, OSError, UnicodeDecodeError) as exc:
            errors.append(str(exc) if isinstance(exc, LiveCheckError) else f"{url}: {exc}")

    sitemap_url = urljoin(root_url, "sitemap.xml")
    sitemap_urls = set()
    try:
        sitemap_body = _read(fetch, sitemap_url, {"application/xml", "text/xml"}, timeout)
        sitemap_root = ElementTree.fromstring(sitemap_body)
        if sitemap_root.tag.rsplit("}", 1)[-1] != "urlset":
            raise LiveCheckError(f"{sitemap_url}: expected a sitemap urlset")
        sitemap_entries = [
            (element.text or "").strip()
            for element in sitemap_root.iter()
            if element.tag.rsplit("}", 1)[-1] == "loc"
        ]
        if not sitemap_entries:
            raise LiveCheckError(f"{sitemap_url}: sitemap contains no page URLs")
        if len(sitemap_entries) != len(set(sitemap_entries)):
            errors.append(f"{sitemap_url}: sitemap contains duplicate page URLs")
        for url in sitemap_entries:
            try:
                _validate_sitemap_route(url, base_url)
            except LiveCheckError as exc:
                errors.append(str(exc))
            else:
                sitemap_urls.add(url)
        missing = sorted(set(checked_pages) - sitemap_urls)
        if missing:
            errors.append(f"{sitemap_url}: missing required routes: {', '.join(missing)}")

        additional_urls = sorted(sitemap_urls - attempted_core_urls)
        route_checks_attempted = len(sitemap_urls.intersection(attempted_core_urls)) + len(additional_urls)
        with ThreadPoolExecutor(max_workers=min(8, len(additional_urls) or 1)) as pool:
            futures = {
                pool.submit(_verify_live_page, url, fetch, timeout): url
                for url in additional_urls
            }
            for future in as_completed(futures):
                try:
                    future.result()
                except (LiveCheckError, OSError, UnicodeDecodeError) as exc:
                    url = futures[future]
                    errors.append(str(exc) if isinstance(exc, LiveCheckError) else f"{url}: {exc}")
    except (LiveCheckError, OSError, UnicodeDecodeError, ElementTree.ParseError) as exc:
        errors.append(str(exc) if isinstance(exc, LiveCheckError) else f"{sitemap_url}: {exc}")

    robots_url = urljoin(root_url, "robots.txt")
    try:
        robots_body = _read(fetch, robots_url, {"text/plain"}, timeout)
        robots_checked = True
        robot_lines = {line.strip() for line in robots_body.splitlines()}
        expected_sitemap_line = f"Sitemap: {sitemap_url}"
        if expected_sitemap_line not in robot_lines:
            errors.append(f"{robots_url}: does not name {sitemap_url}")
        if "Disallow: /" in robot_lines:
            errors.append(f"{robots_url}: blocks all crawlers")
    except (LiveCheckError, OSError, UnicodeDecodeError) as exc:
        errors.append(str(exc) if isinstance(exc, LiveCheckError) else f"{robots_url}: {exc}")

    if errors:
        unique_errors = sorted(set(errors))
        raise LiveCheckError(
            f"live check found {len(unique_errors)} problem(s); sitemap has "
            f"{len(sitemap_urls)} unique in-scope route(s), {route_checks_attempted} route checks were attempted, "
            f"robots fetched: {robots_checked}:\n- " + "\n- ".join(unique_errors)
        )

    return {
        "base_url": base_url,
        "pages_verified": len(sitemap_urls),
        "sitemap_urls": len(sitemap_urls),
        "all_sitemap_pages_verified": True,
        "robots_names_sitemap": True,
        "zero_command_first_action_verified": True,
        "station_disclosure_verified": True,
        "permission_unchecked_by_default": True,
        "microphone_start_disabled_by_default": True,
        "synthetic_action_available": True,
        "internal_feedback_copy_absent": True,
        "contributor_paths_verified": True,
        "file_picker_guidance_verified": True,
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
