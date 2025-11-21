# API Smoke Tester

Small, production-ready CLI tool for running smoke tests against HTTP APIs.

## What it does

- Reads a JSON config describing services and endpoints.
- Sends HTTP requests (GET/POST/HEAD) with optional headers and JSON body.
- Validates expected HTTP status codes.
- Checks response time against a configurable max threshold.
- Prints a concise pass/fail summary to stdout/stderr.
- Optionally writes a structured JSON report file.

Exit code is:
- `0` if all checks pass.
- `1` if any check fails or config/runtime errors occur.

## Quick start

Install dependencies:

```bash
pip install -r requirements.txt

## Ansvarsfraskrivelse

Dette er et uoffisielt open source-verktøy laget på eget initiativ for å gjøre smoke-testing av HTTP-API-er enklere i praksis. Verktøyet er ikke bestilt eller driftet av noen bestemt virksomhet eller leverandør, og leveres uten noen formell support eller garanti.