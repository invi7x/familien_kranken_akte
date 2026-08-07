# Stinkis’ Krankenakten – Version 0.5.0

Eine kleine, selbst gehostete Familien-Gesundheitschronik.

## Neu in Version 0.5.0

### Ruhigere Allergie- und Medikamentenboxen

- In den rechten Mehrwertboxen gibt es nur noch **einen Verwaltungs-Stift pro Person**.
- Ein Klick öffnet ein personenbezogenes Popup mit allen aktiven Einträgen.
- Dort können einzelne Allergien bzw. Medikamente bearbeitet oder bei Fehleingaben gelöscht werden.
- Die störenden Trennlinien zwischen Einzelpositionen wurden entfernt.
- Abgeschlossene Allergien und beendete Medikamente bleiben weiterhin über ihre Historien erreichbar.

### Krankschreibung und Attest

Bei der Kategorie **Krankheit** erscheinen jetzt dynamisch zusätzliche Felder:

- ärztlich krankgeschrieben
- Krankgeschrieben von / bis
- Attest / ärztlicher Nachweis vorhanden
- Art des Attests (Arbeitsunfähigkeit, Schulattest, Sportbefreiung, sonstiges)

Die Angaben werden in der Timeline sowie in CSV- und PDF-Berichten berücksichtigt.

### Berichte

- Neben CSV gibt es jetzt einen **PDF-Bericht** als lesbare persönliche Gesundheitsakte.
- Person, Zeitraum, Kategorie und „nur wichtige“ können vor dem Export ausgewählt werden.
- Der PDF-Bericht enthält Allergiehistorie, Timeline, Medikamentendetails sowie Krankschreibung/Attest.
- CSV bleibt für Excel und eigene Auswertungen erhalten.

### UI-Feinschliff

- „Paperless- oder NAS-Link“ heißt nun neutral **„Externe URL / Link“**.
- Im Timeline-Eintrag heißt die Aktion entsprechend **„Link öffnen“**.
- Mehr Abstand zwischen den Formularfeldern und der Speichern-/Löschen-Leiste.
- Destruktive Löschaktionen bleiben räumlich klar vom Speichern getrennt.

### Datensicherung

- JSON-Schema ist jetzt **Version 5**.
- Alte Sicherungen bleiben importierbar.
- Profilbilder bleiben Bestandteil des JSON-Exports.
- Neue Krankschreibungs- und Attestfelder werden ebenfalls exportiert/importiert.

## Parallel testen

Vorher in der laufenden Version über **Sicherung** einen aktuellen JSON-Export erstellen.

```bash
cd /docker/stinkis-krankenakten-v0.5.0
sudo docker compose -f compose-test.yaml up -d --build
```

Aufruf:

```text
http://SERVER-IP:8491
```

Test-Volume:

```text
stinkis_v050_test_data
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
