# Stinkis’ Krankenakten – Version 0.8.1

Eine kleine, selbst gehostete Familien-Gesundheitschronik.

## Neu in Version 0.8.1

- **Sicherungen und Backup-Einstellungen zusammengeführt**: nur noch ein Menüpunkt „Sicherungen“.
- Automatische monatliche Sicherungen, Sofort-Backup, manueller JSON-Export und Import befinden sich jetzt an einer Stelle.
- Vorhandene automatische Server-Backups werden im Dialog aufgelistet und können direkt über **Download** heruntergeladen werden.
- Es werden maximal **10 automatische Sicherungen** vorgehalten; ein kleinerer Wert kann eingestellt werden.
- Alte Sicherungen werden beim Erstellen bzw. nach Änderung der Aufbewahrungszahl automatisch bereinigt.
- Neue Backup-Dateien heißen neutral `familienakte-backup-...json`; vorhandene ältere `stinkis-backup-...json` bleiben sichtbar und downloadbar.
- Der manuelle Export heißt `familienakte-export.json`.
- Rechte Allergie- und Medikamentenbereiche: jeder Eintrag innerhalb einer Person wird jetzt als dezente **Sub-Card** dargestellt.
- Notizen sind bei Allergien und Medikamenten einheitlich durch einen feinen Trenner von den übrigen Metadaten abgesetzt.

## Parallel testen

```bash
cd /docker/stinkis-krankenakten-v0.8.1
sudo docker compose -f compose-test.yaml up -d --build
```

Aufruf: `http://SERVER-IP:8506`

Test-Volumes: `stinkis_v081_test_data` und `stinkis_v081_test_backups`.

## Automatische Server-Backups

Die Compose-Dateien starten neben der Web-App einen kleinen `backup-scheduler`. Er prüft stündlich, ob das konfigurierte monatliche Backup fällig ist. Standardpfad im Container ist `/backups`. Die Dateien liegen weiterhin persistent im Docker-Volume, sind aber über **Sicherungen → Gespeicherte Server-Backups → Download** direkt erreichbar.
