import json
import subprocess
import sys
from pathlib import Path


plugins = json.loads(Path(__file__).with_name("plugins.json").read_text())
if not isinstance(plugins, list):
    raise ValueError("plugins.json must contain a list")

for plugin in plugins:
    if not isinstance(plugin, dict) or not isinstance(plugin.get("package"), str) or not isinstance(plugin.get("app"), str):
        raise ValueError("Each plugin needs a package and an app string")
    url = plugin.get("url")
    if url is not None and (not isinstance(url, str) or not url.startswith("git+https://")):
        raise ValueError("Plugin URLs must start with git+https://")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "--no-cache-dir", url or plugin["package"]],
        check=True,
    )