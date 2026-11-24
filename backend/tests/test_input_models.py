import unittest

from pydantic import ValidationError

from input_models import EmailInput


class EmailInputValidationTests(unittest.TestCase):
    def test_accepts_values_at_documented_limits(self):
        value = EmailInput(
            subject="s" * 500,
            body="b" * 20_000,
            target_culture="c" * 50,
            tone_emphasis="t" * 200,
        )

        self.assertEqual(len(value.subject), 500)
        self.assertEqual(len(value.body), 20_000)
        self.assertEqual(len(value.target_culture), 50)
        self.assertEqual(len(value.tone_emphasis), 200)

    def test_rejects_each_field_above_its_limit(self):
        cases = (
            {"subject": "s" * 501},
            {"body": "b" * 20_001},
            {"target_culture": "c" * 51},
            {"tone_emphasis": "t" * 201},
        )

        for override in cases:
            payload = {
                "subject": "Subject",
                "body": "Body",
                "target_culture": "Japan",
                "tone_emphasis": "Formal",
            }
            payload.update(override)

            with self.subTest(field=next(iter(override))):
                with self.assertRaises(ValidationError):
                    EmailInput(**payload)

    def test_rejects_empty_required_fields_and_empty_optional_tone(self):
        for field in ("subject", "body", "target_culture", "tone_emphasis"):
            payload = {
                "subject": "Subject",
                "body": "Body",
                "target_culture": "Japan",
            }
            payload[field] = ""

            with self.subTest(field=field):
                with self.assertRaises(ValidationError):
                    EmailInput(**payload)

    def test_tone_emphasis_remains_optional(self):
        value = EmailInput(
            subject="Subject",
            body="Body",
            target_culture="Japan",
        )

        self.assertIsNone(value.tone_emphasis)


if __name__ == "__main__":
    unittest.main()
