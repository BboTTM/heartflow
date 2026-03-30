import unittest

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from feishu_chat_import import normalize_message, parse_message_content, render_messages  # noqa: E402


class FeishuChatImportTest(unittest.TestCase):
    def test_parse_text_message(self):
        content = '{"text":"先给结论，不要讲背景"}'
        self.assertEqual(parse_message_content("text", content), "先给结论，不要讲背景")

    def test_normalize_message(self):
        raw = {
            "message_id": "om_xxx",
            "chat_id": "oc_xxx",
            "create_time": "1711886400000",
            "sender": {"id": "ou_123", "id_type": "open_id"},
            "body": {"message_type": "text", "content": '{"text":"谁负责？"}'},
        }
        normalized = normalize_message(raw)
        self.assertEqual(normalized["sender_id"], "ou_123")
        self.assertEqual(normalized["text"], "谁负责？")
        self.assertEqual(normalized["message_type"], "text")

    def test_render_messages(self):
        rendered = render_messages(
            [
                {
                    "timestamp": "2026-03-31T10:00:00",
                    "sender_id": "ou_123",
                    "text": "先给结论",
                    "message_type": "text",
                }
            ]
        )
        self.assertIn("ou_123", rendered)
        self.assertIn("先给结论", rendered)


if __name__ == "__main__":
    unittest.main()
