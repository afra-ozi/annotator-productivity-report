import unittest
from datetime import date

from productivity import flags, per_annotator


def task(name, seconds, qa=""):
    return {"annotator": name, "task_id": "t", "date": date(2026, 1, 5), "seconds": seconds, "qa_result": qa}


class TestProductivity(unittest.TestCase):
    def test_tasks_per_hour(self):
        rows = [task("a", 90)] * 40  # 40 tasks in 1 hour
        s = per_annotator(rows)["a"]
        self.assertAlmostEqual(s["hours"], 1.0)
        self.assertAlmostEqual(s["tph"], 40.0)

    def test_quality_ignores_unaudited(self):
        rows = [task("a", 60, "pass"), task("a", 60, "fail"), task("a", 60)]
        s = per_annotator(rows)["a"]
        self.assertEqual(s["audited"], 2)
        self.assertAlmostEqual(s["quality"], 0.5)

    def test_no_audits_gives_none(self):
        self.assertIsNone(per_annotator([task("a", 60)])["a"]["quality"])

    def test_flags_fast_and_low_quality(self):
        rows = ([task("steady", 90, "pass")] * 10 + [task("other", 95, "pass")] * 10
                + [task("rusher", 20, "fail")] * 10)
        f = flags(per_annotator(rows), target_tph=40, min_quality=0.9)
        self.assertIn("rusher", f)
        self.assertNotIn("steady", f)
        self.assertTrue(any("very fast" in r for r in f["rusher"]))
        self.assertTrue(any("QA pass rate" in r for r in f["rusher"]))


if __name__ == "__main__":
    unittest.main()
