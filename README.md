# Stinkis’ Krankenakten – Version 0.8.0

Eine kleine, selbst gehostete Familien-Gesundheitschronik.

## Neu in Version 0.8.0

- Neuer Bereich **⚙️ Einstellungen**.
- **Automatische monatliche JSON-Backups** serverseitig aktivierbar.
- Backup-Tag im Monat (1–28), Zielpfad und Anzahl aufzubewahrender Sicherungen konfigurierbar.
- **„Jetzt auf Server sichern“** für ein sofortiges Backup.
- Letzter erfolgreicher Backup-Zeitpunkt wird angezeigt.
- Separater Docker-Backup-Scheduler: Backups laufen auch dann, wenn die Webseite nicht geöffnet ist.
- Standardmäßig werden Backups in einem eigenen persistenten Docker-Volume unter `/backups` abgelegt.
- Rechte Medikamenten-/Allergieboxen typografisch nochmals aufgeräumt: klarere Hierarchie und mehr Luft bei Grund, Zeitraum und Notiz.
- Die bereits vorhandenen Kategorie-Icons bleiben in den Kategorie-Dropdowns erhalten.

## Parallel testen

```bash
cd /docker/stinkis-krankenakten-v0.8.0
sudo docker compose -f compose-test.yaml up -d --build
```

Aufruf: `http://SERVER-IP:8505`

Das Test-Volume heißt `stinkis_v080_test_data`.

## Automatische Server-Backups

Die Compose-Dateien starten neben der Web-App einen kleinen `backup-scheduler`. Er prüft stündlich, ob das konfigurierte monatliche Backup fällig ist.

Standardpfad: `/backups`

Dieser Pfad ist im mitgelieferten Compose als eigenes persistentes Docker-Volume eingebunden. Wer Backups direkt in einen Ordner des Hosts/NAS schreiben möchte, kann das Volume später durch einen Bind-Mount ersetzen, beispielsweise:

```yaml
volumes:
  - /docker/stinkis-backups:/backups
```

Die automatische Sicherung verwendet dasselbe vollständige JSON-Format wie der manuelle Export, inklusive Profilbildern und Schema-Version.
