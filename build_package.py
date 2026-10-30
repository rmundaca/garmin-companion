#!/usr/bin/env python3
"""
build_package.py - Builds the Asustor ADM package (.apk) with an automatic or manual version bump.

Usage:
    python build_package.py                        # Bump patch (e.g. 1.0.0 -> 1.0.1)
    python build_package.py --bump minor           # Bump minor (e.g. 1.0.0 -> 1.1.0)
    python build_package.py --bump major           # Bump major (e.g. 1.0.0 -> 2.0.0)
    python build_package.py --version 1.2.0        # Set an exact version
    python build_package.py --no-bump              # Keep the current version
    python build_package.py -m "Change note"       # Note for CONTROL/changelog.txt
"""

import os
import io
import re
import sys
import json
import tarfile
import zipfile
import argparse
from datetime import date
from pathlib import Path

# UTF-8 stdout for Windows consoles
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent
CONTROL_DIR = ROOT_DIR / "CONTROL"
PACKAGE_DIR = ROOT_DIR / "package"
DIST_DIR = ROOT_DIR / "dist"
CONFIG_JSON = CONTROL_DIR / "config.json"
CHANGELOG_TXT = CONTROL_DIR / "changelog.txt"
APP_INIT_PY = PACKAGE_DIR / "app" / "__init__.py"

def parse_semver(ver_str: str):
    """Parses an X.Y.Z version."""
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)(.*)$", ver_str.strip())
    if not m:
        raise ValueError(f"Invalid semver version: '{ver_str}' (expected X.Y.Z)")
    return int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)

def bump_version_string(ver_str: str, bump_type: str) -> str:
    """Next version for the given bump type."""
    major, minor, patch, extra = parse_semver(ver_str)
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    return ver_str

