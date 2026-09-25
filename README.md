# SysWatch

A lightweight Linux server health and log monitoring tool, built from scratch in Python. SysWatch watches CPU, memory, and disk usage, scans system logs for warnings and errors, stores historical data in SQLite, raises threshold-based alerts, and displays everything on a live web dashboard. It runs continuously as a systemd service.

The idea was simple: automate the kind of checks a junior sysadmin does manually every day, and understand every layer of how Linux exposes that information.

## Why this project

Most monitoring tools (Nagios, Prometheus agents, Datadog) follow the same basic shape: collect data, store it, decide if something is wrong, and show it to a human. SysWatch is a small, self-contained version of that shape, built to understand each stage rather than just calling a library and trusting it.

Almost everything here reads directly from the Linux `/proc` filesystem rather than relying entirely on a library, so the project doubles as a working demonstration of how Linux internals actually expose CPU, memory, and process information.

## Architecture

```
collector.py  --> storage.py  --> alerts.py
     |                                |
     |                                v
     +-------------------------> dashboard.py (Flask)
     
main.py ties collector, storage, and alerts together in a loop
systemd/syswatch.service runs main.py as a background service
```

Each module has one job:

- **collector.py** - reads system metrics. Only observes, never decides anything.
- **parser.py** - scans log files for warnings, errors, and critical messages.
- **storage.py** - writes and reads metrics from a SQLite database.
- **alerts.py** - checks metrics against thresholds and reports problems.
- **dashboard.py** - a Flask web app that displays live metrics, alerts, and top processes.
- **main.py** - the orchestrator. Runs the full cycle (collect, store, check) every few seconds.
- **systemd/syswatch.service** - lets the whole thing run continuously in the background, independent of any open terminal.

Keeping these separate meant that swapping SQLite for another database, or adding a new alert channel, would only touch one file. It also made each piece independently testable while building it.

## What each module actually does

### collector.py

Reads CPU usage directly from `/proc/stat`. The file holds cumulative tick counts since boot (user, nice, system, idle, iowait, irq, softirq, steal, guest, guest_nice), not a live percentage, so CPU usage is calculated by taking two readings a second apart and computing the delta:

```
usage% = (total_delta - idle_delta) / total_delta * 100
```

Memory is read from `/proc/meminfo`, using `MemAvailable` rather than `MemFree`. `MemFree` is misleading on Linux because the kernel deliberately uses free RAM for disk caching, so a healthy machine can show very little `MemFree` while still having plenty of usable memory. `MemAvailable` is the kernel's own estimate of memory that can actually be reclaimed for a new process.

Disk usage comes from Python's `shutil.disk_usage()`.

Process listing uses `psutil`, since correctly reading `/proc/[pid]/` for every process by hand means handling permission errors for processes owned by other users, and psutil already does this safely. Per-process CPU percentage needs the same delta approach as system-wide CPU: `psutil` returns 0.0 on the first call for any process, since it has no earlier reading to compare against, so every process is primed once, then read again after a short pause.

### parser.py

Reads a log file, filters lines by keyword (ERROR, WARNING, CRITICAL, FAIL), and only looks at the most recent N lines rather than the whole file's history, since a real monitoring pass only cares about what changed recently. Matching lines are deduplicated by message text, with a count of how many times each one occurred and a set of which process/PID combinations produced it, instead of flooding the output with the same repeated warning hundreds of times.

### storage.py

A small SQLite wrapper: `init_db()` creates the metrics table if it does not exist, `save_metrics()` inserts one row per reading (timestamp, cpu, mem, disk), and `get_metrics()` reads back the most recent rows. Each function opens and closes its own connection rather than keeping one open for the program's lifetime. SQLite connections are cheap to open, and doing it this way avoids stale or locked connections if something crashes mid-write.

### alerts.py

`check_threshold()` takes the current cpu, mem, and disk values and returns a list of alert messages for anything over threshold. It returns data rather than printing directly, so the same function can be used by a console script and by the web dashboard without duplicating logic. `show_alerts()` is a thin wrapper that prints the result to the console, useful for quick manual testing and for systemd's logs.

### dashboard.py

A Flask app with a single route that pulls live data from collector.py, storage.py, and alerts.py, and renders it through a Jinja2 template. Shows current CPU/mem/disk, a table of top CPU-consuming processes, and an alert panel that switches between an "all clear" state and a list of active alerts.

### main.py

The loop that makes this an actual running tool rather than a set of scripts. Every cycle: collect metrics, save them to SQLite, check and print alerts, sleep, repeat.

### systemd/syswatch.service

Runs `main.py` as a managed background service: restarts automatically on failure, starts on boot if enabled, and logs through `journalctl`. Uses the project's virtual environment's Python interpreter directly rather than the system Python, so it has access to the installed dependencies (Flask, psutil). Runs with unbuffered Python output (`-u` flag), since Python buffers output differently when it is not attached to a live terminal, which otherwise delays logs from reaching `journalctl` in real time.

## Running it

```bash
git clone <repo-url>
cd syswatch
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd src
python3 main.py          # run the monitoring loop directly
python3 dashboard.py     # run the web dashboard on localhost:5000
```

To run as a background service:

```bash
sudo cp systemd/syswatch.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start syswatch
sudo systemctl enable syswatch   # start on boot
sudo journalctl -u syswatch -f   # watch live logs
```

## Design decisions and tradeoffs

- **MemAvailable over MemFree**: covered above, avoids false low-memory alerts caused by normal disk caching behavior.
- **psutil for process listing, manual parsing for system-wide CPU/mem**: manual `/proc` parsing was done first to understand the mechanism, then psutil was used where reinventing it added no further understanding, particularly around handling permission-restricted processes.
- **Recency window in the log parser**: only scanning the last N lines keeps each scan fast and mirrors how a real monitoring pass works, checking what is new rather than reprocessing an entire log file's history every time.
- **Deduplication over raw output**: a single misconfigured service can log the same warning hundreds of times. Counting occurrences and tracking source PIDs gives a usable signal instead of a wall of repeated text.
- **Data returned, not printed, from core logic**: `check_threshold()` and the collector functions all return values rather than printing them, so the same logic serves the console output, the database writer, and the web dashboard without being duplicated three times.
- **Open and close a new SQLite connection per function call**: simpler and safer for this project's scale than holding one long-lived connection, and avoids issues if the process restarts mid-write.

## Known limitations and possible next steps

- Per-process CPU percentage is relative to a single core, not normalized against total logical CPU count.
- The log parser currently does plain substring matching, not full log-line parsing (timestamp, hostname, and process are extracted separately, but the matching itself is keyword-based, not structured).
- Alerts are currently console-only and dashboard-only; no email or webhook integration yet.
- No automated tests yet.
- The dashboard is read-only; no historical charting of the SQLite data over time yet, though `get_metrics()` already supports pulling recent history for this.

## Tech stack

Python 3, Flask, psutil, SQLite3, systemd, Linux `/proc` filesystem.
