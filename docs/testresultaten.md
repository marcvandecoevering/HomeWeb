# Testresultaten

## Vernieuwd beeldmerk en live startpaginastatus - 21 oktober 2026

Een nieuw groen W-beeldmerk wordt gebruikt voor de Unraid-app, startpagina en favicon.
De startpagina haalt elke 30 seconden de Apache/PHP/OPcache-versies, werkelijke
OPcache-status en bronbuild op. De lokale container meldt Apache 2.4.68 en PHP/OPcache
8.3.36. Alle 14 integratietestgroepen zijn geslaagd, inclusief versiecontrole en
het blokkeren van het statusadres na vervanging van de startpagina of plaatsing
van een eigen index.php. Het statusantwoord bevat uitsluitend de vijf bedoelde velden.

Desktop- en smalle weergave zijn visueel gecontroleerd. Ook uitgeschakelde OPcache
(amber, Uitgeschakeld) en een ontbrekend statusantwoord (rood, Niet bereikbaar)
zijn in de browser beproefd. Versies worden bij een fout gewist in plaats van als
actuele gegevens te blijven staan. Bestaande websitebestanden worden niet bijgewerkt.

## Lokale acceptatie - 21 oktober 2026

De image is op Docker Desktop met Linux/amd64 gebouwd. Alle 13 groepen van de
integratietest zijn geslaagd. Machineleesbaar bewijs met exacte digests en
testnamen staat in [local-validation.json](local-validation.json).

Getest: lege en bestaande/verborgen websitemappen; HTML/PHP/indexvolgorde;
rewrite; PHP-foutlogging zonder zichtbare fouten; sessies; uploads van 32 MiB
en weigering van te grote bestanden/POSTs; alle vereiste extensies en GD-features;
MariaDB/PostgreSQL/SQLite; PUID/PGID en schrijfbare uploads; herstart/vervanging
zonder gegevens- of eigenaarschapswijziging; twee onafhankelijke websites;
interne healthcheck met defecte gebruikerswebsite en geen externe toegang;
ongeldige instellingen, ontoegankelijke en read-only mappen; php.ini-overrides
en syntaxfouten; geen terugkerende landingpagina na verwijdering.

Een eerste run ontdekte dat Apache bij een onbekend numeriek UID de gewenste
rechtenverlaging niet uitvoerde. De startprocedure maakt nu indien nodig een
passwd-/groepsvermelding aan, zonder bestaande websitebestanden aan te passen.
De herhaalde HTTP-tests bevestigen 99:100 en een afwijkend 1234:1234.

Python/shell/XML-controles en Actionlint slagen. De landingpagina is visueel
gecontroleerd op desktop en op 390px breedte, zonder horizontale overloop.

## Scan

Trivy 0.76.1 heeft de uiteindelijke image gescand met een vers opgehaalde database.
Er zijn **0 HIGH/CRITICAL-bevindingen met een beschikbare reparatie** volgens deze
scan. Er blijven pakketbevindingen zonder aangeboden reparatie:

| Ernst | Pakketbevindingen |
| --- | ---: |
| Critical | 7 |
| High | 319 |
| Medium | 1381 |
| Low | 616 |
| Unknown | 4 |

Dit zijn pakketbevindingen, geen aantallen unieke CVEs of bewezen bereikbare
aanvalspaden. De aantallen zijn niet weggefilterd. De afgesproken publicatiegrens
blokkeert repareerbare hoge/kritieke bevindingen; slagen is geen veiligheidsgarantie.
PHP 8.3.36 en de verplichte extensies zijn onafhankelijk van de scanner gecontroleerd.
Scanrapport en CycloneDX-SBOM staan lokaal in artifacts; CI bewaart zijn eigen
resultaten als workflowartifacts.

