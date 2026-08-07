# Stinkis’ Krankenakten – Version 0.6.3

Eine kleine, selbst gehostete Familien-Gesundheitschronik.

## Neu in Version 0.6.3

- Neuer Timeline-Filter **Status** mit **Geplant / Laufend / Abgeschlossen**.
- Die beiden Zeitraumfelder sind kompakter; der Statusfilter sitzt rechts daneben.
- **Nur wichtige** ist auf dieselbe Feldhöhe wie die übrigen Filter gebracht.
- Trefferanzeige zählt jetzt **Zukunft + Vergangenheit** und weist beide Anteile getrennt aus.
- Kommende Einträge zeigen standardmäßig höchstens **5 Termine**; weitere können mit einem Klick ein-/ausgeblendet werden.
- Bei Filter **Status = Geplant** greift die normale 20/50/100-Pagination auch für zukünftige Einträge.
- In Allergie- und Medikamentenboxen bleibt nur noch das kompakte blaue **+** ohne langen „Hinzufügen“-Text.
- Geschlechtssymbol steht in den Mehrwertboxen direkt neben dem Personennamen.
- Profilbild-Bereich in **Person bearbeiten** modernisiert: aktueller Avatar/Initialen, eigener Bild-auswählen-Button und Dateivorschau.
- Datenschema bleibt **Version 6**; v0.6.1-Backups sind direkt kompatibel.

## Parallel testen

Vorher in der laufenden Version über **Sicherung** einen aktuellen JSON-Export erstellen.

```bash
cd /docker/stinkis-krankenakten-v0.6.4
sudo docker compose -f compose-test.yaml up -d --build
```

Aufruf:

```text
http://SERVER-IP:8496
```

Test-Volume:

```text
stinkis_v063_test_data
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

### v0.6.4
- Filter-Aktionen wieder konsequent links, Zeitraum und Status rechts gruppiert.
- Statusauswahl kompakter; Datumsfelder bleiben im Inhaltsraster.
- Allergie- und Medikamentengruppen je Person dezent eingerahmt/hinterlegt.
