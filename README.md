# ThuisWeb

Een eigen Apache/PHP-webserver voor Unraid: één website per container, met een
Nederlandstalige landingpagina voor nieuwe, volledig lege websitemappen.

**Status: lokaal en in GitHub Actions gebouwd, getest en gescand op 21 oktober 2026.
De image is openbaar beschikbaar; de Unraid-basistests zijn geslaagd.
Update/rollback en opname in Community Applications volgen nog.**
Zie [testresultaten](docs/testresultaten.md). Openbare broncode:
https://github.com/marcvandecoevering/ThuisWeb.

Image: `ghcr.io/marcvandecoevering/thuisweb:php8.3`. Anoniem downloaden is gecontroleerd.
[Eerste geslaagde release](https://github.com/marcvandecoevering/ThuisWeb/actions/runs/39663665343).

## Installatie op Unraid (na publicatie)

Zoek ThuisWeb in Apps zodra de app is toegelaten, kies Install en controleer:

| Instelling | Standaard |
| --- | --- |
| Netwerk | bridge |
| Hostpoort → containerpoort | 8583 → 8080 |
| Website | `/mnt/user/appdata/thuisweb/www` → `/var/www/html` |
| Configuratie | `/mnt/user/appdata/thuisweb/config` → `/config` |
| PUID / PGID | 99 / 100 |
| PHP-geheugen | 256M |
| Upload per bestand | 32M (32 MiB) |
| Tijdzone | Europe/Amsterdam |

Open WebUI. Bij een lege websitemap staat de landingpagina klaar. Vervang
`index.html` of plaats `index.php`; PHP heeft voorrang. Ook verborgen bestanden
maken een map niet-leeg. ThuisWeb overschrijft geen bestaande websitebestanden
en verandert hun eigenaarschap niet automatisch.

Voor website twee: installeer nog een container met een **andere containernaam,
vrije hostpoort, websitemap én configuratiemap**, bijvoorbeeld `ThuisWeb-twee`,
8584 en `/mnt/user/appdata/thuisweb-twee/{www,config}`. Iedere container heeft
eigen bestanden en instellingen. Poort 8582 is op de doelserver al in gebruik.

Installatie maakt geen routerregels, DNS of certificaten aan. Regel HTTPS via
je bestaande reverse proxy. Databases en SMTP-diensten staan los van ThuisWeb.
Node.js, Python-hosting, WordPress-installatie, een mailserver en een browser-
of bestandsbeheerpaneel maken geen deel uit van versie 1.

## Rechten en configuratie

Het opstartproces en de Apache-master starten als root voor initialisatie.
Apache-workers verwerken verzoeken onder de numerieke PUID/PGID. Beide moeten
positief en ongelijk aan nul zijn. Geen privileged-modus, hostnetwerk of
Docker-socket is nodig. Een nieuw geïnitialiseerde websitemap krijgt de gekozen
eigenaar; er wordt nooit recursief gechownd. Bestaande mappen moeten zelf lees-
en doorlooprechten geven. Alleen uploadmappen die je website nodig heeft hoeven
schrijfbaar te zijn voor PUID/PGID. Geef geen algemene 777-rechten.

`PHP_MEMORY_LIMIT` en `PHP_UPLOAD_LIMIT` accepteren positieve hele waarden in M
of G. `post_max_size` krijgt de uploadlimiet plus minimaal 8 MiB of 10% overhead.
De geheugenlimiet moet minstens deze som zijn. Bij 32M wordt post_max_size 40M.
PHP meldt te grote bestanden via `UPLOAD_ERR_INI_SIZE`; de website moet die
fout correct afhandelen. Een te grote totale POST kan lege POST/FILES opleveren.

Een optioneel `/config/php.ini` wordt bij iedere herstart gekopieerd naar de
laatst ingelezen configuratie. Dit is **vertrouwde beheerdersconfiguratie**:
het mag defaults overschrijven, ook beveiligings- en uploadinstellingen.
Gebruik het alleen als beheerder. Syntaxfouten en PHP-startwaarschuwingen
blokkeren het starten. Herstart na aanpassen. Verwijder het bestand om terug
te gaan naar de defaults.

`/config/.thuisweb-initialized` voorkomt dat een eenmaal geplaatste landingpagina
terugkeert wanneer je later alle websitebestanden verwijdert. Bewaar deze marker
bij back-ups en containervervanging. Gebruik per website een eigen configmap.
Sessies staan standaard in de container en gaan verloren bij vervanging;
voor duurzame sessies configureer je zelf een geschikte sessieopslag.

## Logs en problemen oplossen

Unraid → Docker → ThuisWeb → Logs toont Apache-verzoeken en server-/PHP-fouten.
PHP-fouten zijn standaard niet zichtbaar voor bezoekers; directorylisting en
versiedetails zijn uitgeschakeld. `.htaccess` ondersteunt herschrijven,
authenticatie en toegangsregels; het mag directorylisting niet inschakelen.

De healthcheck gebruikt `127.0.0.1:8081` binnen de container. Publiceer die poort
niet. Deze statische interne virtual host gebruikt geen websitebestanden of
`.htaccess`. Healthy betekent dat Apache reageert, niet dat je website of database
correct werkt. PHP-versie en extensies worden afzonderlijk bij opstart gecontroleerd.

Bij een rechtenfout: controleer de gekozen hostmap, PUID/PGID en rechten op alle
bovenliggende mappen. Bij PHP-configuratiefouten: herstel of hernoem php.ini en
herstart. Een fout in je website verhindert toegang tot Unraid-beheer niet.

## Updates, back-up en herstel

1. Noteer vóór een update de unieke image-tag/digest en containerinstellingen.
2. Stop de website kort voor een consistente back-up. Kopieer `www` en `config`,
   inclusief verborgen bestanden, rechten en eigenaarschap. Maak daarnaast een
   database-eigen dump/snapshot als de website een database gebruikt.
3. Start de website weer. Installeer de geteste update via Unraid en controleer
   WebUI, logs, healthcheck en belangrijke websitefuncties.
4. Test een herstel eerst met nieuwe mappen en een vrije poort. Zet zowel website
   als bijbehorende database terug naar een consistente toestand.
5. Alleen bij een nog veilige vorige release kun je de repository tijdelijk
   vastzetten op de unieke buildtag/digest. Maak een bekende kwetsbare release
   niet opnieuw publiek bereikbaar; is geen veilige rollback beschikbaar, haal
   de website tijdelijk offline en herstel met een gerepareerde image.

Automatisch publiceren naar GHCR is **geen automatische installatie op Unraid**.
Bestaande containers veranderen pas via Unraid of je gekozen updatevoorziening.

## Lokaal bouwen en testen

Benodigd: Git, Python 3.11+ en Docker Desktop met een draaiende Linux-engine
(amd64). Werk in deze projectmap. Gebruik geen productiemounts.

```powershell
python scripts/validate.py
python scripts/build.py
```

De build resolveert de nieuwste officiële PHP 8.3-patch via php.net en legt het
linux/amd64-manifestdigest vast. De Dockerfile vereist dit BASE_IMAGE-argument;
een losse build zonder de resolver faalt bewust. De pipeline bouwt eenmaal,
test die image-ID, exporteert diezelfde image, scant het archief en bewaart het
SBOM en alle resultaten in `artifacts`. Er wordt lokaal niets gepubliceerd.
De tests gebruiken tijdelijke UUID-containers, volumes en een apart netwerk;
ze publiceren geen hostpoorten en ruimen uitsluitend eigen middelen op.

Een afgebroken proces kan testmiddelen achterlaten. Bekijk eerst namen met
prefix `thuisweb-test-`; verwijder alleen de middelen van de afgebroken run.
Gebruik geen globale Docker-prune op een server met andere projecten.

## Beveiliging en onderhoud

PHP 8.3.36 is op 21 oktober 2026 de actuele minimumversie voor de twee genoemde
kritieke kwetsbaarheden. De build vraagt daarnaast steeds de nieuwste 8.3-patch
op en weigert afwijkende/oudere versies, ook als de scanner geen CVE herkent.
PHP 8.3 ontvangt volgens upstream beveiligingsonderhoud tot 31 december 2027.
Er wordt nooit automatisch naar een andere PHP-reeks overgeschakeld.

Dagelijks, bij pushes op main, handmatig en bij PRs wordt gebouwd/getest/gescand.
Alleen main-runs kunnen na succes publiceren. Hoge/kritieke kwetsbaarheden met
beschikbare reparatie blokkeren publicatie. Zonder reparatie blijven ze zichtbaar
in het scanrapport. Een onbereikbare scanner/database of onvolledige scan blokkeert
ook. Een geslaagde scan garandeert geen afwezigheid van kwetsbaarheden. Eigen
imageonderhoud blijft afhankelijk van upstream-reparaties en actuele scanners.

Actions zijn op gecontroleerde commits gepind; de scanner op een image-digest.
Werk die pins bewust bij. PRs krijgen alleen leesrechten en ontvangen geen
publicatiegeheimen. Het publiceren gebeurt in een afzonderlijke job met
package-schrijfrechten. Digest/commit/PHP-versie/scans/SBOM blijven als artifacts
90 dagen beschikbaar; het imagearchief 7 dagen. Archiveer releasebewijs extern
als je het langer wilt bewaren. Unieke buildtags worden niet hergebruikt.

Configureer GitHub Actions-foutmeldingen en controleer periodiek of dagelijkse
runs nog plaatsvinden; zie [publicatie](docs/publicatie.md). De laatste geslaagde
tag blijft bij een test- of scanfout beschikbaar.

## Bronnen

- [Officiële PHP-image](https://hub.docker.com/_/php)
- [PHP-berichten 2026](https://www.php.net/archive/2026.php)
- [Ondersteunde PHP-versies](https://www.php.net/supported-versions.php)
- [Community Applications](https://docs.unraid.net/community-applications/)
- [Templatevereisten](https://ca.unraid.net/submit/help/repository-xml)
- [Unraid-testprotocol](docs/unraid-test.md)

MIT-licentie; zie LICENSE.
