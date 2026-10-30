<p align="center">
  <img src="package/app/static/icon-192.png" width="96" height="96" alt="Garmin Companion icon">
</p>

<h1 align="center">Garmin Companion</h1>

<p align="center">
  Adaptive running plans that sync to your <b>Garmin</b> watch,<br>
  served from a small self-hosted app on your <b>Asustor NAS</b> or any always-on computer.
</p>

---

## Features

| | |
| :--- | :--- |
| **VDOT paces** | A recent race result (5K, 10K, half or marathon) sets your level and five training paces (Jack Daniels' VDOT). |
| **Periodized plans** | 4 to 30 weeks with base, build, peak, taper and race phases, deload weeks and optional tune-up races. |
| **On your watch** | Sessions in the next 10 days are sent to Garmin Connect as structured workouts with pace alerts. |
| **Tracking** | Completed runs are read back from Garmin and compared with what was planned. |
| **Adaptive** | Every 2 weeks the app reviews your runs and proposes raising or lowering the load. You decide. |
| **Multi-user** | Each person signs in with their own Garmin account. Backup and restore from Settings. |

Works on phone and desktop (installable as a web app), in English and Spanish (detected from the browser),
with light and dark themes. How plans are built is explained in detail in [docs/ALGORITHM.md](docs/ALGORITHM.md).

> [!NOTE]
> Garmin Companion uses [garminconnect](https://github.com/cyberjunky/python-garminconnect), an
> **unofficial** Garmin Connect client. Garmin may change its login or API at any time and break the app.

## Requirements

- A **Garmin Connect** account and a watch that supports structured workouts.
- One of:
  - **Asustor NAS** with ADM 3.x and **Entware** (from App Central). Runs on an AS-202TE (Intel Atom, 32-bit
    i686, 1 GB RAM).
  - **Any computer** with Python 3.11 or newer that stays on (Windows, macOS, Linux).
- To generate the Garmin token: a Windows, macOS or Linux computer with Python 3.10 or newer.

## Installation on an Asustor NAS

1. In ADM, open **App Central**, search for **Entware** and install it. It provides Python 3.11; the Python
   that ships with ADM (3.7) is too old.
2. Build the package (see [Packaging](#packaging)) or download `garmin-companion_<version>_any.apk` from the
   [Releases](https://github.com/rmundaca/garmin-companion/releases) page.
3. In ADM, go to **App Central → Management → Manual Install** and upload the `.apk`.
4. Wait a few minutes. The install script uses Entware to install Python 3.11, pip and SQLite, creates a
   virtual environment and installs the dependencies. On a slow NAS this can take 5–10 minutes.
5. Open the app from its ADM desktop icon or at `http://<NAS_IP>:8095`.
6. Connect your Garmin account (see [Generating the Garmin token](#generating-the-garmin-token)).

Upgrades keep your data. Uninstalling backs up the database to `/volume1/home/garmin-companion-backup/`.

### Logs and service control (SSH)

```bash
APP=/usr/local/AppCentral/garmin-companion

cat $APP/data/install.log           # install and dependency log
tail -f $APP/data/app.log           # application log

$APP/CONTROL/start-stop.sh status   # or: start | stop | restart
```

After the NAS reboots, the app waits (up to 3 minutes) for Entware to be mounted before it starts.

### Manual setup over SSH

If the automatic install fails (check `install.log`), you can set up the environment by hand:

```bash
# 1. Python 3.11 from Entware (--force-space works around a false "0 KB free" report on /opt)
opkg install --force-space python3 python3-pip python3-openssl python3-sqlite3
/opt/bin/pip3 install --no-cache-dir virtualenv

# 2. Virtual environment and dependencies
cd /usr/local/AppCentral/garmin-companion
rm -rf venv
/opt/bin/virtualenv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install --no-cache-dir -r requirements.txt

# 3. Optional: run in the foreground to see errors, then stop with Ctrl+C
./venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8095

# 4. Start the service
CONTROL/start-stop.sh restart
```

## Running manually on Windows

1. Install **Python 3.11 or newer** from [python.org](https://www.python.org/downloads/windows/). Tick
   **Add python.exe to PATH** in the installer.
2. Download the source: **Code → Download ZIP** on GitHub and extract it, or
   `git clone https://github.com/rmundaca/garmin-companion.git`.
3. Open **PowerShell** in the project folder and create a virtual environment with the dependencies:

   ```powershell
   py -0                                   # lists the installed Python versions
   py -3.13 -m venv .venv                  # use a version from the list
   .\.venv\Scripts\python -m pip install -r package\requirements.txt
   ```

   Name the version explicitly. `py -3` may pick a free-threaded build (shown as `3.13t`), which does not
   work with the dependencies.

4. Start the app from the `package` folder:

   ```powershell
   cd package
   ..\.venv\Scripts\python -m app.main
   ```

5. Open `http://localhost:8095`. Keep the PowerShell window open while you use the app; close it or press
   **Ctrl+C** to stop it.
6. Connect your Garmin account (see [Generating the Garmin token](#generating-the-garmin-token)).

Notes:

- Data (database, session secret and Garmin tokens) is stored in `package\data\`. To keep it elsewhere, set
  `GC_DATA_DIR` before starting: `$env:GC_DATA_DIR = "D:\GarminCompanion"`.
- To open the app from your phone at `http://<COMPUTER_IP>:8095`, allow Python through Windows Defender
  Firewall on **private networks** when Windows asks.
- The computer must be on for workouts to sync and for runs to be read back from Garmin.
- If you move or rename the project folder, recreate the virtual environment
  (`py -3.13 -m venv --clear .venv` and reinstall the requirements).
- On macOS or Linux, use `python3 -m venv .venv` and `../.venv/bin/python -m app.main`.

## Generating the Garmin token

The app needs a Garmin Connect session for your account. There are two ways to connect:

- **Sign in with email and password** in the app (**Connect Garmin**). The password is not stored; it is
  only used once to obtain a session. This may work, but Garmin often blocks or rate-limits sign-ins from
  servers, and the NAS cannot always complete Garmin's login checks.
- **Upload a token generated on your computer.** This is the **recommended** way, especially on a NAS. You
  sign in once on your own computer, and the app receives a session token instead of your password.

The token is a JSON file (`garmin_tokens_<your email>.json`) with OAuth tokens for your account. It does not
contain your password, but **anyone who has it can access your Garmin account**. Treat it like a password.

### Step 1: Install Python on your computer

Install Python 3.10 or newer from [python.org](https://www.python.org/downloads/). On Windows, tick
**Add python.exe to PATH** in the installer. To check, open a new Command Prompt and run `python --version`.

### Step 2: Run the generator

You only need `generate_token.py` and, on Windows, `generate_token.bat` from the project root (download the
ZIP or clone the repository).

**Windows:** double-click `generate_token.bat`, or run it from a Command Prompt in the project folder:

```bat
generate_token.bat
```

The first time, it installs the `garminconnect` library (`garminconnect>=0.3.2,<0.4`) for your user.

**macOS or Linux:**

```bash
python3 -m pip install --user "garminconnect>=0.3.2,<0.4"
python3 generate_token.py
```

### Step 3: Sign in

The generator asks, in order:

1. **Garmin email** — the one you use for Garmin Connect.
2. **Password** — nothing appears on screen while you type; this is normal.
3. **2FA verification code** — only if two-step verification is on. Garmin sends it by email or SMS. Enter
   it quickly; it expires in a few minutes.

If it succeeds, you will see:

```
OK: signed in as <Your Name>
Token saved to: C:\...\garmin-companion\garmin_tokens\garmin_tokens_you@example.com.json
```

The email in the file name lets you generate tokens for several people in the same folder.

### Step 4: Upload the token to the app

The generator then asks for the **app URL**. Press **Enter** to skip it if you will use option A.

- **Option A — from the browser (recommended):** open the app, tap **Connect Garmin**, choose the
  `garmin_tokens_<email>.json` file (or paste its contents) and confirm. This connects Garmin and signs you
  in on that browser in one step.
- **Option B — from the generator:** enter `http://<NAS_IP>:8095` (or `http://localhost:8095` on Windows),
  or pass it from the start: `generate_token.bat --upload http://<NAS_IP>:8095`. This reconnects Garmin for
  an existing profile, but it does not sign in any browser. Use it when your browser is already signed in and
  the app reports that Garmin is disconnected.

When the app shows **Garmin connected**, **delete the token file** from your computer.

> [!IMPORTANT]
> **Use each token once, and upload it soon.** Garmin rotates the token every time it is used and
> invalidates older copies. A token that is old, was already uploaded, or was used on another computer will
> be rejected. If that happens, simply generate a new one.

### Where the token is kept

The app saves your session in its data folder (`data/tokens/<profile id>/`; `package\data\tokens\` on
Windows). On the NAS, only the user that runs the app can read it. The app refreshes the token automatically,
so you do not need to repeat this unless Garmin ends the session (for example after you change your Garmin
password). Signing out only removes the browser cookie; deleting your profile in the app also removes its
tokens.

### Troubleshooting

| Problem | Fix |
| :--- | :--- |
| `'python' is not recognized` | Python is not on the PATH. Reinstall it with **Add python.exe to PATH**, then open a new window. |
| `could not install garminconnect` | Check your internet connection, or run `python -m pip install --user "garminconnect>=0.3.2,<0.4"` to see the error. |
| `ERROR generating token: ... 401` or `Invalid credentials` | Wrong email or password. Check them on [connect.garmin.com](https://connect.garmin.com). |
| `... 429` or `Too Many Requests` | Garmin is rate-limiting you. Wait 30–60 minutes before trying again. |
| The 2FA code is rejected | It expired or was mistyped. Run the generator again to get a new code. |
| The app says the token is invalid | It was already used or is too old. Generate a new one and upload it right away. |
| `could not connect to http://...` | Check the NAS IP and port 8095, and that your computer is on the same network. |
| Garmin disconnects later | Generate and upload a new token. Check `app.log` for the reason. |

## Getting started

1. **Connect Garmin** (see above). The first profile created on a server is its **administrator**: it can
   download and restore the data of every profile.
2. **Create a plan.** Enter a recent race result (or let the app read your Garmin personal records), the goal
   race and date, and the days you can run.
3. **Train.** The next sessions appear on your watch's calendar. Runs are read back from Garmin
   automatically, and every 2 weeks the app asks how you feel and proposes adjustments.

## Security

There is **no password on the app itself**. Each browser is signed in to the profile of the Garmin account it
connected with, using a signed cookie.

> [!WARNING]
> Keep the app on your local network. **Do not expose or forward port 8095 to the internet.** Traffic is
> plain HTTP, so use it only on networks you trust.

- `data/` holds the database, the cookie signing key (`secret.key`) and the Garmin tokens. It is never
  committed to git or included in the `.apk`.
- Never commit or share `garmin_tokens_*.json` files. `.gitignore` excludes them.
- Database backups downloaded from Settings contain the data of every profile; store them privately.

Report vulnerabilities by opening an issue (without including tokens or personal data).

## Development

```powershell
cd package
..\.venv\Scripts\python -m pip install -r tests\requirements.txt          # test dependencies
..\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8095       # run with auto-reload
..\.venv\Scripts\python -m pytest -q                                       # run the tests
```

Python 3.11 matches the NAS. The NAS (32-bit i686, 1 GB RAM) sets these rules:

- **Dependencies:** FastAPI `<0.100` and Pydantic v1 (`pydantic-core` has no i686 wheels).
  `garminconnect==0.3.2` (0.3.3 and later require Python 3.12). Pure-Python packages or ones with an i686
  wheel only.
- **Front end:** one `index.html`, `app.css`, and vanilla `app.js` and `help.js`. No Node, bundlers or CDNs.
  All text is in the `I18N` table (English and Spanish).
- **Scripts:** `CONTROL/*.sh` run under BusyBox `/bin/sh` with LF line endings.

```
CONTROL/              ADM package metadata and install/start scripts
package/
├── app/
│   ├── api/          HTTP routes
│   ├── core/         Configuration, database, session cookies
│   ├── engine/       VDOT, periodization, workouts, statistics
│   ├── services/     Garmin client, plan sync, periodic reviews
│   ├── models/       Database tables
│   ├── schedulers/   Background jobs
│   └── static/       Front end
└── tests/            Test suite
docs/ALGORITHM.md     How plans are built
generate_token.py     Garmin token generator (generate_token.bat on Windows)
build_package.py      Builds the .apk
```

## Packaging

```powershell
python build_package.py -m "What changed"   # bump the patch version and build
python build_package.py --bump minor        # or: --bump major, --version X.Y.Z, --no-bump
```

Output goes to `dist/garmin-companion_<version>_any.apk` (`build.bat` does the same on Windows). The `.apk`
never includes `package/data/` or the tests.

## License and credits

Released under the [MIT License](LICENSE).

- [python-garminconnect](https://github.com/cyberjunky/python-garminconnect) (MIT) connects to Garmin Connect.
- Training paces follow the VDOT formulas by Jack Daniels and Jimmy Gilbert (*Oxygen Power*, 1979).

Not affiliated with Garmin or Asustor. Garmin and Garmin Connect are trademarks of Garmin Ltd.
