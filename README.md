# Token Seeder

| Key      | Value                                                                                    |
|----------|------------------------------------------------------------------------------------------|
| Version  | 1.0.0                                                                                    |
| Source   | https://github.com/VNG-Realisatie/token-seeder                                           |
| Keywords | ZGW, tooling                                                                             |
| Related | https://github.com/VNG-Realisatie/token-issuer, https://gitlab.com/commonground/ri/infra/ |


## Introductie

Binnen het Nederlandse gemeentelandschap wordt zaakgericht werken nagestreefd.
Om dit mogelijk te maken is er gegevensuitwisseling nodig. De kerngegevens van
zaken moeten ergens geregistreerd worden en opvraagbaar zijn. Om dit proces te ondersteunen is er een
authenticatie module waarbij tokens gegeneerd worden. Om dit proces ook in een kubernetes cluster te ondersteunen
zonder admin is er gekozen voor een seeder die de juiste data aanmaakt.


## Werking

Bij het opstarten van de container wordt de database gevuld met gegevens die nodig zijn om zowel de `token-issuer` als de apis intern te laten werken
en te laten authenticeren. De token-seeder kan het best gebruikt worden als `init-container` binnen een `helm` deployment. 
Een [voorbeeld](https://gitlab.com/commonground/ri/infra/-/blob/main/helm/ri/charts/zrc/templates/deployment.yaml) kan hier gevonden worden.


## Environmental Variables

Er zijn een aantal variables die te zetten zijn om de werking te bepalen.

| Key                                    | Example                         | Description                                                                   |
|----------------------------------------|---------------------------------|-------------------------------------------------------------------------------|
| ENV                                    | kubernetes                      | Variable die bepaalt welke configuratie uit het INI bestand wordt gelezen     |
| DB_NAME, DB_HOST, DB_USER, DB_PASSWORD | zrc, zrc, postgres, supersecret | Variablen gerelateerd aan je draaiende `postgres` database                    |
| TOKEN_ISSUER_NAME                      | token-issuer-test               | Variable die in elke api gezet gaat worden als clientId                       |
| TOKEN_ISSUER_SECRET                    | supersecretsecret               | Variable voor de validatie van de TOKEN_ISSUER_NAME                           |
 | INTERNAL_API_SECRET                    | anothersupersecret              | Variable voor interne api calls                                               |
 | AUTH_SERVICE                           | http://ac:8000                  | Het adres van de authenticatie API                                            |
 | SERVICE_NAME                           | zrc                             | Naam van de aan te maken clientIdentifier ten behoeve van INTERNAL_API_SECRET |


## Links

* Deze tooling is onderdeel van de [VNG standaard API's voor Zaakgericht werken](https://github.com/VNG-Realisatie/gemma-zaken).
* Rapporteer [issues](https://github.com/VNG-Realisatie/token-seeder/issues) bij vragen, fouten of wensen.

## Licentie


Copyright © VNG Realisatie 2022 - 

Licensed under the EUPL
