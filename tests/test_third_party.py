import json
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch
from app.gui.third_party import ThirdPartyCredits, load_components, notices_root, license_path
from app.gui.main import ArmAIApp

ROOT = Path(__file__).resolve().parents[1]

class CreditsDataTests(unittest.TestCase):
    def test_all_entries_have_full_local_texts(self):
        entries = load_components(ROOT)
        self.assertEqual(4, sum(e["kind"] == "model" for e in entries))
        self.assertTrue({"Real-ESRGAN", "GFPGAN", "PyTorch"}.issubset({e["name"] for e in entries}))
        for entry in entries:
            for file in entry["license_files"]:
                self.assertGreater(license_path(ROOT, file).stat().st_size, 0)
        self.assertTrue((ROOT / "THIRD_PARTY_NOTICES.txt").is_file())
        tqdm = next(e for e in entries if e["id"] == "tqdm")
        self.assertEqual("MPL-2.0 AND MIT", tqdm["license"])

    def test_checkpoint_terms_and_source_terms_are_separate(self):
        entries = load_components(ROOT)
        parse = next(e for e in entries if e["id"] == "parsenet")
        self.assertIn("CC-BY-NC-SA-4.0", parse["license"])
        self.assertIn("does not separately state", parse["notes"])
        self.assertEqual(64, len(parse["sha256"]))

    def test_installed_and_internal_resource_paths(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "licenses").mkdir()
            (root / "licenses/components.json").write_text("{}")
            with patch("sys.frozen", True, create=True), patch("sys.executable", str(root/"app.exe")):
                self.assertEqual(root, notices_root())
            with patch("sys.frozen", True, create=True), patch("sys.executable", str(root/"other/app.exe")), patch("sys._MEIPASS", str(root), create=True):
                self.assertEqual(root, notices_root())
        with self.assertRaises(ValueError):
            license_path(ROOT, "../outside.txt")

class CreditsGuiTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def window(self, language="th"):
        window = ThirdPartyCredits(self.root, language, ROOT)
        window.withdraw()
        self.root.update_idletasks()
        return window

    def test_filter_and_selection_buttons(self):
        window = self.window()
        self.assertEqual(63, len(window.tree.get_children()))
        window.query.set("GFPGAN")
        self.assertEqual({"gfpgan", "gfpgan-v14"}, set(window.tree.get_children()))
        window.query.set("not-a-component-xyz")
        self.assertEqual((), window.tree.get_children())
        self.assertTrue(window.view_button.instate(["disabled"]))
        window.query.set("ParseNet")
        self.assertTrue(window.view_button.instate(["!disabled"]))

    def test_view_license_offline_and_open_source_only_on_click(self):
        window = self.window("en")
        window.query.set("PyTorch")
        window.tree.selection_set("torch")
        window._selected()
        with patch("webbrowser.open") as browser:
            window.view_license()
            browser.assert_not_called()
            viewers = [w for w in window.winfo_children() if isinstance(w, tk.Toplevel)]
            self.assertEqual(1, len(viewers))
            viewers[0].withdraw()
            text = next(w for w in viewers[0].winfo_children() if isinstance(w, tk.Text))
            self.assertIn("Redistribution", text.get("1.0","end"))
            self.assertIn("NOTICE", text.get("1.0","end"))
            self.assertEqual("disabled", str(text.cget("state")))
            window.open_source()
            browser.assert_called_once_with("https://github.com/pytorch/pytorch")
        window.view_notices()
        for w in window.winfo_children():
            if isinstance(w, tk.Toplevel):
                w.withdraw()

    def test_help_menu_translations_and_command(self):
        app = ArmAIApp.__new__(ArmAIApp)
        app.root = self.root
        for language, help_label in [("th","ช่วยเหลือ"),("en","Help"),("zh","帮助"),("fr","Aide")]:
            app.language = language
            app._build_help_menu()
            self.assertEqual(help_label, app.menu_bar.entrycget(0,"label"))
            app.help_menu.invoke(1)
            app._third_party_window.withdraw()
            self.assertTrue(app._third_party_window.winfo_exists())
            self.assertNotEqual("",app._third_party_window.title())
            app._third_party_window.destroy()
            app.menu_bar.destroy()

    def test_missing_license_file_shows_error(self):
        window = self.window()
        with patch("tkinter.messagebox.showerror") as show:
            window._show_files("Missing", ["licenses/not-found.txt"])
            show.assert_called_once()

if __name__ == "__main__":
    unittest.main()
