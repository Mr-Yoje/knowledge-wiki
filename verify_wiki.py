#!/usr/bin/env python3
"""兼容性 wrapper，委托到 schema/scripts/verify_wiki.py"""
import sys
import subprocess

if __name__ == "__main__":
    script = __file__ + "/../schema/scripts/verify_wiki.py"
    if sys.platform == "win32":
        script = script.replace("/", "\\")
    result = subprocess.run([sys.executable, script] + sys.argv[1:])
    sys.exit(result.returncode)
