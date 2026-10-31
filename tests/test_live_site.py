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
            "": self._page("", "Talk2Nature"),
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
                '<button id="station-demo">Try invented example · no microphone</button>',
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
        self.assertEqual(result["pages_verified"], 4)
        self.assertEqual(result["sitemap_urls"], 4)
        self.assertTrue(result["robots_names_sitemap"])
        self.assertTrue(result["zero_command_first_action_verified"])
        self.assertTrue(result["station_disclosure_verified"])
        self.assertTrue(result["permission_unchecked_by_default"])
        self.assertTrue(result["microphone_start_disabled_by_default"])
        self.assertTrue(result["synthetic_action_available"])
        self.assertEqual(len(site.calls), 6)

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
        self.assertEqual(result["pages_verified"], 4)
        self.assertEqual(sleeps, [3])

    def test_rejects_stale_or_blocked_live_metadata(self):
        site = FakeLiveSite()
        site.pages["app/"] = site.pages["app/"].replace(
            'content="index,follow"', 'content="noindex,nofollow"'
        )
        with self.assertRaisesRegex(LiveCheckError, "not explicitly indexable"):
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
