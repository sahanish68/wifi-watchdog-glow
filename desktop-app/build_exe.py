"""PyInstaller build script optimized for Windows 11 size + startup time.

Usage:
    pip install pyinstaller
    python build_exe.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
APP_NAME = "NetSentinel"
ENTRY = ROOT / "netsentinel" / "__main__.py"

EXCLUDES = [
    # GUI frameworks we don't use
    "tkinter", "PyQt5", "PySide6", "PySide2",
    # Test / docs
    "unittest", "pydoc", "doctest", "pdb", "test", "tests",
    # Bloat
    "distutils", "setuptools", "pip", "wheel",
    "email.test", "lib2to3", "xmlrpc",
]


def main():
    dist = ROOT / "dist"
    build = ROOT / "build"
    for p in (dist, build):
        if p.exists(): shutil.rmtree(p)

    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean",
        "--onefile", "--windowed",
        "--name", APP_NAME,
        # smaller exe + faster import resolution
        "--strip",
        "--optimize", "2",
    ]
    for m in EXCLUDES:
        args += ["--exclude-module", m]

    if shutil.which("upx"):
        print(">> UPX detected — will compress")
    else:
        args += ["--noupx"]

    args.append(str(ENTRY))
    print(">>", " ".join(args))
    subprocess.check_call(args, cwd=ROOT)
    out = dist / f"{APP_NAME}.exe"
    print(f"\nBuilt: {out} ({out.stat().st_size // 1024} KB)" if out.exists()
          else "\nBuild finished — see ./dist")


if __name__ == "__main__":
    main()
