# Accountinrichting en publicatie

GitHub-eigenaar: `marcvandecoevering`; repository: `marcvandecoevering/ThuisWeb`.
Onderstaande lijst beschrijft de procedure; zie testresultaten voor de uitgevoerde stappen. Wachtwoorden en
tweestapsverificatie voer je zelf in; deel geen wachtwoorden of tokens in chat.

1. Maak of kies je GitHub-account en activeer tweestapsverificatie. Bevestig de
   openbare accountnaam en de maintainernaam. Maak de openbare repository
   `ThuisWeb`, standaardbranch `main`, zonder extra gegenereerde README.
2. Vervang `REPLACE_OWNER` in template/profiel door de accountnaam (GHCR-pad
   in kleine letters) en `REPLACE_MAINTAINER` door de gewenste openbare naam.
   Controleer support via GitHub Issues en pas links aan als je een forum gebruikt.
3. Voer `python scripts/validate.py --release` uit. Controleer icoon, beschrijving,
   licentie en alle openbare links. Zoek op https://ca.unraid.net/ naar ThuisWeb;
   laat een conflict eerst beoordelen voordat je de naam wijzigt.
4. Publiceer de broncode en activeer Actions. Zet branchbescherming/review voor
   main en workflowwijzigingen aan. De workflow heeft geen persoonlijke token
   nodig: GitHub levert per job een beperkt GITHUB_TOKEN.
5. Laat de volledige workflow slagen. Controleer `evidence`, het scanrapport,
   SBOM en `publication`. De tags zijn `php8.3` en een unieke
   `build-RUN_ID-ATTEMPT-COMMIT`-tag. Publicatie laadt het geteste archief; er
   wordt niet opnieuw gebouwd. Een stale main-commit of oudere run wordt geweigerd.
6. Open GitHub → profiel → Packages → thuisweb → Package settings → Change
   visibility → Public. Koppel aan de repository indien nodig.
7. Controleer zonder opgeslagen Docker-login, bijvoorbeeld met een tijdelijke
   lege Docker-configmap, `docker --config <lege-map> pull ghcr.io/<owner>/thuisweb:php8.3`.
   Vergelijk de image-ID met `tested-image.json`. Dit is een verplichte controle,
   geen aanname op basis van de package-instelling.
8. Doorloop eerst het afzonderlijke Unraid-testprotocol. Geen wijzigingen aan de
   Kenteken check-container of publiek verkeer.
9. Open https://ca.unraid.net/submit, meld je zelf aan en registreer de repository.
   Laat het portaal de XML scannen. `ca_profile.xml` moet een niet-lege Profile
   bevatten. Verwerk validatiefouten en controleer alle definitieve metadata.
10. Dien in. Bewaar indieningsnummer, datum en moderatorreacties. Na toelating:
    zoek in Unraid Apps, installeer via de echte vermelding en controleer WebUI.
    Pas dan is de app daadwerkelijk opgenomen; indiening alleen is onvoldoende.

## Meldingen en onderhoud

Zet in je persoonlijke GitHub-instellingen onder Notifications de Actions-
meldingen voor mislukte workflows aan (e-mail en/of web). Controleer dit met een
bewust falende test op een tijdelijke branch, niet door de release te beschadigen.
Dit is een accountinstelling en kan pas na aanmelden worden bevestigd.

Controleer wekelijks de laatste geplande run, scannerupdates en PHP-advisories.
GitHub kan geplande workflows in inactieve openbare repositories uitschakelen;
heractiveer ze zo nodig. Verhoog `security-policy.json` bij nieuwe PHP-fixes en
werk de scannerpin bij. Bewaar de resultaten van eerste release, Unraid-acceptatie
en elke relevante regressietest.

Officiële bronnen: [starter](https://github.com/unraid/unraid-community-apps-starter),
[profiel](https://ca.unraid.net/submit/help/repository-info-xml),
[template](https://ca.unraid.net/submit/help/repository-xml),
[indiening](https://ca.unraid.net/submit).
