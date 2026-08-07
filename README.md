# Stinkis’ Krankenakten – Version 0.2.2

Eine kleine, selbst gehostete Familien-Gesundheitschronik.

## Neu in Version 0.2.2

- Personenfilter wirkt jetzt auch auf Allergien, Medikamente und Medikationshistorie in der rechten Spalte
- Timeline-Bearbeitung als platzsparendes Stift-Icon, auch für schmale Handy-Viewports rechts oben
- Löschbutton im Dialog „Eintrag bearbeiten“ räumlich ganz nach rechts getrennt
- Allergie/Unverträglichkeit: Bezeichnung und Reaktion kompakt in einer Zeile, Notiz weiterhin darunter
- Allergien und Unverträglichkeiten können jetzt bearbeitet werden
- Medikamente können jetzt bearbeitet werden
- Timeline mit 20/50/100 Einträgen pro Seite und Seitennavigation
- Trefferanzeige zeigt den aktuellen Bereich, z. B. „21–40 von 187 Treffern“
- Profilbilder bleiben Bestandteil des JSON-Exports und werden beim Import wiederhergestellt

## Update / Test parallel zur bisherigen Version

Vorher in der laufenden Version über **Sicherung** einen JSON-Export erstellen.

Für einen parallelen Test ist bereits `compose-test.yaml` enthalten. Sie nutzt Port **8487**, einen eigenen Containernamen und ein eigenes Test-Volume. Der Inhalt entspricht:

```yaml
services:
  stinkis-krankenakten-v022:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: stinkis-krankenakten-v022
    restart: unless-stopped
    environment:
      DATA_DIR: /data
      SECRET_KEY: change-this-secret-key
    ports:
      - "8487:8484"
    volumes:
      - stinkis_v022_test_data:/data
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8484/health')"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 15s

volumes:
  stinkis_v022_test_data:
    name: stinkis_v022_test_data
```

Danach:

```bash
docker compose -f compose-test.yaml up -d --build
```

Im Beispiel ist die Testversion unter `http://SERVER-IP:8487` erreichbar.

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

Die Daten liegen standardmäßig im Docker-Volume `stinkis_krankenakten_data`. Zusätzlich kann über **Sicherung** ein JSON-Export erzeugt und wieder importiert werden. Profilbilder sind als Base64-Daten im JSON enthalten.

## Sicherheit

Die App besitzt noch keine Anmeldung. Sie sollte nur im Heimnetz oder über einen abgesicherten VPN-Zugang erreichbar sein.
