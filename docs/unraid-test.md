# Acceptatie op Unraid 192.168.1.10

Status: nog niet uitgevoerd. Werk alleen met nieuwe proefcontainers/mappen.
Gebruik een aantoonbaar vrije poort; neem niet zomaar aan dat 8583 vrij is.

| Controle | Te bewaren bewijs | Resultaat |
| --- | --- | --- |
| Installatie via definitieve template | template, image-digest, instellingen | open |
| WebUI-link en landingpagina | URL en screenshot | open |
| Eigen HTML/PHP, rewrite, uploads | HTTP-resultaten | open |
| PUID/PGID op Unraid-opslag | eigenaar/rechten en schrijfproef | open |
| Logs en health | containerlogs/inspect | open |
| Herstart | bestandschecksums voor/na | open |
| Image-update/vervanging | checksums en image-digests | open |
| Veilige rollback | eerdere veilige digest en hersteltest | open |
| Tweede onafhankelijke website | andere naam/poort/www/config | open |

Maak een afzonderlijke proefmap, bijvoorbeeld onder
`/mnt/user/appdata/thuisweb-acceptatie-<datum>/`. Controleer eerst dat deze niet
bestaat. Leg de daadwerkelijke paden vast. Gebruik geen productieappdata.

## Eventuele Kenteken check-migratieproef

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