def get_current_version() -> str:
    """Current version from CONTROL/config.json."""
    if not CONFIG_JSON.exists():
        raise FileNotFoundError(f"{CONFIG_JSON} not found")
    with open(CONFIG_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("general", {}).get("version") or data.get("version", "1.0.0")

def update_version_in_files(new_version: str, changelog_msg: str = None):
    """Writes the version to the package metadata, changelog and app source."""
    print(f"\n[1/4] Setting version {new_version} in project files...")

    # 1. CONTROL/config.json
    with open(CONFIG_JSON, "r", encoding="utf-8") as f:
        config_data = json.load(f)
    if "general" in config_data:
        config_data["general"]["version"] = new_version
    config_data["version"] = new_version
    with open(CONFIG_JSON, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"  [OK] {CONFIG_JSON.relative_to(ROOT_DIR)}")

    # 2. CONTROL/changelog.txt
    today_str = date.today().isoformat()
    note = changelog_msg or "Garmin Companion update for Asustor ADM."
    new_entry = f"{new_version} ({today_str})\n- {note}\n\n"
    existing_changelog = ""
    if CHANGELOG_TXT.exists():
        with open(CHANGELOG_TXT, "r", encoding="utf-8") as f:
            existing_changelog = f.read().strip()
    
    # Only add it if the changelog does not already start with this version
    if not existing_changelog.startswith(new_version):
        with open(CHANGELOG_TXT, "w", encoding="utf-8") as f:
            f.write(new_entry + existing_changelog + "\n")
        print(f"  [OK] {CHANGELOG_TXT.relative_to(ROOT_DIR)}")

    # 3. package/app/__init__.py
    if APP_INIT_PY.exists():
        with open(APP_INIT_PY, "r", encoding="utf-8") as f:
            content = f.read()
        new_content = re.sub(r'__version__\s*=\s*["\'][^"\']+["\']', f'__version__ = "{new_version}"', content)
        with open(APP_INIT_PY, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"  [OK] {APP_INIT_PY.relative_to(ROOT_DIR)}")

def build_apkg(version: str):
    """Builds the APKG (.apk) files in the Asustor ADM format."""
    if not CONTROL_DIR.exists():
        raise FileNotFoundError(f"{CONTROL_DIR} not found")
    if not PACKAGE_DIR.exists():
        raise FileNotFoundError(f"{PACKAGE_DIR} not found")

    # 1. control.tar.gz
    print("\n[2/4] Building control.tar.gz in memory...")
    control_buffer = io.BytesIO()
    with tarfile.open(fileobj=control_buffer, mode="w:gz") as tar:
        for file_path in sorted(CONTROL_DIR.glob("*")):
            if file_path.is_file():
                rel_name = file_path.name
                data = file_path.read_bytes()
                ti = tarfile.TarInfo(name=rel_name)
                ti.size = len(data)
                ti.mtime = int(file_path.stat().st_mtime)
                ti.uid = 0
                ti.gid = 0
                ti.uname = "root"
                ti.gname = "root"
                # Shell scripts are executable
                if file_path.suffix == ".sh":
                    ti.mode = 0o755
                else:
                    ti.mode = 0o644
                tar.addfile(ti, io.BytesIO(data))
                print(f"   + {rel_name} ({oct(ti.mode)})")

    control_bytes = control_buffer.getvalue()
    print(f"  [OK] control.tar.gz built: {len(control_bytes) / 1024:.1f} KB")

    # 2. data.tar.gz
    print("\n[3/4] Building data.tar.gz in memory...")
    data_buffer = io.BytesIO()

    def should_exclude(rel_path: str) -> bool:
        norm = rel_path.replace("\\", "/")
        if "__pycache__" in norm or norm.endswith(".pyc") or norm.endswith(".pyo") or ".git" in norm:
            return True
        # The whole data/ folder stays out: on the NAS it links to the persistent data (it once shipped app-restore-*.db)
        if norm == "data" or norm.startswith("data/") or norm.endswith(".log") or norm.endswith(".bak"):
            return True
        if norm.startswith("tests/") or norm == "tests" or ".pytest_cache" in norm:
            return True
        if norm.endswith(".apk") or norm.endswith(".tmp"):
            return True
        return False

    with tarfile.open(fileobj=data_buffer, mode="w:gz") as tar:
        for root, dirs, files in os.walk(PACKAGE_DIR):
            dirs.sort()
            files.sort()
            for d in dirs:
                full_dir = Path(root) / d
                rel_dir = full_dir.relative_to(PACKAGE_DIR).as_posix()
                if should_exclude(rel_dir):
                    continue
                ti = tarfile.TarInfo(name=rel_dir)
                ti.type = tarfile.DIRTYPE
                ti.mode = 0o755
                ti.uid = 0
                ti.gid = 0
                ti.uname = "root"
                ti.gname = "root"
                ti.mtime = int(full_dir.stat().st_mtime)
                tar.addfile(ti)

            for f in files:
                full_file = Path(root) / f
                rel_file = full_file.relative_to(PACKAGE_DIR).as_posix()
                if should_exclude(rel_file):
                    continue
                data = full_file.read_bytes()
                ti = tarfile.TarInfo(name=rel_file)
                ti.size = len(data)
                ti.mode = 0o644
                ti.uid = 0
                ti.gid = 0
                ti.uname = "root"
                ti.gname = "root"
                ti.mtime = int(full_file.stat().st_mtime)
                tar.addfile(ti, io.BytesIO(data))

    data_bytes = data_buffer.getvalue()
    print(f"  [OK] data.tar.gz built: {len(data_bytes) / 1024:.1f} KB")

    # 3. APK files
    print("\n[4/4] Creating the APKG (.apk) container...")
    apkg_version_bytes = b"2.0\n"

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    output_generic = DIST_DIR / "garmin-companion.apk"
    output_versioned = DIST_DIR / f"garmin-companion_{version}_any.apk"

    for target_file in [output_generic, output_versioned]:
        with zipfile.ZipFile(target_file, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("apkg-version", apkg_version_bytes)
            zf.writestr("control.tar.gz", control_bytes)
            zf.writestr("data.tar.gz", data_bytes)
        
        size_kb = target_file.stat().st_size / 1024.0
        print(f"  [OK] Created: dist/{target_file.name} ({size_kb:.1f} KB)")

    # 4. Contents check
    print("\n" + "=" * 65)
    print(f" Asustor APKG v{version} built successfully")
    print("=" * 65)
    with zipfile.ZipFile(output_generic, "r") as zf:
        for info in zf.infolist():
            print(f"  * {info.filename:<18} ({info.file_size:,} bytes uncompressed)")
    print("=" * 65)
    print("\nTo install it on your Asustor NAS:")
    print("  1. Open the ADM web interface (http://<NAS_IP>:8000)")
    print("  2. Go to 'App Central' -> 'Management' -> 'Manual Install'")
    print(f"  3. Select 'dist/{output_versioned.name}' or 'dist/{output_generic.name}' and upload it")
    print("  4. The post-install script sets up the service on port 8095.")
    print("=" * 65 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Builds the Asustor APKG package and bumps the version.")
    parser.add_argument(
        "--bump",
        choices=["patch", "minor", "major"],
        default="patch",
        help="Semver bump type (default: patch)"
    )
    parser.add_argument(
        "--version",
        type=str,
        default=None,
        help="Exact version (e.g. 1.1.0)"
    )
    parser.add_argument(
        "--no-bump",
        action="store_true",
        help="Build with the current version"
    )
    parser.add_argument(
        "-m", "--message",
        type=str,
        default=None,
        help="Note for CONTROL/changelog.txt"
    )

    args = parser.parse_args()

    cur_version = get_current_version()
    print("=" * 65)
    print(f"  Garmin Companion - Asustor Package Builder")
    print(f"  Current project version: v{cur_version}")
    print("=" * 65)

    if args.no_bump:
        new_version = cur_version
        print(f"Mode: no version bump (v{new_version})")
    elif args.version:
        new_version = args.version
        print(f"Mode: manual version -> v{new_version}")
    else:
        new_version = bump_version_string(cur_version, args.bump)
        print(f"Mode: [{args.bump}] bump -> v{cur_version} ==> v{new_version}")

    update_version_in_files(new_version, args.message)
    build_apkg(new_version)

if __name__ == "__main__":
    main()
