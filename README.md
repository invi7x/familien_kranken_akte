# Stinkis’ Krankenakten – Version 0.7.0

Eine kleine, selbst gehostete Familien-Gesundheitschronik.

## Neu in Version 0.7.0

- Neuer optionaler **Behandlungsfall / Vorgang** verbindet zusammengehörige Timeline-Einträge.
- Krankheit, Arztbesuch und Medikament behalten trotzdem jeweils ihren eigenen Zeitraum.
- Beim Anlegen eines Eintrags kann ein bestehender Vorgang gewählt oder direkt ein neuer Vorgang angelegt werden.
- Nach dem Speichern eines verknüpften Eintrags erscheint eine kompakte Folgeaktion: **+ Arztbesuch**, **+ Medikament** oder **+ weiterer Eintrag**.
- Vorgangs-Badge in der Timeline öffnet eine Übersicht aller zugehörigen Einträge.
- JSON-Export/-Import enthält die Vorgänge; Schema-Version jetzt 7.
- CSV-Bericht erhält die zusätzliche Spalte **Vorgang**.
- Medikamentenbox rechts typografisch aufgeräumt: Name, Dosierung, Grund, Zeitraum und Notiz sind klarer gegliedert.
- Auf schmalen Mobil-Viewports wird **Neuer Eintrag** im Header als kompaktes rundes Plus dargestellt.
- **Externe URL / Link** ist jetzt ein freies Textfeld und akzeptiert damit auch NAS-/Netzwerkpfade oder andere Referenzen.
- Datumsfelder werden serverseitig strenger validiert; unvollständige oder ungültige Kalenderdaten werden abgewiesen.

## Parallel testen

```bash
cd /docker/stinkis-krankenakten-v0.7.0
sudo docker compose -f compose-test.yaml up -d --build
```

Aufruf: `http://SERVER-IP:8502`

Das Test-Volume heißt `stinkis_v070_test_data`.
