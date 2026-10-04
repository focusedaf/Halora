"""Offline tests: all network calls are mocked.

Run from backend/:  python -m unittest tests.test_urlhealth -v
"""

import unittest
from unittest.mock import patch

from app.services.urlhealth import cascade
from app.services.urlhealth.archives.base import ArchiveProvider, snapshot_result
from app.services.urlhealth.safety import check_target, normalize_url, url_key


def live(status, **kw):
    return {"status": status, "url": "https://x.test/a", "final_url": "https://x.test/a",
            "http_status": kw.get("http_status"), "redirects": [], "content_type": None,
            "title": None, "reason": kw.get("reason"), "latency_ms": 1}


class Fake(ArchiveProvider):
    def __init__(self, name, outcome, can_save=False):
        super().__init__()
        self.name, self.label, self.outcome, self.supports_save = name, name, outcome, can_save
        self.calls = 0

    def lookup(self, url):
        self.calls += 1
        if self.outcome == "boom":
            raise RuntimeError("provider exploded")
        if self.outcome == "found":
            return snapshot_result(self.name, "found", snapshot_url=f"https://{self.name}/snap",
                                   captured_at="2024-01-01T00:00:00+00:00")
        return snapshot_result(self.name, self.outcome)

    def save(self, url):
        return snapshot_result(self.name, "created", snapshot_url=f"https://{self.name}/new")


def run(live_status, fakes, **opts):
    cascade._cache.clear()
    with patch.object(cascade, "check_live", return_value=live(live_status)), \
         patch.object(cascade, "build_providers", return_value=fakes):
        return cascade.check_url_health("https://x.test/a", refresh=True, **opts)


class Waterfall(unittest.TestCase):
    def test_alive_skips_archives(self):
        p = Fake("a", "found")
        r = run("alive", [p])
        self.assertEqual(r["health"], "alive")
        self.assertEqual(p.calls, 0)

    def test_dead_falls_through_to_first_hit(self):
        a, b, c = Fake("a", "not_found"), Fake("b", "found"), Fake("c", "found")
        r = run("dead", [a, b, c])
        self.assertEqual(r["health"], "archived")
        self.assertEqual(r["recommended"]["provider"], "b")
        self.assertEqual(c.calls, 0)  # waterfall stopped at b

    def test_error_and_exception_do_not_break_cascade(self):
        r = run("dead", [Fake("a", "boom"), Fake("b", "error"), Fake("c", "found")])
        self.assertEqual(r["recommended"]["provider"], "c")

    def test_all_mode_queries_everyone(self):
        fakes = [Fake("a", "found"), Fake("b", "found")]
        r = run("dead", fakes, mode="all")
        self.assertEqual(len(r["archive"]["snapshots"]), 2)

    def test_dead_without_snapshot(self):
        self.assertEqual(run("dead", [Fake("a", "not_found")])["health"], "dead")
        self.assertEqual(run("timeout", [Fake("a", "not_found")])["health"], "unreachable")

    def test_blocked_is_restricted_with_archive_fallback(self):
        r = run("blocked", [Fake("a", "found")])
        self.assertEqual(r["health"], "restricted")
        self.assertEqual(r["archive"]["best"]["provider"], "a")

    def test_preserve_saves_when_live_and_unarchived(self):
        r = run("alive", [Fake("a", "not_found", can_save=True)], preserve=True)
        self.assertTrue(r["archive"]["best"]["newly_created"])

    def test_invalid_url(self):
        self.assertEqual(cascade.check_url_health("ftp://nope")["health"], "invalid")


class Helpers(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_url("example.com/a#frag"), "https://example.com/a")
        self.assertIsNone(normalize_url("javascript:alert(1)"))

    def test_url_key_ignores_scheme_www_slash(self):
        self.assertEqual(url_key("http://www.a.com/x/"), url_key("https://a.com/x"))

    def test_ssrf_guard(self):
        self.assertEqual(check_target("http://127.0.0.1/"), "private")
        self.assertEqual(check_target("http://169.254.169.254/latest/meta-data"), "private")
        self.assertEqual(check_target("http://10.0.0.5/"), "private")

    def test_extract_urls(self):
        text = "See https://a.com/x, and (https://b.org/y). Again https://a.com/x."
        self.assertEqual(cascade.extract_urls(text), ["https://a.com/x", "https://b.org/y"])


if __name__ == "__main__":
    unittest.main()
