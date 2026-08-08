# Stinkis’ Krankenakten – Version 0.6.8

Eine kleine, selbst gehostete Familien-Gesundheitschronik.

## Neu in Version 0.6.8

- Statuslogik korrigiert: Einträge ohne Enddatum bleiben nach ihrem Beginn **Laufend**. **Abgeschlossen** ist nur noch möglich, wenn ein echtes Enddatum in der Vergangenheit vorliegt.
- Statusfilter verwendet exakt dieselbe Logik wie die Timeline-Tags.
- Löschen in Medikamenten-/Allergie-Verwaltungsdialogen synchronisiert jetzt die sichtbaren Dashboard-Boxen sofort, ohne Seitenreload.
- Leere Personen-Gruppen verschwinden nach dem Löschen des letzten zugehörigen Eintrags automatisch.
- Die Medikationshistorie und abgeschlossene Allergien zeigen keine verwaisten Personennamen mehr; bei komplett leerer Historie erscheint ein sauberer Leerzustand.
- Notizen in den rechten Übersichtsboxen und Historien werden explizit mit **„Notiz:“** gekennzeichnet.
- Der Speichern-Button im Allergie-/Unverträglichkeitsdialog erhält nochmals mehr Abstand zum Formularende.
- Schema-Version bleibt **6**; bestehende JSON-Sicherungen aus v0.6.x sind direkt kompatibel.

## Parallel testen

Vorher in der laufenden Version über **Sicherung** einen aktuellen JSON-Export erstellen.

```bash
cd /docker/stinkis-krankenakten-v0.6.8
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
