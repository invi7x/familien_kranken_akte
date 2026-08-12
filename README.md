# Stinkis’ Krankenakten – Version 0.8.4

Eine kleine, selbst gehostete Familien-Gesundheitschronik.

## Neu in Version 0.8.4

- Import robuster gemacht: Behandlungsfälle mit leerem bzw. `null`-Wert in `updated_at` werden automatisch repariert.
- Bestehende migrierte Datenbanken normalisieren fehlende Vorgangs-Zeitstempel beim Start.
- Neue Vorgänge erhalten `created_at` und `updated_at` nun explizit beim Anlegen.
- JSON-Exporte normalisieren Vorgangs-Zeitstempel, damit keine neuen Sicherungen mit `updated_at: null` entstehen.
- Schema bleibt Version 8; bestehende Sicherungen bleiben kompatibel.

## Parallel testen

```bash
cd /docker/stinkis-krankenakten-v0.8.4
sudo docker compose -f compose-test.yaml up -d --build
```

Aufruf: `http://SERVER-IP:8510`

Test-Volumes: `familienakte_v084_test_data` und `familienakte_v084_test_backups`.

## Automatische Server-Backups

Die Compose-Dateien starten neben der Web-App einen kleinen `backup-scheduler`. Er prüft stündlich, ob das konfigurierte monatliche Backup fällig ist. Standardpfad im Container ist `/backups`. Die Dateien liegen weiterhin persistent im Docker-Volume, sind aber über **Sicherungen → Gespeicherte Server-Backups → Download** direkt erreichbar.
