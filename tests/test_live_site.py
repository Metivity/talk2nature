import unittest
import subprocess
import sys
import urllib.error
from pathlib import Path

from scripts.check_live_site import LiveCheckError, verify_live_site


class FakeLiveSite:
    def __init__(self, base_url="https://example.github.io/talk2nature"):
        self.base_url = base_url.rstrip("/")
        self.calls = []
        self.pages = {
            "": self._page(
                "",
                "Talk2Nature",
                '<a href="/talk2nature/contribute/">Find a way to help</a>',
            ),
            "contribute/": self._page(
                "contribute/",
                "Join Talk2Nature",
                '<a href="#contribute-researchers">I’m a researcher</a>'
                '<a href="#contribute-developers">I’m a developer</a>'
                '<a href="#contribute-naturalists">I’m a naturalist or supporter</a>'
                '<h2>Review a research workflow.</h2><a href="/talk2nature/community/university/">Researcher path</a>'
                '<h2>Improve a tool.</h2><a href="https://github.com/Metivity/talk2nature/issues">Developer path</a>'
                '<h2>Ground the question.</h2><a href="/talk2nature/contribute/source/">Suggest a source</a>'
                "Try the Field Companion with the microphone off.",
            ),
            "app/": self._page(
                "app/",
                "Field Companion",
                '<a class="glass-button primary" href="/talk2nature/app/station/?mode=demo#station-console">'
                "Try an example · no microphone</a> We don't call, imitate or prompt animals.",
            ),
            "app/station/": self._page(
                "app/station/",
                "Nature Station",
                "<strong>Listen-only by design.</strong> We do not call, imitate or prompt animals. "
                "You choose when recording starts and can stop it at any time. "
                "In the browser, recording ends if you leave this page. "
                '<input id="station-permission" type="checkbox">'
                '<button id="station-start" disabled>Permission needed</button>'
                '<button id="station-demo">Try invented example · no microphone</button>'
                '<button id="station-voice" aria-describedby="station-voice-guidance">Mark heard speech</button>'
                '<p id="station-voice-guidance">Only mark nearby human speech when it occurs naturally. '
                'Do not speak, call or imitate to elicit a response.</p>',
            ),
            "app/compare/": self._page(
                "app/compare/",
                "Review saved moments",
                '<span>Open a session ZIP</span><span>Tap to open Files on your device</span>'
                '<span>Browse here or drop one file</span><span>ZIP up to 27 MB</span>'
                '<input id="file-a" type="file" accept=".zip,application/zip">'
                '<input id="file-b" type="file" accept=".zip,application/zip">',
            ),
            "tools/listen/": self._page(
                "tools/listen/",
                "Listen",
                '<span>Open a sound or notebook</span><span>Tap to open Files on your device</span>'
                '<span>Browse here or drop one file</span><span>WAV up to 2 min / 25 MB</span>'
                '<span>MP3/M4A not supported</span>'
                '<input id="wav-file" type="file" accept=".wav,.t2n,audio/wav">',
            ),
            "tools/annotation-compare/": self._page(
                "tools/annotation-compare/",
                "Compare annotations",
                '<span>Open observer A labels</span><span>Open observer B labels</span>'
                '<span>Tap to open Files on your device</span><span>Browse here or drop one file</span>'
                '<input id="annotation-file-a" type="file" accept=".json,application/json">'
                '<input id="annotation-file-b" type="file" accept=".json,application/json">',
            ),
            "research/resources/": self._page("research/resources/", "Research resources"),
        }
        self.sitemap = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + "".join(f"<url><loc>{self.base_url}/{path}</loc></url>" for path in self.pages)
            + "</urlset>"
        )
        self.robots = f"User-agent: *\nAllow: /\nSitemap: {self.base_url}/sitemap.xml\n"

    def _page(self, path, title, body="Page"):
        url = f"{self.base_url}/{path}"
        return (
            '<!doctype html><html lang="en"><head>'
            f"<title>{title}</title><meta name=\"description\" content=\"{title} description\">"
            '<meta name="robots" content="index,follow">'
            f'<link rel="canonical" href="{url}">'
            f"</head><body><h1>Page</h1>{body}</body></html>"
        )

    def fetch(self, url, timeout):
        self.calls.append((url, timeout))
        path = url.removeprefix(self.base_url + "/")
        if path in self.pages:
            return 200, "text/html", self.pages[path], url
        if path == "sitemap.xml":
            return 200, "application/xml", self.sitemap, url
        if path == "robots.txt":
            return 200, "text/plain", self.robots, url
        return 404, "text/plain", "not found", url


