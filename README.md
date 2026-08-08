# Stinkis’ Krankenakten – Version 0.6.7

Eine kleine, selbst gehostete Familien-Gesundheitschronik.

## Neu in Version 0.6.7

- Bugfix: Beim bewussten Speichern/Importieren erscheint keine irreführende Browser-Warnung „Website verlassen?“ mehr.
- Filterbox nachpoliert: Hauptsuche etwas kompakter, **Nur wichtige** sauber im Raster und auf einheitlicher Feldhöhe.
- Personen-Karten zeigen jetzt das **aktuelle Alter** statt des Geburtsdatums.
- Sicherungsdialog aufgeräumt und Hinweistext verkürzt.
- Moderner Datei-Button **Sicherung auswählen** statt nativer Browser-Dateiauswahl.
- Einheitlicher moderner Datei-Button auch beim Anlegen neuer Personen.
- Mehr Abstand zwischen Dateiauswahl und Import-Button.
- Mehr Luft zwischen „Der Name bleibt unverändert.“ und dem Feld „Geburtsdatum“.
- Untere Speichern-/Import-Aktionsleisten bekommen konsistent mehr Abstand zum letzten Eingabefeld.
- Favicon aus v0.6.4 bleibt eingebunden.
- Datenschema bleibt **Version 6**; bestehende v0.6.x-Backups sind direkt kompatibel.

## Parallel testen

Vorher in der laufenden Version über **Sicherung** einen aktuellen JSON-Export erstellen.

```bash
cd /docker/stinkis-krankenakten-v0.6.7
sudo docker compose -f compose-test.yaml up -d --build
```

Aufruf:

```text
http://SERVER-IP:8497
```

Test-Volume:

```text
stinkis_v065_test_data
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
