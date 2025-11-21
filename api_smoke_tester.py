import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


@dataclass
class EndpointConfig:
    name: str
    path: str
    method: str
    expected_status: int
    max_response_ms: Optional[float]


@dataclass
class ServiceConfig:
    name: str
    base_url: str
    timeout_seconds: float
    endpoints: List[EndpointConfig]


def load_config(path: Path) -> List[ServiceConfig]:
    if not path.is_file():
        raise FileNotFoundError(f"Fant ikke konfigfil: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    services_raw = data.get("services")
    if not isinstance(services_raw, list) or not services_raw:
        raise ValueError("Config må inneholde en ikke-tom 'services'-liste")

    services: List[ServiceConfig] = []
    for s in services_raw:
        name = s.get("name")
        base_url = s.get("base_url")
        timeout = s.get("timeout_seconds", 5.0)
        endpoints_raw = s.get("endpoints") or []
        if not name or not base_url or not endpoints_raw:
            raise ValueError(f"Ugyldig service-definisjon: {s}")
        endpoints: List[EndpointConfig] = []
        for e in endpoints_raw:
            ename = e.get("name")
            path_val = e.get("path")
            method = str(e.get("method", "GET")).upper()
            expected_status = int(e.get("expected_status", 200))
            max_ms = e.get("max_response_ms")
            if ename is None or path_val is None:
                raise ValueError(f"Ugyldig endpoint-definisjon: {e}")
            endpoints.append(
                EndpointConfig(
                    name=str(ename),
                    path=str(path_val),
                    method=method,
                    expected_status=expected_status,
                    max_response_ms=float(max_ms) if max_ms is not None else None,
                )
            )
        services.append(
            ServiceConfig(
                name=str(name),
                base_url=str(base_url).rstrip("/"),
                timeout_seconds=float(timeout),
                endpoints=endpoints,
            )
        )
    return services


def run_tests(services: List[ServiceConfig]) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    total = 0
    passed = 0
    failed = 0

    for svc in services:
        for ep in svc.endpoints:
            total += 1
            url = svc.base_url + ep.path
            start = time.perf_counter()
            try:
                if ep.method == "GET":
                    resp = requests.get(url, timeout=svc.timeout_seconds)
                elif ep.method == "POST":
                    resp = requests.post(url, json=None, timeout=svc.timeout_seconds)
                elif ep.method == "HEAD":
                    resp = requests.head(url, timeout=svc.timeout_seconds)
                else:
                    raise ValueError(f"Ustøttet metode: {ep.method}")
                elapsed_ms = (time.perf_counter() - start) * 1000.0
                ok_status = resp.status_code == ep.expected_status
                ok_time = True
                if ep.max_response_ms is not None:
                    ok_time = elapsed_ms <= ep.max_response_ms
                ok = ok_status and ok_time
                if ok:
                    passed += 1
                else:
                    failed += 1
                results.append(
                    {
                        "service": svc.name,
                        "endpoint": ep.name,
                        "url": url,
                        "method": ep.method,
                        "status_code": resp.status_code,
                        "expected_status": ep.expected_status,
                        "response_ms": elapsed_ms,
                        "max_response_ms": ep.max_response_ms,
                        "ok_status": ok_status,
                        "ok_time": ok_time,
                        "ok": ok,
                    }
                )
                status_flag = "OK" if ok else "FAIL"
                print(
                    f"[{status_flag}] {svc.name}/{ep.name} "
                    f"{ep.method} {url} -> {resp.status_code} "
                    f"({elapsed_ms:.1f} ms)"
                )
            except Exception as e:
                failed += 1
                elapsed_ms = (time.perf_counter() - start) * 1000.0
                results.append(
                    {
                        "service": svc.name,
                        "endpoint": ep.name,
                        "url": url,
                        "method": ep.method,
                        "status_code": None,
                        "expected_status": ep.expected_status,
                        "response_ms": elapsed_ms,
                        "max_response_ms": ep.max_response_ms,
                        "ok_status": False,
                        "ok_time": False,
                        "ok": False,
                        "error": str(e),
                    }
                )
                print(
                    f"[ERROR] {svc.name}/{ep.name} {ep.method} {url} "
                    f"feilet etter {elapsed_ms:.1f} ms: {e}"
                )

    summary = {"total": total, "passed": passed, "failed": failed}
    return {"summary": summary, "results": results}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Enkel API smoke-tester basert på JSON-konfig."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Sti til config-fil (JSON) med services/endpoints.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Sti til JSON-rapport som skal skrives.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config_path = Path(args.config)
    output_path = Path(args.output)

    services = load_config(config_path)
    report = run_tests(services)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    summary = report["summary"]
    print("")
    print("Oppsummert:")
    print(f"  total:  {summary['total']}")
    print(f"  passed: {summary['passed']}")
    print(f"  failed: {summary['failed']}")

    if summary["failed"] > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
