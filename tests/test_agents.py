"""Offline unit tests for the deterministic workflow stages."""
import unittest

from research_crew.agents import plan_research, review_report, write_report


class PlannerTests(unittest.TestCase):
    def test_creates_multiple_focused_queries(self):
        queries = plan_research("How does MCP connect AI applications to tools?")
        self.assertEqual(len(queries), 3)
        self.assertIn("MCP", queries[0])

    def test_rejects_empty_question(self):
        with self.assertRaises(ValueError):
            plan_research("   ")

    def test_respects_query_limit(self):
        self.assertEqual(len(plan_research("Explain MCP with examples", max_queries=1)), 1)


class ReportTests(unittest.TestCase):
    def test_report_contains_source_url_and_conclusion(self):
        results = [{"title": "MCP overview", "body": "A protocol overview.", "url": "https://example.com/mcp"}]
        report = write_report("What is MCP?", results)
        self.assertIn("https://example.com/mcp", report)
        self.assertIn("## Conclusion", report)

    def test_empty_results_are_reported_honestly(self):
        report = write_report("What is MCP?", [])
        self.assertIn("No search results were returned", report)

    def test_reviewer_flags_missing_sources(self):
        review = review_report("# Report\n\n## Conclusion\nDone.", [{"title": "x"}])
        self.assertFalse(review.passed)
        self.assertTrue(any("source links" in note.lower() for note in review.notes))

    def test_reviewer_passes_basic_structure_but_warns_about_small_sample(self):
        report = "# Report\n\nSource: https://example.com\n\n## Conclusion\nDone."
        review = review_report(report, [{"title": "x", "url": "https://example.com"}])
        self.assertTrue(review.passed)
        self.assertTrue(any("Fewer than three" in note for note in review.notes))


if __name__ == "__main__":
    unittest.main()
