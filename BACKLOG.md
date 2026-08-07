# Backlog – Stinkis’ Krankenakten

## Nächste Ausbaustufen

- Ärztliche Krankschreibung / Attest mit eigenem Zeitraum und späterer Jahresauswertung
- Medikamente optional mit Diagnose, Krankheit, OP oder anderem Timeline-Eintrag verknüpfen
- Dosierungsänderungen und Pausierung einer Medikation historisch abbilden
- Profilbilder automatisch verkleinern und optional als Datei statt im JSON sichern
- Dokumentenanhänge zusätzlich zu Paperless-/NAS-Links
- Pollenflug-Widget mit externer Datenquelle und persönlicher Allergie-Zuordnung
- Optionaler Status „verstorben am“ mit Archivierung und Schreibschutz (Priorität 99)
- Spätere neutrale Umbenennung für eine öffentliche Veröffentlichung

## In v0.4.0 erledigt

- Kommende Timeline-Einträge optisch und logisch vom bisherigen Verlauf getrennt
- Deutlicher Heute-Trenner
- Zukunft aufsteigend, Historie absteigend sortiert
- Pagination nur für historische Einträge
- Kompakte Stift-/Löschen-Icons in Allergie- und Medikamentenboxen
- Filter- und Zurücksetzen-Button unter dem Suchfeld nebeneinander
- Einheitlich breiter Dashboard- und Statusbereich

## In v0.3.0 erledigt

- Medikamente besitzen nur noch einen Erfassungsweg: + Neuer Eintrag → Medikament
- Dynamische Medikamentenfelder in Neu-/Bearbeiten-Dialogen
- Timeline ist zentrale Datenquelle für Medikamente und rechte Medikamentenbox
- Aktive Medikamente werden anhand des heutigen Datums automatisch ermittelt
- Abgelaufene Medikamente bleiben in der Medikationshistorie erhalten
- Alte separate Medikamentendaten werden automatisch migriert
- Bearbeiten aus aktueller Medikamentenbox und Historie
- Medikamenten-Quick-Action öffnet den zentralen Timeline-Dialog
- Medikamentendetails werden in der Timeline angezeigt
- Validierung von Beginn/Ende
- JSON-Schema 3 mit Import alter v0.1/v0.2-Sicherungen

## In v0.2.2 erledigt

- Allergien und Medikamente können bearbeitet werden
- Allergiebezeichnung und Reaktion stehen kompakt in einer Zeile; Notizen darunter
- Personenfilter wirkt auch auf rechte Mehrwertspalten
- Timeline-Bearbeitung als Stift-Icon für Desktop und Mobil
- Löschaktion im Bearbeiten-Dialog klar vom Speichern getrennt
- Timeline-Paginierung mit 20/50/100 Einträgen pro Seite

## Dauerhafte Anforderungen

- JSON-Export und Import bleiben versionsübergreifend erhalten.
- Profilbilder bleiben im Backup erhalten.
- Alte Sicherungen werden durch Schema-Migration weiter unterstützt.
- Einträge werden in Übersichten grundsätzlich nach Person gruppiert.
- Die Hauptansicht bleibt einfach; selten benötigte Funktionen wandern in Dialoge.

## Erledigt in v0.4.0
- Allergien abschließen statt historisch löschen
- Allergiehistorie mit Start-/Enddatum und Abschlussnotiz
- Avatar direkt in der Timeline
- Zeitraumfilter mit Überschneidungslogik
- CSV-Berichte pro Person / Zeitraum / Kategorie

## Als Nächstes / später
- PDF-Bericht als druckbare Patientenakte
- Krankmeldung / Attest und Jahresauswertung
- Pollenflug-Widget
- Archivierung verstorbener Personen (Prio 99)
