# Testresultaten

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

De officiele Community Applications-scan vindt een geldige Docker-app zonder
templatewaarschuwingen en bevestigt dat de image downloadbaar is. Dit is nog
geen indiening of opname in de catalogus.

## Nog afzonderlijk te verifiëren

- Update en veilige rollback op Unraid tussen twee geteste releases.
- Community Applications-indiening, toelating en daadwerkelijke vindbaarheid.

Bekende beperkingen: uitsluitend linux/amd64; sessies niet duurzaam bij
containervervanging; geen database/TLS/beheerpaneel; beheerders-php.ini kan defaults
overschrijven. Lokaal succes vervangt de Unraid-acceptatie niet.
