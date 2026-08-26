# Running IntegrationTest.py on Windows

`IntegrationTest.py` only needs Python, `requests`, `urllib3`, and `python-dotenv` — it
does not need the NLP stack (spaCy/scispacy) or WeasyPrint that the notebooks in this repo
use, so you don't need the full `requirements.txt` unless you're also running those.

## 1. Install Python

- Install Python 3.12 from https://www.python.org/downloads/windows/
  (or `winget install Python.Python.3.12`).
- During install, tick **"Add python.exe to PATH"**.
- Verify in PowerShell:
  ```powershell
  py -3.12 --version
  ```

## 2. Get the repo

```powershell
git clone <repo-url> Testing
cd Testing
```
(If you already have the repo as a folder copy, just `cd` into it instead.)

## 3. Create and activate a virtual environment

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script with an execution-policy error, run once
(per user, not admin-required):
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 4. Install dependencies

Minimal set actually used by `IntegrationTest.py`:
```powershell
pip install requests urllib3 python-dotenv
```

Or, to match the rest of the repo's environment exactly (needed only if you'll also run
the notebooks):
```powershell
pip install -r requirements.txt
```

## 5. Create `.env`

`IntegrationTest.py` reads `V2_TOOLS` and `V2_SERVER` via `python-dotenv`. Create a
`.env` file in the repo root (same folder as `IntegrationTest.py`) — it's gitignored, so
it won't be committed:

```
V2_TOOLS=https://192.168.1.x:xxxx
V2_SERVER=https://192.168.1.x:xxxx
```

These must point to your NW-GMSA transformation-tools server and interface engine (RIE)
— get the actual host/port from whoever manages that lab environment. The other
variables in the repo's `.env` convention (`FHIR_SERVER`, `OAUTH2_TOKEN`, `CLIENT_ID`,
`CLIENT_SECRET`) aren't read by this script and can be omitted if you only need
`IntegrationTest.py`.

Both servers must be reachable from the Windows machine (same network/VPN as the lab
`192.168.1.x` stack).

## 6. Run it

From the repo root, with the venv active:

```powershell
python IntegrationTest.py
```

Useful flags:
```powershell
# Only run O21 order test cases
python IntegrationTest.py --type O21

# Only run R01 report test cases
python IntegrationTest.py --type R01

# Run the transform stages but skip actually posting to V2_SERVER (the RIE)
python IntegrationTest.py --skip-send
```

Exit code is `0` if every case passed, `1` otherwise — useful for CI/scheduled task
integration.

## Notes specific to Windows

- The script writes output files under `Output\FHIR\<type>\` and `Output\V2\<type>\`
  (relative to wherever you run it from) — run it from the repo root so paths line up
  with `Input\V2\<type>\`.
- v2 round-trip files it writes are opened with `newline=""` in the script, so CR
  terminators are preserved as-is rather than being translated to CRLF by Python's text
  layer — no extra Windows config needed there.
- If your lab's `V2_TOOLS`/`V2_SERVER` use a self-signed cert, that's already handled:
  the script disables the `InsecureRequestWarning` and calls requests with
  `verify=False`.
