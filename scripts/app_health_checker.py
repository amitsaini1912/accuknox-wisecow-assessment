#!/usr/bin/env python3
"""Application health checker: reports UP/DOWN from HTTP status codes.
Usage: python3 app_health_checker.py https://example.com [--timeout 5] [--retries 3]
Exit code 0 = UP, 1 = DOWN."""
import argparse, sys, time
import requests

def check(url, timeout=5, retries=3, backoff=1.0, verify=True):
    last = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, timeout=timeout, verify=verify)
            elapsed = r.elapsed.total_seconds() * 1000
            if 200 <= r.status_code < 400:
                return "UP", f"HTTP {r.status_code} in {elapsed:.0f} ms"
            last = f"HTTP {r.status_code}"
            if r.status_code < 500:  # 4xx won't fix itself on retry
                break
        except requests.exceptions.Timeout:
            last = f"timeout after {timeout}s"
        except requests.exceptions.SSLError as e:
            last = f"TLS error: {e.__class__.__name__}"
            break
        except requests.exceptions.ConnectionError:
            last = "connection refused / unreachable"
        time.sleep(backoff * attempt)
    return "DOWN", last

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--timeout", type=float, default=5)
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--insecure", action="store_true", help="skip TLS verify (self-signed)")
    a = ap.parse_args()
    status, detail = check(a.url, a.timeout, a.retries, verify=not a.insecure)
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {a.url} is {status} ({detail})")
    sys.exit(0 if status == "UP" else 1)

if __name__ == "__main__":
    main()
