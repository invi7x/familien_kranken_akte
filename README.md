# Stinkis’ Krankenakten – Version 0.3.1

Eine kleine, selbst gehostete Familien-Gesundheitschronik.

## Neu in Version 0.3.1

### Seit v0.3.0: Medikamente nur noch über einen Erfassungsweg

- Medikamente werden ausschließlich über **+ Neuer Eintrag → Medikament** angelegt.
- Die Eingabemaske blendet bei der Kategorie **Medikament** automatisch zusätzliche Felder für **Dosierung**, **Grund / Indikation** und **Medikamenten-Unverträglichkeit** ein.
- Ein Medikament ist damit immer ein Timeline-Eintrag und gleichzeitig die Datenquelle für die rechte Medikamentenbox.
- Die rechte Box zeigt nur Medikamente, deren Zeitraum am aktuellen Datum läuft.
- Abgelaufene Medikamente verschwinden automatisch aus der aktuellen Box und bleiben unter **Beendete Medikamente anzeigen** erhalten.
- Der blaue Button **+ Eintragen** in der Medikamentenbox öffnet denselben zentralen Timeline-Dialog direkt mit vorausgewählter Kategorie Medikament.
- Aktive und beendete Medikamente können direkt aus der jeweiligen Übersicht bearbeitet werden; die Änderung wirkt gleichzeitig auf Timeline und Medikamentenübersicht.
- Alte Medikamentendaten aus v0.1/v0.2 werden beim Upgrade bzw. Import automatisch in das neue Timeline-Modell übernommen.

### Weitere Verbesserungen

- Medikamentendetails werden auch direkt im Timeline-Eintrag kompakt dargestellt.
- Zukünftig gestartete Medikamente werden noch nicht als aktuell laufend angezeigt.
- Beginn/Ende werden validiert; ein Enddatum vor dem Beginn wird abgefangen.
- Auch beendete Medikamente können aus der Historie wieder bearbeitet werden.
- JSON-Schema auf **Version 3** angehoben; alte Sicherungen bleiben importierbar.
- Der JSON-Export enthält weiterhin eine Medikamenten-Kompatibilitätsabbildung für ältere App-Stände.

## Parallel testen

Vorher in der laufenden Version über **Sicherung** einen aktuellen JSON-Export erstellen.

Für den Paralleltest ist `compose-test.yaml` enthalten. Sie verwendet Port **8489** und ein eigenes Volume:

```bash
cd /docker/stinkis-krankenakten-v0.3.1
docker compose -f compose-test.yaml up -d --build
```

Aufruf:

```text
http://SERVER-IP:8489
```

Test-Volume:

```text
stinkis_v031_test_data
```

Damit bleibt die bisherige Installation unangetastet.

## Installation als Hauptversion

```bash
cd /docker/stinkis-familienakte
docker compose up -d --build
```

Standardmäßig:

```text
http://SERVER-IP:8484
```

## Backup

Die Daten liegen standardmäßig im Docker-Volume `stinkis_krankenakten_data`. Zusätzlich kann über **Sicherung** ein JSON-Export erzeugt und wieder importiert werden. Profilbilder sind weiterhin als Base64-Daten im JSON enthalten.

## Sicherheit

Die App besitzt noch keine Anmeldung. Sie sollte nur im Heimnetz oder über einen abgesicherten VPN-Zugang erreichbar sein.


### UI und Timeline in v0.3.1

- Zukünftige Timeline-Einträge stehen separat unter **Kommende Einträge** und werden chronologisch aufsteigend sortiert.
- Ein **Heute**-Trenner grenzt geplante Einträge vom bisherigen Verlauf ab.
- Nur die Historie wird paginiert; kommende Einträge bleiben immer sichtbar.
- Bearbeiten/Löschen in Allergie- und Medikamentenboxen sind platzsparende Icon-Aktionen.
- **Filtern** und **Zurücksetzen** stehen gemeinsam unter dem Suchfeld.
- Oberer Inhalts- und Statusbereich nutzt dieselbe Gesamtbreite wie das Dashboard.
