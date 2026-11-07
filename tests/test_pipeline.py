import unittest
import tempfile
import shutil
from pathlib import Path
from aistudio.cli import init_project
from aistudio.inventory import scan_inventory
from aistudio.manifest import GapManifestBuilder, validate_manifest
from aistudio.assembler import assemble_assets

class TestAIStudioPipeline(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_init_and_scan(self):
        project_dir = init_project("test_proj", base_dir=self.test_dir)
        self.assertTrue((project_dir / "00_立项与策划").exists())
        self.assertTrue((project_dir / "01_raw_assets/user_assets").exists())
        self.assertTrue((project_dir / "02_generated/voices").exists())
        self.assertTrue((project_dir / "03_assets_hub").exists())

        # Create dummy user file
        dummy_file = project_dir / "01_raw_assets/user_assets/sample.txt"
        dummy_file.write_text("Hello AIStudio")

        inv = scan_inventory(project_dir)
        self.assertEqual(inv["total_files"], 1)

    def test_manifest_builder_and_validate(self):
        builder = GapManifestBuilder("test_proj", "Test Project")
        builder.add_tts_task("tts_01", "测试文案", "02_generated/voices/shot_01.wav")
        builder.add_image_task("img_01", "futuristic city", "02_generated/images/shot_01.png")
        manifest_file = self.test_dir / "gap_manifest.json"
        builder.save(manifest_file)

        self.assertTrue(validate_manifest(manifest_file))

    def test_assembler(self):
        project_dir = init_project("test_proj_2", base_dir=self.test_dir)
        gen_img = project_dir / "02_generated/images/shot_01.png"
        gen_img.write_text("dummy image data")

        status = assemble_assets(project_dir)
        self.assertTrue(status["is_ready"])
        self.assertEqual(status["assembled_count"], 1)
        self.assertTrue((project_dir / "03_assets_hub/assets_ready.lock").exists())

if __name__ == "__main__":
    unittest.main()
