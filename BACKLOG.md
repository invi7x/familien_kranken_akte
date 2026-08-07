# Backlog – Stinkis’ Krankenakten

## Nächste Ausbaustufen

- Ärztliche Krankschreibung / Attest mit eigenem Zeitraum und späterer Jahresauswertung
- Medikamente optional mit Diagnose, Krankheit, OP oder anderem Timeline-Eintrag verknüpfen
- Dosierungsänderungen und Pausierung einer Medikation
- Profilbilder automatisch verkleinern und optional als Datei statt im JSON sichern
- Dokumentenanhänge zusätzlich zu Paperless-/NAS-Links
- Pollenflug-Widget mit externer Datenquelle und persönlicher Allergie-Zuordnung
- Optionaler Status „verstorben am“ mit Archivierung und Schreibschutz (Priorität 99)
- Spätere neutrale Umbenennung für eine öffentliche Veröffentlichung

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
