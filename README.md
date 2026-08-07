# Stinkis’ Krankenakten – Version 0.5.1

Eine kleine, selbst gehostete Familien-Gesundheitschronik.

## Neu in Version 0.5.1

- Filterbox neu geordnet: Such-/Kategoriezeile plus sauber integrierte Zeitraum-/Aktionszeile.
- Personenleiste, Filter, Statusmeldungen und Dashboard nutzen ein konsistentes gemeinsames Seitenraster.
- Mehr Abstand zwischen dem letzten Formularfeld und Speichern-/Löschen-Aktionen.
- Dialoge schließen nicht mehr durch Klick auf den Hintergrund oder Escape.
- Bei ungespeicherten Formularänderungen warnt „Schließen“ vor dem Verwerfen.
- Offene, geänderte Dialoge schützen zusätzlich vor versehentlichem Verlassen/Neuladen der Seite.
- Die ruhige Personenverwaltung für Allergien und Medikamente aus v0.5.0 bleibt erhalten.

## Parallel testen

Vorher in der laufenden Version über **Sicherung** einen aktuellen JSON-Export erstellen.

```bash
cd /docker/stinkis-krankenakten-v0.5.1
sudo docker compose -f compose-test.yaml up -d --build
```

Aufruf:

```text
http://SERVER-IP:8492
```

Test-Volume:

```text
stinkis_v051_test_data
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
