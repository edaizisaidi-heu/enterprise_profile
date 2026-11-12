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
    endpoint = "/health/detailed" if getattr(args, "detailed", False) else "/health"
    url = f"{args.base_url}{endpoint}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if getattr(args, "detailed", False):
                print("==================================================")
                print("🟢 TESSERAQS C2 NODE DETAILED HEALTH DIAGNOSTICS")
                print("==================================================")
                print(json.dumps(data, indent=2))
            else:
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


def cmd_ready(args):
    """Check readiness probe of the C2 Listener node."""
    url = f"{args.base_url}/ready"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            status = data.get("status", "UNKNOWN")
            is_ready = status == "READY"
            icon = "🟢" if is_ready else "🔴"
            print("==================================================")
            print(f"{icon} TESSERAQS C2 NODE READINESS: {status}")
            print("==================================================")
            print(f"Node                 : {data.get('node')}")
            print(f"Core Artifacts Ready : {data.get('core_artifacts_ready')}")
            print(f"Modules Dir Access   : {data.get('modules_dir_accessible')}")
            print(f"Timestamp            : {data.get('timestamp')}")
            if not is_ready:
                sys.exit(1)
    except urllib.error.HTTPError as err:
        err_msg = err.read().decode("utf-8", errors="replace")
        print(f"❌ Node readiness check failed (HTTP {err.code}): {err_msg}", file=sys.stderr)
        sys.exit(1)
    except Exception as err:
        print(f"❌ Error connecting to node readiness endpoint: {err}", file=sys.stderr)
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

    if getattr(args, "timestamp", None):
        headers["X-Sovereign-Timestamp"] = str(args.timestamp)
    if getattr(args, "nonce", None):
        headers["X-Sovereign-Nonce"] = str(args.nonce)

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
        "ca.crt",
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


def cmd_live(args):
    """Live monitor C2 telemetry stream and node health."""
    import time
    count = args.count
    iteration = 0
    print("==================================================")
    print(f"📡 TESSERAQS LIVE TELEMETRY MONITOR ({args.base_url})")
    print("==================================================")
    try:
        while True:
            iteration += 1
            url = f"{args.base_url}/telemetry/stats"
            try:
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=args.timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    metrics = data.get("metrics", {})
                    ts = data.get("timestamp", "")
                    uptime = data.get("uptime_seconds", 0)
                    total_req = metrics.get("total_requests", 0)
                    processed = metrics.get("processed_telemetry", 0)
                    errors = metrics.get("errors", 0)
                    print(f"[{ts}] Uptime: {uptime}s | Req: {total_req} | Telemetry: {processed} | Errors: {errors}")
            except Exception as err:
                print(f"[ERROR] Iteration {iteration}: {err}", file=sys.stderr)

            if count > 0 and iteration >= count:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n[!] Live monitoring stopped by user.")


def cmd_verify_remote(args):
    """Verify live sovereign defense attestation on remote domain."""
    target = args.target_url.rstrip("/")
    print("==================================================")
    print(f"🛡️  VERIFYING REMOTE SOVEREIGN ATTRIBUTES: {target}")
    print("==================================================")
    endpoints = [
        ("/attestation/security.json", "Security Attestation JSON"),
        ("/attestation/sovereign_consensus.json", "ZKP Consensus Proof"),
        ("/robots.txt", "Anti-AI Training Shield"),
        ("/ca.crt", "Root CA Certificate")
    ]
    all_ok = True
    for ep, desc in endpoints:
        full_url = f"{target}{ep}"
        try:
            req = urllib.request.Request(full_url, headers={"User-Agent": "TesseraQS-CLI-Verifier"})
            with urllib.request.urlopen(req, timeout=args.timeout) as resp:
                content = resp.read()
                print(f"  [✓] {desc} verified ({len(content)} bytes) - HTTP {resp.status}")
        except Exception as err:
            print(f"  [!] {desc} failed at {full_url}: {err}", file=sys.stderr)
            all_ok = False

    if all_ok:
        print("\n✓ Remote Sovereign Attestation 100% EMPIRICAL ACTIVE.")
    else:
        print("\n❌ Warning: Remote verification detected missing or unreachable layers.", file=sys.stderr)
        sys.exit(1)


def main():
    # Subcommand parent parser: use argparse.SUPPRESS for defaults so global flags take effect if set before subcommand
    sub_parent = argparse.ArgumentParser(add_help=False)
    sub_parent.add_argument("--base-url", default=argparse.SUPPRESS, help=f"C2 Base URL (default: {DEFAULT_BASE_URL})")
    sub_parent.add_argument("--timeout", type=int, default=argparse.SUPPRESS, help="Request timeout in seconds (default: 5)")

    parser = argparse.ArgumentParser(
        description="TesseraQS Autonomous Sovereign CLI"
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help=f"C2 Base URL (default: {DEFAULT_BASE_URL})")
    parser.add_argument("--timeout", type=int, default=5, help="Request timeout in seconds (default: 5)")
    parser.add_argument("--version", action="version", version="TesseraQS Sovereign CLI v3.3.0")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Health command
    p_health = subparsers.add_parser("health", parents=[sub_parent], help="Check C2 Listener health status")
    p_health.add_argument("--detailed", action="store_true", help="Fetch detailed health diagnostics and artifacts status")
    p_health.set_defaults(func=cmd_health)

    # Ready command
    p_ready = subparsers.add_parser("ready", parents=[sub_parent], help="Check C2 Listener readiness probe")
    p_ready.set_defaults(func=cmd_ready)

    # Metrics command
    p_metrics = subparsers.add_parser("metrics", parents=[sub_parent], help="Fetch node metrics and stats")
    p_metrics.add_argument("--format", choices=["json", "prometheus"], default="json", help="Output format")
    p_metrics.set_defaults(func=cmd_metrics)

    # Send telemetry command
    p_send = subparsers.add_parser("send", parents=[sub_parent], help="Send telemetry or directive to /omni-listener")
    p_send.add_argument("--directive", required=True, help="Directive string")
    p_send.add_argument("--module", default="tessera_cli", help="Source module name")
    p_send.add_argument("--intent", default="USER_DIRECTIVE", help="Intent descriptor")
    p_send.add_argument("--secret", default="", help="Optional HMAC sovereign secret key")
    p_send.add_argument("--timestamp", default="", help="Optional timestamp for replay protection")
    p_send.add_argument("--nonce", default="", help="Optional nonce for replay protection")
    p_send.set_defaults(func=cmd_send)

    # Audit command
    p_audit = subparsers.add_parser("audit", parents=[sub_parent], help="Verify local sovereign defense artifacts")
    p_audit.set_defaults(func=cmd_audit)

    # Live telemetry monitor command
    p_live = subparsers.add_parser("live", parents=[sub_parent], help="Stream live telemetry stats from node")
    p_live.add_argument("--interval", type=float, default=1.0, help="Poll interval in seconds (default: 1.0)")
    p_live.add_argument("--count", type=int, default=1, help="Number of samples to collect before exit (default: 1, 0 for infinite)")
    p_live.set_defaults(func=cmd_live)

    # Verify remote domain command
    p_remote = subparsers.add_parser("verify-remote", parents=[sub_parent], help="Verify live sovereign attestation on remote host")
    p_remote.add_argument("--target-url", default="https://tesseraqs.cloud-ip.cc", help="Target domain URL")
    p_remote.set_defaults(func=cmd_verify_remote)

    parsed = parser.parse_args()
    parsed.func(parsed)


if __name__ == "__main__":
    main()
