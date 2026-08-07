# Stinkis’ Krankenakten – Version 0.6.0

Eine kleine, selbst gehostete Familien-Gesundheitschronik.

## Neu in Version 0.6.0

- Filterbox logisch neu angeordnet: **Filtern | Zurücksetzen** links, **Zeitraum von | bis** rechts.
- Der Filter **„Nur wichtige“** nutzt jetzt dasselbe `!`-Kennzeichen wie wichtige Timeline-Einträge.
- Gemeinsamer Inhaltsrahmen für Personenleiste, Filter, Timeline und rechte Mehrwertspalte; die Außenkanten sind auf dasselbe Raster gezogen.
- Allergie-/Medikamenten-Popups übernehmen beim Hinzufügen automatisch die Person, aus deren Verwaltung sie geöffnet wurden.
- Personenverwaltung verwendet konsequent Stift-/Mülleimer-Icons statt Bearbeiten-/Löschen-Text.
- Personen lassen sich in der Verwaltung per **Drag & Drop** sortieren; die Reihenfolge gilt anschließend auch in Übersicht, Auswahlfeldern und Mehrwertboxen.
- Die Personenreihenfolge wird im JSON-Backup über `sort_order` mitgesichert.
- „Hinzufügen“ ist in Allergie- und Medikamentenbox vereinheitlicht; Plus-Symbole sind optisch zentriert.
- Historische Timeline ist zusätzlich nach **Monaten** gegliedert (z. B. „August 2026“, „Juli 2026“).
- Rechte Mehrwertboxen verzichten auf harte Trennlinien zwischen Personengruppen.
- JSON-Schema **6**; ältere Sicherungen bleiben importierbar.

## Parallel testen

Vorher in der laufenden Version über **Sicherung** einen aktuellen JSON-Export erstellen.

```bash
cd /docker/stinkis-krankenakten-v0.6.0
sudo docker compose -f compose-test.yaml up -d --build
```

Aufruf:

```text
http://SERVER-IP:8493
```

Test-Volume:

```text
stinkis_v060_test_data
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

Die Daten liegen standardmäßig im Docker-Volume `stinkis_krankenakten_data`. Zusätzlich kann über **Sicherung** ein JSON-Export erzeugt und wieder importiert werden. Profilbilder und die benutzerdefinierte Personenreihenfolge sind Bestandteil des Exports.

## Sicherheit

Die App besitzt noch keine Anmeldung. Sie sollte nur im Heimnetz oder über einen abgesicherten VPN-Zugang erreichbar sein.
