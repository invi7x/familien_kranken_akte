# Stinkis’ Krankenakten – Version 0.8.2

Eine kleine, selbst gehostete Familien-Gesundheitschronik.

## Neu in Version 0.8.2

- Technische Docker-Namen für den Release neutralisiert: `familienakte`, `familienakte_data` und `familienakte_backups`.
- Sicherungsdialog vollständig responsiv gemacht; horizontales Scrollen innerhalb des Dialogs entfernt.
- Backup-Dateinamen und Download-Funktion bleiben neutral als `familienakte-backup-...json`.
- Den vorläufigen Pollenflug-Platzhalter aus der rechten Spalte entfernt; das Feature bleibt vorerst auf Eis.

## Parallel testen

```bash
cd /docker/stinkis-krankenakten-v0.8.2
sudo docker compose -f compose-test.yaml up -d --build
```

Aufruf: `http://SERVER-IP:8507`

Test-Volumes: `familienakte_v082_test_data` und `familienakte_v082_test_backups`.

## Automatische Server-Backups

Die Compose-Dateien starten neben der Web-App einen kleinen `backup-scheduler`. Er prüft stündlich, ob das konfigurierte monatliche Backup fällig ist. Standardpfad im Container ist `/backups`. Die Dateien liegen weiterhin persistent im Docker-Volume, sind aber über **Sicherungen → Gespeicherte Server-Backups → Download** direkt erreichbar.
