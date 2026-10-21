# ThuisWeb met Docker

ThuisWeb werkt ook zonder Unraid. Gebruik Docker Desktop op een Windows-pc met een Intel- of AMD-processor, of Docker Engine met Compose op Linux (x86-64). De image wordt voor `linux/amd64` gepubliceerd; ARM wordt niet native ondersteund.

## Windows: beginnen in drie stappen

### 1. Installeer Docker Desktop

Volg de [officiële Windows-installatiehandleiding](https://docs.docker.com/desktop/setup/install/windows-install/), start Docker Desktop en gebruik **Linux-containers** (standaard met WSL 2). Open daarna een nieuw PowerShell-venster.

### 2. Maak een eigen map en download het Compose-bestand

Gebruik een nieuwe, lege map voor je eerste website. Git en een GitHub-account zijn niet nodig.

```powershell
New-Item -ItemType Directory -Path "$HOME\ThuisWeb"
Set-Location "$HOME\ThuisWeb"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/marcvandecoevering/ThuisWeb/main/compose.yaml" -OutFile compose.yaml
New-Item -ItemType Directory -Path www, config
```

### 3. Start ThuisWeb

```powershell
docker compose up -d
```

Open **[http://localhost:8583](http://localhost:8583)**. De eerste download kan enkele minuten duren. Je ziet de ThuisWeb-startpagina met de actuele componentversies.

## Je eigen website plaatsen

Open de map `ThuisWeb\www` in Verkenner en plaats daar je HTML-, CSS-, JavaScript- en PHP-bestanden. Vervang `index.html` door je eigen pagina of plaats `index.php`; PHP heeft voorrang. Ververs je browser om wijzigingen te zien. Een database zit niet in deze container.

De map `config` bewaart instellingen. Een eigen `config/php.ini` wordt na `docker compose restart` toegepast. De startpagina wordt alleen in een volledig lege websitemap geplaatst; bestaande bestanden worden niet overschreven.

## Stoppen en bijwerken

Voer deze opdrachten steeds uit vanuit de map met `compose.yaml`.

| Actie | Opdracht |
| --- | --- |
| Status bekijken | `docker compose ps` |
| Logs bekijken | `docker compose logs --tail=100 thuisweb` |
| Stoppen | `docker compose stop` |
| Weer starten | `docker compose up -d` |
| Container verwijderen | `docker compose down` |

Je bestanden in `www` en `config` blijven bij deze opdrachten staan. Maak vóór een update een back-up van beide mappen en van een eventuele database. Werk daarna bij met:

```powershell
docker compose pull
docker compose up -d
```

Updates overschrijven je website en bestaande startpagina niet. Docker Desktop moet draaien om de website te kunnen openen.

## Andere poort of meerdere websites

Is poort 8583 bezet? Maak naast `compose.yaml` een bestand `.env` met:

```dotenv
THUISWEB_PORT=8584
```

Voer opnieuw `docker compose up -d` uit en open `http://localhost:8584`.

Voor een tweede website maak je een aparte map, bijvoorbeeld `ThuisWeb-twee`, met een eigen kopie van `compose.yaml`, eigen `www` en `config`, en een andere poort in `.env`. Gebruik verschillende mapnamen: Compose gebruikt de mapnaam als projectnaam.

Dit voorbeeld luistert alleen op je eigen pc (`127.0.0.1`). Voor bereikbaarheid op je thuisnetwerk verander je de poortregel in `"${THUISWEB_PORT:-8583}:8080"` en configureer je zo nodig de firewall. Een domeinnaam en HTTPS regel je afzonderlijk via een reverse proxy.

## Linux

Installeer Docker Engine en de Docker Compose-plugin. Download [compose.yaml](../compose.yaml) naar een eigen projectmap en maak daarin `www` en `config`. Zet in `.env` de numerieke gebruikers- en groeps-ID's die je met `id -u` en `id -g` opvraagt:

```dotenv
PUID=1000
PGID=1000
```

Vervang de voorbeeldwaarden door je eigen niet-root ID's. Bestaande websitebestanden moeten leesbaar zijn voor die gebruiker; uploadmappen moeten ook schrijfbaar zijn. Start met `docker compose up -d` en open `http://localhost:8583`.

## Problemen oplossen

- **Docker wordt niet herkend:** open een nieuw PowerShell-venster na de installatie.
- **Geen verbinding met Docker:** start Docker Desktop en wacht totdat de engine gereed is.
- **Windows-containers geselecteerd:** schakel over naar Linux-containers.
- **Poort al in gebruik:** stel een andere poort in zoals hierboven.
- **Geen toegang tot de websitemap:** controleer Docker Desktop-bestandsdeling en de maprechten; gebruik een lokale map buiten OneDrive of een netwerkschijf.

Meer over instellingen, back-ups en rechten: [handleiding](handleiding.md).
