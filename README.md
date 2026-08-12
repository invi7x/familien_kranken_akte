# Familienakte

**Familienakte** ist eine selbst gehostete Familien-Gesundheitschronik für Docker. Gesundheitsereignisse, Medikamente, Allergien, Arztbesuche, Impfungen, Laborwerte und weitere Einträge lassen sich pro Person in einer gemeinsamen Timeline verwalten.

> Entwicklungsstand: **Beta / v0.8.4**. Die Anwendung wird bereits im Alltag getestet, ist aber noch auf dem Weg zu v1.0.

## Highlights

- mehrere Familienmitglieder mit Profilbild, Geburtsdatum und Geschlecht
- chronologische Timeline mit Kategorien, Status und Monatsabschnitten
- Krankheiten, Arztbesuche, Medikamente, Labor, Impfungen, OPs und Notizen
- Allergien und Unverträglichkeiten mit Historie
- laufende und abgeschlossene Medikation
- Behandlungsfälle / Vorgänge zum Verknüpfen zusammengehöriger Ereignisse
- Suche und Filter nach Person, Kategorie, Zeitraum, Status und Wichtigkeit
- JSON-Backup und Wiederherstellung
- automatische monatliche Server-Backups mit Download in der Weboberfläche
- CSV- und PDF-Berichte
- responsive Oberfläche für Desktop und Smartphone
- Docker-Compose-Deployment

## Screenshots

Screenshots folgen. Bitte für öffentliche Screenshots ausschließlich Demo-Daten verwenden und keine echten Gesundheitsdaten, Namen oder Profilbilder veröffentlichen.

## Schnellstart mit Docker Compose

### 1. Repository klonen

```bash
git clone https://github.com/DEIN-GITHUB-NAME/familienakte.git
cd familienakte
```

### 2. Secret ändern

Vor einer produktiven Nutzung in `compose.yaml` den Wert von `SECRET_KEY` durch einen langen zufälligen Wert ersetzen oder die Konfiguration auf eine `.env`-Datei umstellen.

### 3. Starten

```bash
docker compose up -d --build
```

Standardmäßig ist die Anwendung anschließend unter Port `8484` erreichbar:

```text
http://SERVER-IP:8484
```

## Persistente Daten

Docker Compose verwendet zwei benannte Volumes:

- `familienakte_data` – Datenbank und Anwendungsdaten
- `familienakte_backups` – automatische JSON-Sicherungen

Die automatischen Backups können direkt über **Sicherungen** in der Weboberfläche heruntergeladen werden.

## Updates

Vor einem Update empfiehlt sich ein manueller JSON-Export über **Sicherungen**.

Danach typischerweise:

```bash
git pull
docker compose up -d --build
```

Änderungen am Datenbankschema werden von der Anwendung beim Start migriert. JSON-Backups enthalten eine Schema-Version und sollen soweit möglich rückwärtskompatibel importiert werden können.

## Backup & Restore

Über **Sicherungen** stehen zur Verfügung:

- manueller JSON-Export
- Import eines vorhandenen JSON-Backups
- automatische monatliche Sicherung
- Download vorhandener Server-Backups

Backups können sensible Gesundheitsdaten und Profilbilder enthalten. Sie sollten entsprechend geschützt werden.

## Sicherheit und Datenschutz

Familienakte verarbeitet sensible Gesundheitsinformationen. Die Anwendung sollte nur in einer vertrauenswürdigen Umgebung betrieben werden.

Empfohlen:

- HTTPS über einen Reverse Proxy oder Zugriff per VPN
- starkes, individuelles `SECRET_KEY`
- regelmäßige Backups
- eingeschränkter Zugriff auf Docker-Volumes und Backup-Dateien
- keine echten Gesundheitsdaten in GitHub-Issues oder Screenshots

Weitere Hinweise stehen in [SECURITY.md](SECURITY.md).

## Projektstatus / Roadmap

Der aktuelle Schwerpunkt auf dem Weg zu v1.0 liegt auf Stabilität, Restore-Tests, Reports und Release-Dokumentation. Größere spätere Ideen sind unter anderem Mehrsprachigkeit und eine grafische Gesundheits-Zeitachse.

Siehe auch [BACKLOG.md](BACKLOG.md) und [CHANGELOG.md](CHANGELOG.md).

## Mitmachen

Bugreports, Feature-Ideen und Pull Requests sind willkommen. Bitte vorab [CONTRIBUTING.md](CONTRIBUTING.md) lesen.

## Lizenz

MIT – siehe [LICENSE](LICENSE).

## Hinweis

Familienakte ist kein Medizinprodukt und ersetzt keine medizinische Beratung, Diagnose oder Behandlung.
