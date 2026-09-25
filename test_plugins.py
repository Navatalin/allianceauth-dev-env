import json
import runpy
import unittest
from unittest.mock import patch


class PluginInstallTests(unittest.TestCase):
    def test_pypi_and_git_sources(self):
        plugins = [
            {"package": "example==1.2.3", "app": "example"},
            {"package": "other", "app": "other", "url": "git+https://example.com/other.git@v1"},
        ]
        with patch("pathlib.Path.read_text", return_value=json.dumps(plugins)), patch("subprocess.run") as install:
            runpy.run_path("install_plugins.py")

        self.assertEqual(install.call_count, 2)
        self.assertEqual(install.call_args_list[0].args[0][-1], "example==1.2.3")
        self.assertEqual(install.call_args_list[1].args[0][-1], plugins[1]["url"])
        self.assertTrue(all("--upgrade" in call.args[0] for call in install.call_args_list))
        self.assertTrue(all(call.kwargs["check"] for call in install.call_args_list))

    def test_invalid_source_is_rejected(self):
        plugins = [{"package": "example", "app": "example", "url": "file:///tmp/plugin"}]
        with patch("pathlib.Path.read_text", return_value=json.dumps(plugins)), patch("subprocess.run") as install:
            with self.assertRaises(ValueError):
                runpy.run_path("install_plugins.py")
        install.assert_not_called()


if __name__ == "__main__":
    unittest.main()