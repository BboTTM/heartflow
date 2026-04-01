import unittest

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from social_chat_import import parse_csv_text, parse_json_text, parse_txt, render_messages  # noqa: E402


class SocialChatImportTest(unittest.TestCase):
    def test_parse_txt(self):
        parsed = parse_txt("[2026-04-01 10:00:00] Alice: 先给结论\nBob: 我晚上再回你\n")
        self.assertEqual(parsed[0]["sender"], "Alice")
        self.assertEqual(parsed[0]["text"], "先给结论")
        self.assertEqual(parsed[1]["sender"], "Bob")

    def test_parse_json(self):
        parsed = parse_json_text(
            '[{"author":"Alice","message":"先给结论","created_at":"2026-04-01T10:00:00"},{"user":"Bob","content":"我晚上再回你"}]'
        )
        self.assertEqual(parsed[0]["sender"], "Alice")
        self.assertEqual(parsed[0]["text"], "先给结论")
        self.assertEqual(parsed[1]["sender"], "Bob")

    def test_parse_csv(self):
        parsed = parse_csv_text("time,name,text\n2026-04-01 10:00, Alice, 先给结论\n")
        self.assertEqual(parsed[0]["sender"], "Alice")
        self.assertEqual(parsed[0]["text"], "先给结论")

    def test_render_messages(self):
        rendered = render_messages(
            [{"timestamp": "2026-04-01T10:00:00", "sender": "Alice", "text": "先给结论"}],
            platform="telegram",
        )
        self.assertIn("# platform: telegram", rendered)
        self.assertIn("Alice: 先给结论", rendered)


if __name__ == "__main__":
    unittest.main()
