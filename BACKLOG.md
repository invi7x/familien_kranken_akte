# Backlog – Stinkis’ Krankenakten

## In v0.6.2 erledigt

## In v0.6.5 erledigt

- Dirty-State-Bug behoben: Beim normalen Speichern/Importieren keine falsche „Website verlassen?“-Warnung mehr.
- Hauptsuche etwas schmaler; „Nur wichtige“ bleibt vollständig im Filterraster und ist sauber ausgerichtet.
- Personenkarten zeigen aktuelles Alter statt Geburtsdatum.
- Sicherungsdialog mit modernem Datei-Button, mehr Abstand und kürzerem Hinweistext.
- Datei-Upload beim Anlegen neuer Personen im gleichen modernen Stil.
- Formularabstände im Personen-Editor und an unteren Aktionsleisten verbessert.

- Statusfilter Geplant / Laufend / Abgeschlossen in der Timeline-Suche.
- Korrekte Gesamt-Trefferanzeige inklusive zukünftiger Einträge.
- Zukunftsvorschau auf fünf Einträge begrenzt, mit Auf-/Zuklappen weiterer Termine.
- Bei reinem Zukunftsfilter Pagination mit 20/50/100 Einträgen.
- Zeitraumfelder kompakter und Statusauswahl rechts daneben.
- „Nur wichtige“-Filter optisch auf gleiche Feldhöhe gebracht.
- Plus-Aktionen in den rechten Boxen auf reines Icon reduziert.
- Geschlechtssymbol näher an den Personennamen gerückt.
- Moderner Profilbild-Editor mit Avatar-/Initialenvorschau und verstecktem nativen File-Input.

## Nächste Ausbaustufen

- Jahresauswertung für ärztliche Krankschreibungen (Kalender-/Arbeitstage)
- Medikamente optional mit Diagnose, Krankheit, OP oder anderem Timeline-Eintrag verknüpfen
- Dosierungsänderungen und Pausierung einer Medikation historisch abbilden
- Profilbilder automatisch verkleinern und optional als Datei statt im JSON sichern
- Dokumentenanhänge zusätzlich zu externen URL-/Links
- Pollenflug-Widget mit externer Datenquelle und persönlicher Allergie-Zuordnung
- Grafischer Gesundheitsverlauf / interaktive Zeitachse unter Berichte (Marker für Ereignisse, Balken für Zeiträume, Zoom Monat/Jahr/Gesamt)
- Optionaler Status „verstorben am“ mit Archivierung und Schreibschutz (Priorität 99)
- Spätere neutrale Umbenennung für eine öffentliche Veröffentlichung


## In v0.5.0 erledigt

- Rechte Allergie- und Medikamentenboxen visuell beruhigt
- Nur noch ein Verwaltungs-Stift pro Person in den Mehrwertboxen
- Bearbeiten/Löschen einzelner Allergien und Medikamente in personenbezogenen Popups
- Trennlinien zwischen Einzelpositionen entfernt
- Mehr Abstand zwischen Formularfeldern und Speichern/Löschen-Aktionen
- „Paperless- oder NAS-Link“ neutral in „Externe URL / Link“ umbenannt
- Dynamische Krankschreibung-/Attest-Felder bei Kategorie Krankheit
- Eigener Zeitraum für ärztliche Krankschreibung und Attest-Typ
- Krankschreibung/Attest in Timeline und Exportdaten sichtbar
- PDF-Bericht zusätzlich zum CSV-Bericht
- PDF/CSV nach Person, Zeitraum, Kategorie und Wichtigkeit filterbar
- JSON-Schema 5; ältere Backups bleiben importierbar

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
- Jahresauswertung für Krankmeldungen / Atteste
- Pollenflug-Widget
- Archivierung verstorbener Personen (Prio 99)

## In v0.6.2 erledigt

- Filteraktionen links und Zeitraumfelder rechts angeordnet
- Wichtigkeitsfilter mit wiedererkennbarem `!`-Icon
- Gemeinsamer Inhaltsrahmen / bündigere Außenkanten
- Kontextübernahme beim Hinzufügen aus Allergie-/Medikamentenverwaltung
- Personenverwaltung mit Icon-Aktionen statt Textlinks
- Drag-&-Drop-Sortierung der Personen inklusive persistenter `sort_order`
- Personenreihenfolge Bestandteil des JSON-Backups
- Einheitliches „Hinzufügen“ und optisch zentriertes Plus-Icon
- Monats-Trenner in der historischen Timeline
- Harte Trennlinien zwischen Personengruppen in Mehrwertboxen entfernt

## Erledigt in v0.6.2
- [x] Drag & Drop ohne Dialog-Schließen / Seitenreload
- [x] App-eigener Löschdialog
- [x] Timeline-Status-Tags Geplant / Laufend / Abgeschlossen
- [x] Rechte Außenkante über ein strikt begrenztes gemeinsames Raster korrigiert

## Erledigt in v0.6.3
- Filterzeile neu ausgerichtet: Aktionen links, Zeitraum und Status rechts.
- Statusfeld kompakter dimensioniert; Datumsfelder bleiben innerhalb des gemeinsamen Rasters.
- Personengruppen in Allergie- und Medikamentenboxen als dezente Karten hervorgehoben.
