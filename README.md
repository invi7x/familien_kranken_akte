# Stinkis’ Krankenakten – Version 0.4.0

Eine kleine, selbst gehostete Familien-Gesundheitschronik.

## Neu in Version 0.4.0

### Allergien behalten ihre Historie

- Allergien und Unverträglichkeiten können jetzt optional mit **Bekannt seit** versehen werden.
- Beim Bearbeiten gibt es **Tritt nicht mehr auf / abgeschlossen**.
- Dazu können ein Abschlussdatum und eine Abschlussnotiz hinterlegt werden.
- Abgeschlossene Einträge verschwinden aus der aktuellen rechten Übersicht, werden aber **nicht gelöscht**.
- Über **Abgeschlossene Allergien anzeigen** bleibt die gesamte Historie einsehbar.
- Historische Allergien können wieder bearbeitet bzw. reaktiviert werden.

### Timeline und Suche

- Der Avatar der Person wird jetzt auch direkt in jedem Timeline-Eintrag angezeigt.
- Die Suche besitzt einen optionalen **Zeitraum von / bis**.
- Mehrtägige Einträge werden gefunden, sobald sich ihr Zeitraum mit dem Suchzeitraum überschneidet.
- Personen-, Kategorie-, Wichtigkeits- und Zeitraumfilter lassen sich kombinieren.

### Berichte

- Oben gibt es neu **Berichte**.
- Für eine Person kann eine Excel-kompatible **CSV-Akte** exportiert werden.
- Person, Zeitraum, Kategorie und „nur wichtige“ können ausgewählt werden.
- Der CSV-Bericht enthält Timeline-Einträge, Medikationsdetails und die Allergiehistorie.
- PDF bleibt für eine spätere Version im Backlog.

### Datensicherung

- JSON-Schema ist jetzt **Version 4**.
- Alte Sicherungen bleiben importierbar.
- Profilbilder bleiben Bestandteil des JSON-Exports.
- Neue Allergie-Historienfelder werden ebenfalls exportiert/importiert.

## Parallel testen

Vorher in der laufenden Version über **Sicherung** einen aktuellen JSON-Export erstellen.

```bash
cd /docker/stinkis-krankenakten-v0.4.0
sudo docker compose -f compose-test.yaml up -d --build
```

Aufruf:

```text
http://SERVER-IP:8490
```

Test-Volume:

```text
stinkis_v040_test_data
```

Damit bleibt die bisherige Installation unangetastet.

## Installation als Hauptversion

```bash
cd /docker/stinkis-familienakte
sudo docker compose up -d --build
```

Standardmäßig:

```text
http://SERVER-IP:8484
```

## Backup

Die Daten liegen standardmäßig im Docker-Volume `stinkis_krankenakten_data`. Zusätzlich kann über **Sicherung** ein JSON-Export erzeugt und wieder importiert werden.

## Sicherheit

Die App besitzt noch keine Anmeldung. Sie sollte nur im Heimnetz oder über einen abgesicherten VPN-Zugang erreichbar sein.
