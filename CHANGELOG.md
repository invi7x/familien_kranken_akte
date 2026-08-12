## 0.8.4

- Sicherungsdialog bleibt nach Speichern und Sofort-Backup als echtes Modal geöffnet; kein Seitenreload.
- Backup-Status, letzte Sicherung und Backup-Liste werden direkt im Dialog aktualisiert.
- Formularraster für „Tag im Monat“ und „Sicherungen behalten“ sauber ausgerichtet.

# Changelog

## 0.8.3
- Importfehler bei `treatment_cases.updated_at = null` behoben.
- Fehlende Vorgangs-Zeitstempel werden beim Start und Import automatisch normalisiert.
- Exporte schreiben für Vorgänge künftig immer einen belastbaren `updated_at`-Wert.
- Neue Vorgänge erhalten Zeitstempel explizit beim Anlegen.

## 0.8.2
- Docker-Service-, Container- und Volume-Namen auf neutrale `familienakte_*`-Bezeichnungen umgestellt.
- Sicherungsdialog responsiv korrigiert; horizontales Scrollen entfernt und Backup-Zeilen für kleine Viewports optimiert.
- Pollenflug-Platzhalter aus der Oberfläche entfernt; Feature vorerst zurückgestellt.

## 0.8.1
- Sicherungen + automatische Backup-Einstellungen in einem Dialog zusammengeführt.
- Download vorhandener Server-Backups über die Weboberfläche.
- Maximale Backup-Aufbewahrung auf 10 begrenzt.
- Neutralere Backup-/Export-Dateinamen.
- Sub-Cards für mehrere Allergie-/Medikamenteneinträge je Person.
- Einheitlicher Notiztrenner.

## 0.8.0
- Einstellungen-Bereich eingeführt.
- Monatliche automatische JSON-Backups mit eigenständigem Docker-Scheduler.
- Backup-Ziel, Tag im Monat und Aufbewahrungsanzahl konfigurierbar.
- Sofortiges Server-Backup per Button.
- Eigenes persistentes Backup-Volume in Compose.
- Typografisches Polish der rechten Medikamenten-/Allergieboxen.

## 0.7.x
- Behandlungsfälle/Vorgänge mit Status Aktiv, Abgeschlossen und Archiviert.
- Verknüpfung von Krankheiten, Arztbesuchen, Medikamenten und weiteren Timeline-Einträgen.
- Vorgangsverwaltung und Vorgangsstatus direkt im Vorgangsfenster.
