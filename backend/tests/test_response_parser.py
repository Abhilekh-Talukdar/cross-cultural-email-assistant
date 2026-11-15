import unittest

from response_parser import parse_rewrite_response


class ParseRewriteResponseTests(unittest.TestCase):
    def test_parses_all_sections_and_ignores_surrounding_whitespace(self):
        content = """
        ### Rewritten Subject ###
        Project update

        ### Rewritten Body ###
        Hello,
        Here is the update.

        ### Cultural Notes ###
        Uses a concise, professional tone.
        """
        self.assertEqual(
            parse_rewrite_response(content),
            (
                "Project update",
                "Hello,\n        Here is the update.",
                "Uses a concise, professional tone.",
            ),
        )

    def test_allows_preamble_before_first_section(self):
        content = (
            "Here is the rewrite.\n"
            "### Rewritten Subject ###\nSubject\n"
            "### Rewritten Body ###\nBody\n"
            "### Cultural Notes ###\nNotes"
        )
        self.assertEqual(parse_rewrite_response(content), ("Subject", "Body", "Notes"))

    def test_rejects_none_and_non_text_responses(self):
        for content in (None, 42, "", "   "):
            with self.subTest(content=content), self.assertRaises(ValueError):
                parse_rewrite_response(content)

    def test_rejects_each_missing_marker(self):
        valid = (
            "### Rewritten Subject ###\nSubject\n"
            "### Rewritten Body ###\nBody\n"
            "### Cultural Notes ###\nNotes"
        )
        for marker in (
            "### Rewritten Subject ###",
            "### Rewritten Body ###",
            "### Cultural Notes ###",
        ):
            with self.subTest(marker=marker), self.assertRaises(ValueError):
                parse_rewrite_response(valid.replace(marker, ""))

    def test_rejects_markers_in_the_wrong_order(self):
        content = (
            "### Rewritten Body ###\nBody\n"
            "### Rewritten Subject ###\nSubject\n"
            "### Cultural Notes ###\nNotes"
        )
        with self.assertRaises(ValueError):
            parse_rewrite_response(content)

    def test_rejects_empty_sections(self):
        cases = (
            "### Rewritten Subject ###\n\n### Rewritten Body ###\nBody\n### Cultural Notes ###\nNotes",
            "### Rewritten Subject ###\nSubject\n### Rewritten Body ###\n\n### Cultural Notes ###\nNotes",
            "### Rewritten Subject ###\nSubject\n### Rewritten Body ###\nBody\n### Cultural Notes ###\n",
        )
        for content in cases:
            with self.subTest(content=content), self.assertRaises(ValueError):
                parse_rewrite_response(content)


if __name__ == "__main__":
    unittest.main()