De twee openbare CI-releases rapporteren elk 7 Critical, 314 High, 1389 Medium,
613 Low en 4 Unknown pakketbevindingen, met eveneens nul repareerbare
HIGH/CRITICAL-bevindingen. De tabel hierboven betreft de eerdere lokale build;
raadpleeg voor iedere release het eigen scanrapport en SBOM.

## Eerste openbare release en Unraid-basistests

[GitHub Actions-run 39663665343](https://github.com/marcvandecoevering/ThuisWeb/actions/runs/39663665343)
heeft alle 13 integratietestgroepen en de scangrens doorlopen en exact de geteste
image gepubliceerd. Het openbare GHCR-package is zonder Docker-login opgehaald.

- Broncommit: `6bedcfc71a0021895d636afe39ae707074f9e631`.
- Unieke tag: `build-39663665343-1-6bedcfc71a00`.
- Registry-digest: `sha256:df99023e89a90a1ef918b5468a554328c64a897c4c8d45d59995dead6f7e6659`.
- Config-digest: `sha256:09a098325529cc170884ea86bfcb568ade48d41c2412ca4f3963b28c9980a7d9`.
- PHP: 8.3.36; basisdigest gelijk aan de lokale acceptatie.

De Unraid 7.3.3-proefinstallatie via de XML-template is geslaagd met eigen
appdata-mappen en poorten 18583/18584. De WebUI-link toont de landingpagina;
de eerste container is healthy. Een eigen PHP-website meldt PHP 8.3.36,
worker 99:100 en succesvol schrijven naar de uploadmap. Herstart behoudt
alle bestandschecksums en eigenaarschap, inclusief een verborgen bestand.
Een tweede container toont onafhankelijk eigen HTML. Productiemappen en
bestaande containers zijn niet gewijzigd.

De officiële Community Applications-scan vindt een geldige Docker-app zonder
templatewaarschuwingen en bevestigt dat de image downloadbaar is. Die scan is
op zichzelf geen indiening of opname in de catalogus.

## Update en rollback op Unraid

Ook [release 2](https://github.com/marcvandecoevering/ThuisWeb/actions/runs/39665014043)
heeft alle controles en publicatie doorlopen. De proefcontainer is via de Unraid-UI
van release 1 naar release 2 vervangen en weer naar release 1 teruggezet. In beide
richtingen bleven alle bestandschecksums, eigenaarschap en rechten gelijk; de PHP-
schrijfproef en tweede website bleven werken. Beide releases gebruiken PHP 8.3.36
en hebben geen repareerbare hoge/kritieke scanbevindingen. Dit is geen garantie dat
terugrollen naar een willekeurige oudere release veilig is.
Zie [Unraid-testdetails](unraid-test.md).

## Community Applications

Ingediend op 21 oktober 2026; het portaal bevestigt om 21:55:10 (Europe/Amsterdam)
de status **auto_approved**, met reviewnotitie "Auto-approved for Docker apps
(non-duplicated)." Repositorynaam: `marccoef's Repository`.
[Indieningsstatus](https://ca.unraid.net/submissions/repository?url=https://github.com/marcvandecoevering/ThuisWeb)
(aanmelding vereist).

Het portaal meldt dat de app na de volgende Community Applications-catalogusbuild
verschijnt. Goedkeuring is dus nog niet hetzelfde als daadwerkelijke vindbaarheid.
Bij de aansluitende controle meldt de echte Unraid Apps-tab nog "No Matching
Applications Found"; het portaal toont 0 zichtbare apps. Installatie vanuit de
catalogus kan daarom nog niet worden beproefd. De XML-installatie is wel getest.

## Nog afzonderlijk te verifiëren

- Daadwerkelijke vindbaarheid na de volgende catalogusbuild en installatie vanuit die vermelding.

Bekende beperkingen: uitsluitend linux/amd64; sessies niet duurzaam bij
containervervanging; geen database/TLS/beheerpaneel; beheerders-php.ini kan defaults
overschrijven. Lokaal succes vervangt de Unraid-acceptatie niet.
