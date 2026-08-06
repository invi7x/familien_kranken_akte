# Stinkis’ Krankenakten – Version 0.2.1

Eine kleine, selbst gehostete Familien-Gesundheitschronik.

## Neu in Version 0.2.1

- Fehler bei gruppierten Allergien und Medikamenten (`group.items`) dauerhaft korrigiert
- Profilbilder beziehungsweise Initialen direkt neben den Personennamen in den Seitenboxen
- Geschlechtssymbol auch in den gruppierten Seitenboxen
- optisch einheitliche blaue Plus-Aktion für „Hinzufügen“
- Versionsstand auf 0.2.1 aktualisiert

## Update von Version 0.1

Vorher in der laufenden v0.1 oben rechts einen JSON-Export erstellen.

Dann im Projektordner:

```bash
docker compose down
docker compose up -d --build
```

Die bestehende SQLite-Datenbank im Volume wird beim Start automatisch um die neuen Spalten ergänzt. Alternativ kann die v0.1-JSON-Sicherung über **Sicherung → Sicherung importieren** eingespielt werden.

## Installation

```bash
cd /docker/stinkis-familienakte
docker compose up -d --build
```

Danach:

```text
http://SERVER-IP:8484
```

## Lokales Git-Repository anlegen

```bash
cd /docker/stinkis-familienakte
git init
git add .
git commit -m "Stinkis Krankenakten v0.2.1"
git tag v0.2.1
```

Falls Git nach Name und E-Mail fragt:

```bash
git config user.name "Dennis König"
git config user.email "deine-adresse@example.de"
```

## Backup

Die Daten liegen im Docker-Volume `stinkis_krankenakten_data`. Zusätzlich kann über **Sicherung** ein JSON-Export erzeugt und wieder importiert werden.

## Sicherheit

Die App besitzt noch keine Anmeldung. Sie sollte nur im Heimnetz oder über einen abgesicherten VPN-Zugang erreichbar sein.
