import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AnalyzeRelationshipMaterialsTest(unittest.TestCase):
    def test_cli_generates_meta_and_card(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            input_path = tmp / "messages.txt"
            meta_out = tmp / "meta.json"
            card_out = tmp / "card.md"
            input_path.write_text(
                "慢慢来吧，我想再了解你一点。下次有机会可以一起吃饭。\n",
                encoding="utf-8",
            )
            cmd = [
                "python3",
                str(ROOT / "tools" / "analyze_relationship_materials.py"),
                "--input",
                str(input_path),
                "--display-name",
                "Lin",
                "--source-type",
                "real-person",
                "--stage",
                "熟悉",
                "--meta-out",
                str(meta_out),
                "--card-out",
                str(card_out),
            ]
            result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            meta = json.loads(meta_out.read_text(encoding="utf-8"))
            card = card_out.read_text(encoding="utf-8")
            self.assertEqual(meta["display_name"], "Lin")
            self.assertEqual(meta["relationship_stage"], "熟悉")
            self.assertIn("archetype_guess", meta["analysis"])
            self.assertIn("## interaction_style", card)


if __name__ == "__main__":
    unittest.main()
