# Acceptatie op Unraid 192.168.1.10

Status: basistests, image-update en rollback geslaagd op 21 oktober 2026,
Unraid 7.3.3 / linux amd64.
Proefcontainers: `ThuisWeb-acceptatie` en `ThuisWeb-acceptatie-twee`, poorten
18583 en 18584, onder `/mnt/user/appdata/thuisweb-acceptatie-20261021/site1`
en `site2`. Beide gebruiken aparte www/config-mappen. Werk alleen met proefmiddelen.
Gebruik een aantoonbaar vrije poort; neem niet zomaar aan dat 8583 vrij is.

| Controle | Te bewaren bewijs | Resultaat |
| --- | --- | --- |
| Installatie via definitieve template | naam, poort en proefpaden aangepast; overige defaults | geslaagd |
| WebUI-link en landingpagina | http://192.168.1.10:18583/ via Unraid-menu | geslaagd |
| Eigen HTML/PHP en schrijven | PHP 8.3.36, site 1 JSON; site 2 eigen HTML | geslaagd |
| Rewrite, multipart uploads | volledige integratietests lokaal en in CI | daar geslaagd, niet apart op Unraid herhaald |
| PUID/PGID op Unraid-opslag | HTTP-worker 99:100, schrijfproef true | geslaagd |
| Logs en health | beide healthy; interne 8081 geeft ready, niet gepubliceerd | geslaagd |
| Herstart | alle checksums, verborgen bestand, eigenaarschap en rechten gelijk | geslaagd |
| Image-update/vervanging | release 1 -> release 2, checksums en rechten gelijk | geslaagd |
| Veilige rollback | release 2 -> release 1, beide PHP 8.3.36 en scan geslaagd | geslaagd |
| Tweede onafhankelijke website | andere naam/poort/www/config | geslaagd |

Maak een afzonderlijke proefmap, bijvoorbeeld onder
`/mnt/user/appdata/thuisweb-acceptatie-<datum>/`. Controleer eerst dat deze niet
bestaat. Leg de daadwerkelijke paden vast. Gebruik geen productieappdata.

Geteste image-config-digests:

- Release 1, run 39663665343: `sha256:09a098325529cc170884ea86bfcb568ade48d41c2412ca4f3963b28c9980a7d9`.
- Release 2, run 39665014043: `sha256:0abfa01bc15de2b337e61685e2fb636e1e685a6ab17918319c0dd97f6ed24e3c`.

De update/rollback verving daadwerkelijk de container via Unraid, met verschillende
image-digests en behoud van dezelfde proefmounts. De tweede website bleef reageren.
Dit test de vervangingsprocedure; beide releases gebruiken dezelfde PHP-patch.
Checksums, rechtenoverzichten, proefback-up en logs staan in de proefmap.
Na afloop draait site 1 weer op release 2. Het PHP-proefbestand is buiten de
webroot bewaard als `site1-test-index.php`, zodat de WebUI de landingpagina toont.
Site 2 toont de afzonderlijke HTML-proefpagina op poort 18584. Autostart is niet
ingeschakeld voor de proefcontainers.

## Eventuele Kenteken check-migratieproef

Deze optionele vervolgproef is niet uitgevoerd. De alleen-lezen voorcontrole
bevestigt een MySQL/PDO-afhankelijkheid en externe curl-verzoeken; daarvoor zijn
een afzonderlijke testdatabase en afgeschermde externe bijwerkingen nodig.

Pas na geslaagde basistests. Inspecteer eerst de bestaande container op poort
8582: image/digest, mounts, omgevingsvariabelen, netwerk, PHP-versie/extensies,
databaseverbindingswijze en eventuele schrijf-/cron-/SMTP-afhankelijkheden.
Behandel aanwezige geheimen vertrouwelijk; zet ze niet in Git of testrapporten.

Maak een consistente kopie van website en eventuele database naar afzonderlijke
proefmappen en proefdatabase. Een websitekopie die nog naar de productiedatabase
wijst is niet geïsoleerd: wijzig de gekopieerde configuratie vóór het starten.
Voorkom echte e-mails, betalingen en andere externe bijwerkingen in de proef.
Gebruik een vrije poort en geen bestaande proxyroute. Controleer belangrijke
gebruikersfuncties en schrijfhandelingen. Verander de originele container,
poort 8582, oorspronkelijke bestanden en publieke routering niet.

Verwijder na afloop uitsluitend geïdentificeerde proefmiddelen. Een echte
migratie is een afzonderlijke stap na beoordeling van de proefresultaten.
