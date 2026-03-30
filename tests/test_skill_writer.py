import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RelationshipSkillWriterTest(unittest.TestCase):
    def run_cmd(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["python3", str(ROOT / "tools" / "skill_writer.py"), *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

    def test_create_import_update_and_rollback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            base_dir = tmp / "relationships"
            meta_file = tmp / "meta.json"
            card_file = tmp / "card.md"
            material_file = tmp / "notes.txt"
            correction_file = tmp / "correction.json"

            meta_file.write_text(
                json.dumps(
                    {
                        "display_name": "Lin",
                        "source_type": "real-person",
                        "relationship_stage": "熟悉",
                        "core_persona": "慢热型对象",
                        "default_mode": "immersive",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            card_file.write_text(
                "## 核心人格\n\n慢热型对象。\n\n## 当前阶段\n\n熟悉\n",
                encoding="utf-8",
            )
            material_file.write_text(
                "慢慢来吧，我想再了解你一点。下次有机会可以一起吃饭。\n",
                encoding="utf-8",
            )
            correction_file.write_text(
                json.dumps(
                    {
                        "dimension": "interaction_style",
                        "wrong": "很快进入暧昧",
                        "correct": "会先观察一段时间，再逐步升温",
                        "reason": "对象明显更慢热",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            create = self.run_cmd("--action", "create", "--slug", "lin", "--meta-file", str(meta_file), "--card-file", str(card_file), "--base-dir", str(base_dir))
            self.assertEqual(create.returncode, 0, msg=create.stderr)

            imported = self.run_cmd("--action", "import-material", "--slug", "lin", "--material-file", str(material_file), "--material-kind", "notes", "--base-dir", str(base_dir))
            self.assertEqual(imported.returncode, 0, msg=imported.stderr)

            updated = self.run_cmd("--action", "update", "--slug", "lin", "--update-kind", "correction", "--correction-file", str(correction_file), "--base-dir", str(base_dir))
            self.assertEqual(updated.returncode, 0, msg=updated.stderr)

            meta = json.loads((base_dir / "lin" / "meta.json").read_text(encoding="utf-8"))
            card = (base_dir / "lin" / "relationship-card.md").read_text(encoding="utf-8")
            self.assertEqual(meta["slug"], "lin")
            self.assertEqual(meta["relationship_stage"], "熟悉")
            self.assertIn("source_updates", card)
            self.assertIn("corrections", card)

            rolled = self.run_cmd("--action", "rollback", "--slug", "lin", "--version", "v1", "--base-dir", str(base_dir))
            self.assertEqual(rolled.returncode, 0, msg=rolled.stderr)
            rolled_meta = json.loads((base_dir / "lin" / "meta.json").read_text(encoding="utf-8"))
            self.assertEqual(rolled_meta["version"], "v1")


if __name__ == "__main__":
    unittest.main()
