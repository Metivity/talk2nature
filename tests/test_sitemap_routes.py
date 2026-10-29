import tempfile
import unittest
from pathlib import Path

from scripts.compare_sitemap_routes import SitemapError, compare_routes, sitemap_urls


BASE = "https://example.org/project"
NS = "http://www.sitemaps.org/schemas/sitemap/0.9"


def sitemap(*urls):
    entries = "".join(f"<url><loc>{url}</loc></url>" for url in urls)
    return f'<urlset xmlns="{NS}">{entries}</urlset>'


class SitemapRouteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def write(self, name, body):
        path = self.root / name
        path.write_text(body)
        return path

    def test_identical_routes_have_no_missing_or_new_urls(self):
        urls = [BASE + "/", BASE + "/research/one/"]
        reference = self.write("reference.xml", sitemap(*urls))
        candidate = self.write("candidate.xml", sitemap(*urls))
        result = compare_routes(reference, candidate, BASE)
        self.assertEqual(result["preserved_urls"], 2)
        self.assertEqual(result["missing_from_candidate"], [])
        self.assertEqual(result["new_in_candidate"], [])

    def test_removed_routes_are_reported_and_new_pages_are_allowed(self):
        reference = self.write("reference.xml", sitemap(BASE + "/", BASE + "/old/"))
        candidate = self.write("candidate.xml", sitemap(BASE + "/", BASE + "/new/"))
        result = compare_routes(reference, candidate, BASE)
        self.assertEqual(result["missing_from_candidate"], [BASE + "/old/"])
        self.assertEqual(result["new_in_candidate"], [BASE + "/new/"])

    def test_duplicate_locations_are_rejected(self):
        path = self.write("duplicate.xml", sitemap(BASE + "/", BASE + "/"))
        with self.assertRaisesRegex(SitemapError, "duplicate"):
            sitemap_urls(path, BASE)

    def test_urls_outside_the_project_path_are_rejected(self):
        path = self.write("outside.xml", sitemap("https://example.org/other/"))
        with self.assertRaisesRegex(SitemapError, "project path"):
            sitemap_urls(path, BASE)

    def test_foreign_origins_and_query_urls_are_rejected(self):
        foreign = self.write("foreign.xml", sitemap("https://other.org/project/"))
        query = self.write("query.xml", sitemap(BASE + "/?source=campaign"))
        with self.assertRaisesRegex(SitemapError, "origin"):
            sitemap_urls(foreign, BASE)
        with self.assertRaisesRegex(SitemapError, "canonical"):
            sitemap_urls(query, BASE)

    def test_sitemap_index_is_not_mistaken_for_a_urlset(self):
        path = self.write("index.xml", f'<sitemapindex xmlns="{NS}"/>')
        with self.assertRaisesRegex(SitemapError, "urlset"):
            sitemap_urls(path, BASE)

    def test_pages_deployment_blocks_route_loss_before_artifact_upload(self):
        workflow = (Path(__file__).parents[1] / ".github/workflows/pages.yml").read_text()
        capture = workflow.index("Preserve currently published routes")
        compare = workflow.index("scripts/compare_sitemap_routes.py")
        upload = workflow.index("Upload only the public site")
        self.assertLess(capture, compare)
        self.assertLess(compare, upload)
        self.assertIn('SITE_URL: ${{ steps.pages.outputs.base_url }}', workflow)


if __name__ == "__main__":
    unittest.main()
