from __future__ import annotations

import time
from datetime import datetime

from app import _backup_due, _load_backup_settings, _write_server_backup, init_db


def main() -> None:
    init_db()
    print("Backup-Scheduler gestartet.", flush=True)
    while True:
        try:
            settings = _load_backup_settings()
            if _backup_due(settings):
                target = _write_server_backup()
                print(f"Automatisches Backup gespeichert: {target}", flush=True)
        except Exception as exc:  # scheduler must survive transient filesystem/db errors
            print(f"Backup-Scheduler Fehler {datetime.now().isoformat(timespec='seconds')}: {exc}", flush=True)
        time.sleep(3600)


if __name__ == "__main__":
    main()
