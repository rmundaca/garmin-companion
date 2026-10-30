"""
Generates a Garmin Connect session token (garmin_tokens_<email>.json) on your computer and
optionally uploads it to the app running on the NAS. The email in the file name lets you keep
tokens for several people in the same folder without overwriting each other.

Usage:
  python generate_token.py
  python generate_token.py --out ./garmin_tokens
  python generate_token.py --upload http://<NAS_IP>:8095
"""
import argparse
import getpass
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Same 0.3.x series as the NAS (package/requirements.txt): the token format is compatible.
SUPPORTED_SERIES = "garminconnect>=0.3.2,<0.4"

try:
    import garminconnect
except ImportError:
    print("ERROR: the 'garminconnect' library is missing. Install it with:")
    print(f'  python -m pip install "{SUPPORTED_SERIES}"')
    sys.exit(1)

BASE_DIR = Path(__file__).resolve().parent


def check_library_version() -> None:
    try:
        from importlib.metadata import version
        installed = version("garminconnect")
    except Exception:
        return
    if installed.split(".")[:2] != ["0", "3"]:
        print(f"WARNING: garminconnect {installed} is installed; the app expects the 0.3.x series.")
        print(f'  python -m pip install "{SUPPORTED_SERIES}"')


def token_filename(email: str) -> str:
    """garmin_tokens_<email>.json, with the email reduced to characters valid on any file system."""
    safe = re.sub(r"[^A-Za-z0-9@._-]", "_", email.strip().lower())
    return f"garmin_tokens_{safe}.json"


def write_private(path: Path, content: str) -> None:
    """Writes the file readable by its owner only (on Linux/macOS); it holds the account refresh token."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)


def generate(out_dir: Path) -> Path:
    email = input("Garmin email: ").strip()
    password = getpass.getpass("Password (hidden): ")
    if not email or not password:
        raise ValueError("Email and password are required.")

    client = garminconnect.Garmin(
        email=email,
        password=password,
        prompt_mfa=lambda: input("2FA verification code: ").strip(),
    )
    client.login()

    out_dir.mkdir(parents=True, exist_ok=True)
    token_file = out_dir / token_filename(email)
    write_private(token_file, client.client.dumps())

    try:
        name = client.get_full_name()
    except Exception:
        name = "user"
    print(f"\nOK: signed in as {name}")
    print(f"Token saved to: {token_file}")
    return token_file


def upload(token_file: Path, base_url: str) -> None:
    url = base_url.rstrip("/") + "/api/auth/token"
    body = json.dumps({"token_json": token_file.read_text(encoding="utf-8")}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8") or "{}")
        print(f"Uploaded to {url}: {data.get('status', 'ok')}")
    except urllib.error.HTTPError as e:
        print(f"ERROR uploading token ({e.code}): {e.read().decode('utf-8', 'replace')}")
    except urllib.error.URLError as e:
        print(f"ERROR: could not connect to {url}: {e.reason}")


def main():
    parser = argparse.ArgumentParser(description="Generates a Garmin Connect session token.")
    parser.add_argument("--out", default=str(BASE_DIR / "garmin_tokens"),
                        help="Folder where garmin_tokens_<email>.json is saved")
    parser.add_argument("--upload", metavar="URL",
                        help="Base URL of the app (e.g. http://<NAS_IP>:8095) to upload the token to")
    args = parser.parse_args()

    check_library_version()
    try:
        token_file = generate(Path(args.out))
    except Exception as e:
        print(f"\nERROR generating token: {e}")
        sys.exit(1)

    base_url = args.upload
    if base_url is None:
        base_url = input("\nApp URL to upload the token to (Enter to skip, e.g. http://<NAS_IP>:8095): ").strip()
    if base_url:
        upload(token_file, base_url)

    print("\nIMPORTANT: this file contains your account credentials. Do not share it or commit it to git.")
    print("Use it in one place only and upload it soon: Garmin rotates the token when it is used and")
    print("invalidates other copies, so an old file or one already used elsewhere will be rejected.")


if __name__ == "__main__":
    main()