class LiveSiteTests(unittest.TestCase):
    def test_verifier_runs_as_a_standalone_script(self):
        script = Path(__file__).parents[1] / "scripts/check_live_site.py"
        result = subprocess.run(
            [sys.executable, str(script), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("HTTPS GitHub Pages deployment URL", result.stdout)

    def test_checks_core_pages_sitemap_and_robots(self):
        site = FakeLiveSite()
        result = verify_live_site(site.base_url + "/", attempts=1, fetch=site.fetch)
        self.assertEqual(result["pages_verified"], 8)
        self.assertEqual(result["sitemap_urls"], 8)
        self.assertTrue(result["all_sitemap_pages_verified"])
        self.assertTrue(result["robots_names_sitemap"])
        self.assertTrue(result["zero_command_first_action_verified"])
        self.assertTrue(result["station_disclosure_verified"])
        self.assertTrue(result["permission_unchecked_by_default"])
        self.assertTrue(result["microphone_start_disabled_by_default"])
        self.assertTrue(result["synthetic_action_available"])
        self.assertTrue(result["internal_feedback_copy_absent"])
        self.assertTrue(result["contributor_paths_verified"])
        self.assertTrue(result["file_picker_guidance_verified"])
        self.assertEqual(len(site.calls), 10)

    def test_checks_every_sitemap_page_for_reachability_and_index_metadata(self):
        site = FakeLiveSite()
        route = "research/dcase2018-bird-presence-benchmark/"
        site.pages[route] = site._page(route, "DCASE research note")
        site.sitemap = site.sitemap.replace(
            "</urlset>",
            f"<url><loc>{site.base_url}/{route}</loc></url></urlset>",
        )

        result = verify_live_site(site.base_url, attempts=1, fetch=site.fetch)

        self.assertEqual(result["pages_verified"], 9)
        self.assertEqual(result["sitemap_urls"], 9)
        self.assertIn((f"{site.base_url}/{route}", 5), site.calls)

    def test_reports_core_copy_failure_and_still_checks_all_sitemap_routes_and_robots(self):
        site = FakeLiveSite()
        site.pages["app/station/"] = site.pages["app/station/"].replace(
            "Listen-only by design.", "Passive observation."
        )
        missing_route = "research/missing-note/"
        site.sitemap = site.sitemap.replace(
            "</urlset>",
            f"<url><loc>{site.base_url}/{missing_route}</loc></url></urlset>",
        )

        with self.assertRaises(LiveCheckError) as raised:
            verify_live_site(site.base_url, attempts=1, fetch=site.fetch)

        message = str(raised.exception)
        self.assertIn("9 unique in-scope route(s), 9 route checks were attempted, robots fetched: True", message)
        self.assertIn("Zero Command setup disclosure is incomplete", message)
        self.assertIn("https://example.github.io/talk2nature/research/missing-note/: expected HTTP 200, received 404", message)
        self.assertIn((f"{site.base_url}/{missing_route}", 5), site.calls)
        self.assertIn((f"{site.base_url}/robots.txt", 5), site.calls)

    def test_rejects_a_sitemap_route_that_returns_404(self):
        site = FakeLiveSite()
        route = "research/missing-note/"
        site.sitemap = site.sitemap.replace(
            "</urlset>",
            f"<url><loc>{site.base_url}/{route}</loc></url></urlset>",
        )

        with self.assertRaisesRegex(LiveCheckError, "research/missing-note.*expected HTTP 200, received 404"):
            verify_live_site(site.base_url, attempts=1, fetch=site.fetch)

    def test_rejects_an_out_of_project_sitemap_url_before_fetching_it(self):
        site = FakeLiveSite()
        site.sitemap = site.sitemap.replace(
            "</urlset>",
            "<url><loc>https://example.org/outside/</loc></url></urlset>",
        )

        with self.assertRaisesRegex(LiveCheckError, "out-of-project URL"):
            verify_live_site(site.base_url, attempts=1, fetch=site.fetch)
        self.assertFalse(any("example.org" in url for url, _ in site.calls))

    def test_rejects_a_stale_or_microphone_first_app_home(self):
        site = FakeLiveSite()
        site.pages["app/"] = site.pages["app/"].replace(
            'href="/talk2nature/app/station/?mode=demo#station-console"',
            'href="/talk2nature/app/station/?mode=companion#station-console"',
        ).replace("Try an example · no microphone", "Start a 30-second moment")
        with self.assertRaisesRegex(LiveCheckError, "first primary action"):
            verify_live_site(site.base_url, attempts=1, fetch=site.fetch)

    def test_rejects_incomplete_station_zero_command_disclosure(self):
        site = FakeLiveSite()
        site.pages["app/station/"] = site.pages["app/station/"].replace(
            "You choose when recording starts and can stop it at any time.",
            "Recording starts when you open the app.",
        )
        with self.assertRaisesRegex(LiveCheckError, "setup disclosure is incomplete"):
            verify_live_site(site.base_url, attempts=1, fetch=site.fetch)

    def test_rejects_a_checked_permission_or_enabled_microphone_start(self):
        site = FakeLiveSite()
        station = site.pages["app/station/"].replace(
            '<input id="station-permission" type="checkbox">',
            '<input id="station-permission" type="checkbox" checked>',
        )
        site.pages["app/station/"] = station
        with self.assertRaisesRegex(LiveCheckError, "permission must be unchecked"):
            verify_live_site(site.base_url, attempts=1, fetch=site.fetch)

        site = FakeLiveSite()
        site.pages["app/station/"] = site.pages["app/station/"].replace(
            '<button id="station-start" disabled>', '<button id="station-start">'
        )
        with self.assertRaisesRegex(LiveCheckError, "Start must be disabled"):
            verify_live_site(site.base_url, attempts=1, fetch=site.fetch)

    def test_rejects_a_missing_or_unavailable_synthetic_station_action(self):
        site = FakeLiveSite()
        site.pages["app/station/"] = site.pages["app/station/"].replace(
            "Try invented example · no microphone", "Try without a microphone"
        )
        with self.assertRaisesRegex(LiveCheckError, "invented, microphone-free action"):
            verify_live_site(site.base_url, attempts=1, fetch=site.fetch)

    def test_rejects_a_stale_speech_marker_that_could_prompt_the_animal(self):
        site = FakeLiveSite()
        site.pages["app/station/"] = site.pages["app/station/"].replace(
            "Mark heard speech", "Mark my voice"
        )
        with self.assertRaisesRegex(LiveCheckError, "observational speech marker"):
            verify_live_site(site.base_url, attempts=1, fetch=site.fetch)

    def test_retries_transient_deployment_failure(self):
        site = FakeLiveSite()
        calls = 0

        def flaky_fetch(url, timeout):
            nonlocal calls
            calls += 1
            if calls == 1:
                raise urllib.error.URLError("deployment still propagating")
            return site.fetch(url, timeout)

        sleeps = []
        result = verify_live_site(
            site.base_url, attempts=2, interval=3, fetch=flaky_fetch, sleep=sleeps.append
        )
        self.assertEqual(result["pages_verified"], 8)
        self.assertEqual(sleeps, [3])

    def test_rejects_stale_or_blocked_live_metadata(self):
        site = FakeLiveSite()
        site.pages["app/"] = site.pages["app/"].replace(
            'content="index,follow"', 'content="noindex,nofollow"'
        )
        with self.assertRaisesRegex(LiveCheckError, "not explicitly indexable"):
            verify_live_site(site.base_url, attempts=1, fetch=site.fetch)

    def test_rejects_internal_feedback_copy_on_the_live_homepage(self):
        site = FakeLiveSite()
        site.pages[""] = site.pages[""].replace(
            "<h1>Page</h1>", "<h1>Page</h1>Less scrolling. More noticing."
        )
        with self.assertRaisesRegex(LiveCheckError, "internal feedback copy is still visible"):
            verify_live_site(site.base_url, attempts=1, fetch=site.fetch)

    def test_rejects_missing_contribution_quick_links(self):
        site = FakeLiveSite()
        site.pages["contribute/"] = site.pages["contribute/"].replace(
            '<a href="#contribute-developers">I’m a developer</a>', ""
        )
        with self.assertRaisesRegex(LiveCheckError, "direct researcher, developer and naturalist paths"):
            verify_live_site(site.base_url, attempts=1, fetch=site.fetch)

    def test_rejects_old_file_picker_instructions_on_live_listen_page(self):
        site = FakeLiveSite()
        site.pages["tools/listen/"] = site.pages["tools/listen/"].replace(
            "Browse here or drop one file", "Choose File"
        )
        with self.assertRaisesRegex(LiveCheckError, "file-opening guidance is incomplete"):
            verify_live_site(site.base_url, attempts=1, fetch=site.fetch)

    def test_requires_https_before_network_access(self):
        site = FakeLiveSite()
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            verify_live_site("http://example.github.io/talk2nature", fetch=site.fetch)
        self.assertEqual(site.calls, [])

    def test_pages_workflow_verifies_the_deployed_site_after_deploy(self):
        workflow = (Path(__file__).parents[1] / ".github/workflows/pages.yml").read_text()
        deploy_step = workflow.index("id: deployment")
        live_check_step = workflow.index("name: Verify live routes and crawl metadata")
        self.assertGreater(live_check_step, deploy_step)
        self.assertIn("DEPLOYMENT_URL: ${{ steps.deployment.outputs.page_url }}", workflow)
        self.assertIn('python3 scripts/check_live_site.py --base-url "$DEPLOYMENT_URL"', workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("timeout-minutes: 5", workflow)


if __name__ == "__main__":
    unittest.main()
