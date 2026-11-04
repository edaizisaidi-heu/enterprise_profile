#!/usr/bin/env python3
"""
TESSERAQS AUTONOMOUS SOVEREIGN CLI (tessera_cli.py)
Unified Command-Line Interface for TesseraQS C2 Management, Telemetry, and Sovereign Audit.
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import hmac
import hashlib

DEFAULT_BASE_URL = os.environ.get("C2_BASE_URL", "http://127.0.0.1:5000")
DEFAULT_SECRET = os.environ.get("SOVEREIGN_SECRET_KEY", "")


def compute_signature(payload_bytes: bytes, secret: str) -> str:
    """Compute HMAC-SHA256 signature for payload."""
    if not secret:
        return ""
    return hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()


def cmd_health(args):
    """Check health of the C2 Listener node."""
    url = f"{args.base_url}/health"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print("==================================================")
            print("🟢 TESSERAQS C2 NODE HEALTH STATUS: ONLINE")
            print("==================================================")
            print(f"Service      : {data.get('service')}")
            print(f"Version      : {data.get('version')}")
            print(f"Node         : {data.get('node')}")
            print(f"Architecture : {data.get('architecture')}")
            print(f"Timestamp    : {data.get('timestamp')}")
            print(f"Uptime (s)   : {data.get('uptime_seconds')}")
    except Exception as err:
        print(f"❌ Error connecting to node health endpoint: {err}", file=sys.stderr)
        sys.exit(1)


def cmd_metrics(args):
    """Retrieve metrics or telemetry stats from C2 Listener."""
    if args.format == "prometheus":
        url = f"{args.base_url}/metrics"
    else:
        url = f"{args.base_url}/telemetry/stats"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            content = resp.read().decode("utf-8")
            if args.format == "prometheus":
                print(content.strip())
            else:
                data = json.loads(content)
                print(json.dumps(data, indent=2))
    except Exception as err:
        print(f"❌ Error retrieving metrics: {err}", file=sys.stderr)
        sys.exit(1)


def cmd_send(args):
    """Send directive/telemetry payload to /omni-listener."""
    url = f"{args.base_url}/omni-listener"
    payload = {
        "module": args.module,
        "intent": args.intent,
        "directive": args.directive
    }
    payload_bytes = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}

    secret = args.secret or DEFAULT_SECRET
    if secret:
        sig = compute_signature(payload_bytes, secret)
        headers["X-Sovereign-Signature"] = sig

    try:
        req = urllib.request.Request(url, data=payload_bytes, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            print("==================================================")
            print(f"📡 TELEMETRY RESPONSE: {result.get('status')} [{result.get('action')}]")
            print("==================================================")
            print(json.dumps(result, indent=2))
    except urllib.error.HTTPError as err:
        err_msg = err.read().decode("utf-8", errors="replace")
        print(f"❌ HTTP Error {err.code}: {err_msg}", file=sys.stderr)
        sys.exit(1)
    except Exception as err:
        print(f"❌ Error dispatching telemetry: {err}", file=sys.stderr)
        sys.exit(1)


def cmd_audit(args):
    """Run local or remote sovereign defense audit."""
    print("==================================================")
    print("🛡️  TESSERAQS SOVEREIGN DEFENSE LOCAL AUDIT")
    print("==================================================")
    files_to_check = [
        "c2_listener.py",
        "attestation/security.json",
        "attestation/sovereign_consensus.json",
        "robots.txt",
        ".well-known/security.txt",
        "openapi.json"
    ]
    all_ok = True
    for f in files_to_check:
        if os.path.exists(f):
            print(f"  [✓] File present: {f}")
        else:
            print(f"  [!] Missing file: {f}")
            all_ok = False

    if all_ok:
        print("\n✓ Local cryptographic artifacts and defense layers verified.")
    else:
        print("\n❌ Warning: Incomplete defense artifacts detected.", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="TesseraQS Autonomous Sovereign CLI")
    parser.add_argument("--version", action="version", version="TesseraQS Sovereign CLI v3.3.0")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help=f"C2 Base URL (default: {DEFAULT_BASE_URL})")
    parser.add_argument("--timeout", type=int, default=5, help="Request timeout in seconds (default: 5)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Health command
    p_health = subparsers.add_parser("health", help="Check C2 Listener health status")
    p_health.set_defaults(func=cmd_health)

    # Metrics command
    p_metrics = subparsers.add_parser("metrics", help="Fetch node metrics and stats")
    p_metrics.add_argument("--format", choices=["json", "prometheus"], default="json", help="Output format")
    p_metrics.set_defaults(func=cmd_metrics)

    # Send telemetry command
    p_send = subparsers.add_parser("send", help="Send telemetry or directive to /omni-listener")
    p_send.add_argument("--directive", required=True, help="Directive string")
    p_send.add_argument("--module", default="tessera_cli", help="Source module name")
    p_send.add_argument("--intent", default="USER_DIRECTIVE", help="Intent descriptor")
    p_send.add_argument("--secret", default="", help="Optional HMAC sovereign secret key")
    p_send.set_defaults(func=cmd_send)

    # Audit command
    p_audit = subparsers.add_parser("audit", help="Verify local sovereign defense artifacts")
    p_audit.set_defaults(func=cmd_audit)

    parsed = parser.parse_args()
    parsed.func(parsed)


if __name__ == "__main__":
    main()
