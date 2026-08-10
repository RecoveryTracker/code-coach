# Setting up Code Coach on Windows 11

About 10 minutes. Uses `winget`, which is built into Windows 11, so there are no
installer wizards to click through and no PATH checkboxes to forget.

> On Windows 10, `winget` may not be present. Install it from the Microsoft Store
> ("App Installer"), or download Python, Node, and Git from their websites — if
> you use the Python installer, **tick "Add python.exe to PATH"** on the first
> screen.

---

## 1. Install Python, Node, and Git

Open the Start menu, type **Terminal**, and open it. Paste these one at a time
and let each finish:

```powershell
winget install -e --id Python.Python.3.12
```

```powershell
winget install -e --id OpenJS.NodeJS.LTS
```

```powershell
winget install -e --id Git.Git
```

If it asks you to accept a source agreement, type `Y` and press Enter.

## 2. Close the Terminal and open a new one

This step matters. The installers change your PATH, and a window that was already
open won't pick that up. Close it completely, then reopen Terminal.

Check all three are visible:

```powershell
python --version
```

```powershell
node --version
```

```powershell
git --version
```

Three version numbers means you're good. If any says *"is not recognized"*, the
window is still the old one — close and reopen it again.

## 3. Download the app

```powershell
cd $HOME\Documents
```

```powershell
git clone https://github.com/RecoveryTracker/code-coach.git
```

```powershell
cd code-coach
```

## 4. Set it up (once)

```powershell
python -m venv .venv
```

```powershell
.\.venv\Scripts\pip install -r requirements.txt
```

```powershell
cd web
```

```powershell
npm install
```

```powershell
cd ..
```

`npm install` takes a couple of minutes and prints a lot of text. That's normal.

## 5. Run it

```powershell
.\start.bat
```

Two small windows open — those are the servers, leave them alone — and your
browser opens the app. If it doesn't, go to **http://localhost:5173**.

From now on that's the only step: open the `code-coach` folder and double-click
**start.bat**.

**To stop:** close the two small server windows.

---

## If something breaks

**`No module named uvicorn`**
You're running the system Python instead of the project's. Re-run the
`.\.venv\Scripts\pip install -r requirements.txt` line from step 4, from inside
the `code-coach` folder.

**`python` / `npm` / `git` is not recognized**
Step 2 — you need a Terminal window opened *after* the installs.

**Browser loads but says it can't reach the API**
Wait ten seconds and refresh. The Python server takes longer to start than the
page does.

**Page won't load at all**
Check both small windows are still open. If one closed itself, run `.\start.bat`
again and read what it says before it disappears.

**`&&` errors**
Windows PowerShell doesn't support `&&` for chaining. Run each command on its
own line, as written above.

---

## Getting updates later

```powershell
cd $HOME\Documents\code-coach
```

```powershell
git pull
```

If the update touched the frontend, re-run `npm install` inside `web`. Your typed
work and progress are stored separately and survive updates.

---

## What it is

Typing practice for LeetCode: 52 solutions across 13 patterns, typed verbatim so
the shapes end up in muscle memory. It checks each line as you go and tells you
exactly which one is off — including indentation, since that's syntax in Python.

There's a **Foundations** track too if you'd rather start with plain Python.

Pick a class from the dropdown at the top left and start typing. The
[README](README.md) covers the rest.
