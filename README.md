# API Smoke Tester

Lite, kommandolinjebasert verktøy for raske smoke-tester av HTTP-API-er.

## Hva verktøyet gjør

- Leser en JSON-konfig med tjenester og endepunkter.
- Sender HTTP-kall (GET/POST/HEAD) med valgfrie headers og JSON-body.
- Verifiserer forventet HTTP-statuskode per endepunkt.
- Måler svartid og sjekker mot en definert maks responstid.
- Skriver kort pass/fail-oversikt til stdout/stderr.
- Kan skrive en strukturert JSON-rapport til fil.
- Returnerer exit-kode som egner seg rett inn i CI/CD.

Exit-koder:

- `0` – alle sjekker besto.
- `1` – minst én sjekk feilet eller en teknisk feil oppstod.

## Eksempel på konfig (config.example.json)

```json
{
  "services": [
    {
      "name": "httpbin",
      "base_url": "https://httpbin.org",
      "timeout_seconds": 5.0,
      "endpoints": [
        {
          "name": "status-200",
          "path": "/status/200",
          "method": "GET",
          "expected_status": 200,
          "max_response_ms": 1500
        },
        {
          "name": "delay-1s",
          "path": "/delay/1",
          "method": "GET",
          "expected_status": 200,
          "max_response_ms": 2500
        }
      ]
    }
  ]
}
```

Felter:

- `name` – logisk navn på tjenesten/endepunktet.
- `base_url` – rot-URL for tjenesten (uten trailing slash).
- `timeout_seconds` – per request-timeout.
- `path` – sti relativt til `base_url`.
- `method` – HTTP-metode (GET/POST/HEAD).
- `expected_status` – forventet HTTP-statuskode.
- `max_response_ms` – maks akseptert svartid i millisekunder.

## Bruk

Installer avhengigheter:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
```

Kjør smoke-test mot `config.example.json` og skriv rapport til `report.json`:

```bash
python api_smoke_tester.py --config config.example.json --output report.json
```

Eksempel på enkel bruk i CI (pseudo):

```bash
python api_smoke_tester.py --config config.ci.json --output smoke_report.json
```

Hvis kommandoen returnerer exit-kode 1 skal jobben feile.

## Ansvarsfraskrivelse

Dette er et uoffisielt open source-verktøy laget på eget initiativ for å gjøre smoke-testing av HTTP-API-er enklere i praksis.
Verktøyet er ikke bestilt eller driftet av noen bestemt virksomhet eller leverandør, og leveres uten noen formell support eller garanti.
