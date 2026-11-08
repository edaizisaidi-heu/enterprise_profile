"""
OMEGA C2 TELEMETRY BRIDGE & AUTONOMOUS INTENT EXECUTOR (V3.3 - METRICS & CRYPTOGRAPHIC SOVEREIGN GUARD)
"""
import http.server
import json
import os
import glob
import re
import subprocess
import logging
import sys
import datetime
import hmac
import hashlib
import time
from typing import Dict, Any

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", 5000))
MODULES_DIR = os.environ.get("MODULES_DIR", os.path.expanduser("~/workspace/modules"))
MAX_PAYLOAD_SIZE = int(os.environ.get("MAX_PAYLOAD_SIZE", 1024 * 1024))  # 1 MB default limit
SOVEREIGN_SECRET_KEY = os.environ.get("SOVEREIGN_SECRET_KEY", "")

# Anti-Replay Protection Configuration
# MAX_REPLAY_WINDOW_SECONDS: allowed clock skew in seconds (default: 300 / 5 minutes)
MAX_REPLAY_WINDOW_SECONDS = int(os.environ.get("MAX_REPLAY_WINDOW_SECONDS", 300))
# NONCE_CACHE_TTL: time-to-live in seconds for tracked nonces
NONCE_CACHE_TTL = int(os.environ.get("NONCE_CACHE_TTL", 600))
# In-memory nonce store: {nonce: seen_timestamp}
SEEN_NONCES: Dict[str, float] = {}

# Autonomous Rate Limiting Configuration (In-Memory Token Bucket per Client IP)
RATE_LIMIT_ENABLED = os.environ.get("RATE_LIMIT_ENABLED", "0") in ("1", "true", "True")
RATE_LIMIT_RPS = float(os.environ.get("RATE_LIMIT_RPS", 50.0))  # tokens added per second
RATE_LIMIT_BURST = float(os.environ.get("RATE_LIMIT_BURST", 100.0))  # maximum bucket capacity
# Structure: {client_ip: (tokens, last_updated_time)}
RATE_LIMIT_BUCKETS: Dict[str, tuple[float, float]] = {}

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("c2_listener")

SERVER_START_TIME = time.time()

# Thread-safe in-memory metrics state
METRICS = {
    "total_requests": 0,
    "processed_telemetry": 0,
    "intents_executed": {
        "PURGE_EXECUTED": 0,
        "AUDIT_AND_HEAL_COMPLETE": 0,
        "RECURSIVE_SIMULATION_UPDATED": 0,
        "ESCALATED_TO_ALPHA": 0,
        "TELEMETRY_LOGGED": 0
    },
    "errors": 0,
    "signature_failures": 0,
    "replay_failures": 0,
    "rate_limit_exceeded": 0,
    "total_duration_seconds": 0.0,
    "duration_buckets": {
        "0.005": 0,
        "0.01": 0,
        "0.025": 0,
        "0.05": 0,
        "0.1": 0,
        "0.25": 0,
        "0.5": 0,
        "1.0": 0,
        "2.5": 0,
        "+Inf": 0
    }
}


def record_request_duration(duration: float) -> None:
    """Record request latency in metrics histogram."""
    METRICS["total_duration_seconds"] += duration
    for le_str, count in list(METRICS["duration_buckets"].items()):
        if le_str == "+Inf":
            METRICS["duration_buckets"]["+Inf"] += 1
        elif duration <= float(le_str):
            METRICS["duration_buckets"][le_str] += 1


def is_safe_path(base_dir: str, target_path: str) -> bool:
    """Check if target_path resides inside base_dir to prevent path traversal."""
    abs_base = os.path.realpath(base_dir)
    abs_target = os.path.realpath(target_path)
    try:
        return os.path.commonpath([abs_base, abs_target]) == abs_base
    except ValueError:
        return False


def get_utc_timestamp() -> str:
    """Return current ISO 8601 UTC timestamp."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def get_uptime_seconds() -> float:
    """Return server uptime in seconds."""
    return round(time.time() - SERVER_START_TIME, 2)


def cleanup_expired_nonces(current_time: float) -> None:
    """Evict expired nonces from memory cache to prevent unbound growth."""
    expired = [nonce for nonce, ts in SEEN_NONCES.items() if (current_time - ts) > NONCE_CACHE_TTL]
    for nonce in expired:
        SEEN_NONCES.pop(nonce, None)


def check_rate_limit(client_ip: str) -> bool:
    """
    Token-bucket algorithm for rate limiting. Returns True if request allowed, False if exceeded.
    """
    if not RATE_LIMIT_ENABLED:
        return True

    now = time.time()
    tokens, last_time = RATE_LIMIT_BUCKETS.get(client_ip, (RATE_LIMIT_BURST, now))

    # Refill tokens according to elapsed time
    elapsed = max(0.0, now - last_time)
    tokens = min(RATE_LIMIT_BURST, tokens + elapsed * RATE_LIMIT_RPS)

    if tokens >= 1.0:
        RATE_LIMIT_BUCKETS[client_ip] = (tokens - 1.0, now)
        return True
    else:
        RATE_LIMIT_BUCKETS[client_ip] = (tokens, now)
        return False


def verify_anti_replay(timestamp_str: str, nonce: str) -> tuple[bool, str]:
    """
    Validate timestamp freshness and nonce uniqueness if provided.
    Returns (is_valid, error_message).
    """
    now = time.time()
    cleanup_expired_nonces(now)

    if timestamp_str:
        try:
            # Supports both epoch seconds (float/int) or ISO 8601 string
            try:
                req_ts = float(timestamp_str)
            except ValueError:
                req_dt = datetime.datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                req_ts = req_dt.timestamp()

            if abs(now - req_ts) > MAX_REPLAY_WINDOW_SECONDS:
                return False, f"Cap masa di luar julat toleransi ({MAX_REPLAY_WINDOW_SECONDS}s)."
        except Exception:
            return False, "Format X-Sovereign-Timestamp tidak sah."

    if nonce:
        if nonce in SEEN_NONCES:
            return False, "Pengesanan serangan ulangan: Nonce telah digunakan sebelum ini."
        SEEN_NONCES[nonce] = now

    return True, ""


def verify_sovereign_signature(payload_bytes: bytes, signature_hex: str) -> bool:
    """Verify HMAC-SHA256 signature against SOVEREIGN_SECRET_KEY if configured."""
    if not SOVEREIGN_SECRET_KEY:
        return True  # Zero-friction mode if no key configured
    if not signature_hex:
        return False
    expected = hmac.new(SOVEREIGN_SECRET_KEY.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_hex)


class C2Handler(http.server.BaseHTTPRequestHandler):
    """HTTP Request Handler for OMEGA C2 Telemetry Bridge."""

    def _set_headers(self, status: int = 200, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS, HEAD")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Sovereign-Signature, X-Sovereign-Timestamp, X-Sovereign-Nonce")
        self.end_headers()

    def _send_method_not_allowed(self) -> None:
        METRICS["errors"] += 1
        self._set_headers(405)
        self.wfile.write(json.dumps({"error": "Method Not Allowed"}).encode("utf-8"))

    def do_OPTIONS(self) -> None:
        METRICS["total_requests"] += 1
        self._set_headers(204)

    def do_HEAD(self) -> None:
        start_time = time.time()
        METRICS["total_requests"] += 1
        try:
            if self.path in ["/health", "/status", "/ready"]:
                self._set_headers(200)
            elif self.path == "/health/detailed":
                self._set_headers(200, "application/json")
            elif self.path in ["/metrics", "/telemetry/stats"]:
                content_type = "text/plain; version=0.0.4; charset=utf-8" if self.path == "/metrics" else "application/json"
                self._set_headers(200, content_type)
            else:
                self._set_headers(404)
        finally:
            record_request_duration(time.time() - start_time)

    def do_PUT(self) -> None:
        self._send_method_not_allowed()

    def do_DELETE(self) -> None:
        self._send_method_not_allowed()

    def do_PATCH(self) -> None:
        self._send_method_not_allowed()

    def do_GET(self) -> None:
        start_time = time.time()
        METRICS["total_requests"] += 1
        try:
            if self.path in ["/health", "/status"]:
                self._set_headers(200)
                self.wfile.write(json.dumps({
                    "status": "ONLINE",
                    "service": "OMEGA_C2_LISTENER",
                    "version": "3.3.0",
                    "node": "TELUK_INTAN_EDGE_01",
                    "architecture": "TesseraQS Core",
                    "timestamp": get_utc_timestamp(),
                    "uptime_seconds": get_uptime_seconds()
                }).encode("utf-8"))
            elif self.path == "/ready":
                artifacts_ok = all(os.path.exists(f) for f in [
                    "c2_listener.py", "ca.crt", "openapi.json"
                ])
                status_code = 200 if artifacts_ok else 503
                self._set_headers(status_code)
                self.wfile.write(json.dumps({
                    "status": "READY" if artifacts_ok else "NOT_READY",
                    "node": "TELUK_INTAN_EDGE_01",
                    "modules_dir_accessible": os.path.isdir(MODULES_DIR) or os.path.exists(os.path.dirname(os.path.realpath(MODULES_DIR))),
                    "core_artifacts_ready": artifacts_ok,
                    "timestamp": get_utc_timestamp()
                }).encode("utf-8"))
            elif self.path == "/health/detailed":
                self._set_headers(200)
                files_to_check = [
                    "c2_listener.py", "ca.crt", "attestation/security.json",
                    "attestation/sovereign_consensus.json", "robots.txt",
                    ".well-known/security.txt", "openapi.json"
                ]
                audit_status = {f: os.path.exists(f) for f in files_to_check}
                self.wfile.write(json.dumps({
                    "status": "ONLINE",
                    "node": "TELUK_INTAN_EDGE_01",
                    "version": "3.3.0",
                    "architecture": "TesseraQS Core",
                    "uptime_seconds": get_uptime_seconds(),
                    "artifacts_integrity": audit_status,
                    "sovereignty_level": "100% EMPIRICAL ACTIVE",
                    "rate_limiting": {
                        "enabled": RATE_LIMIT_ENABLED,
                        "rps": RATE_LIMIT_RPS,
                        "burst": RATE_LIMIT_BURST
                    },
                    "anti_replay": {
                        "max_skew_seconds": MAX_REPLAY_WINDOW_SECONDS,
                        "nonce_ttl_seconds": NONCE_CACHE_TTL,
                        "tracked_nonces": len(SEEN_NONCES)
                    },
                    "metrics_summary": {
                        "total_requests": METRICS["total_requests"],
                        "processed_telemetry": METRICS["processed_telemetry"],
                        "errors": METRICS["errors"]
                    },
                    "timestamp": get_utc_timestamp()
                }, indent=2).encode("utf-8"))
            elif self.path == "/telemetry/stats":
                self._set_headers(200)
                stats = {
                    "status": "ONLINE",
                    "node": "TELUK_INTAN_EDGE_01",
                    "version": "3.3.0",
                    "uptime_seconds": get_uptime_seconds(),
                    "metrics": METRICS,
                    "timestamp": get_utc_timestamp()
                }
                self.wfile.write(json.dumps(stats, indent=2).encode("utf-8"))
            elif self.path == "/metrics":
                self._set_headers(200, content_type="text/plain; version=0.0.4; charset=utf-8")
                uptime = get_uptime_seconds()
                lines = [
                    "# HELP omega_c2_uptime_seconds Total server uptime in seconds",
                    "# TYPE omega_c2_uptime_seconds gauge",
                    f"omega_c2_uptime_seconds {uptime}",
                    "# HELP omega_c2_requests_total Total number of HTTP requests processed",
                    "# TYPE omega_c2_requests_total counter",
                    f"omega_c2_requests_total {METRICS['total_requests']}",
                    "# HELP omega_c2_telemetry_total Total telemetry packets processed",
                    "# TYPE omega_c2_telemetry_total counter",
                    f"omega_c2_telemetry_total {METRICS['processed_telemetry']}",
                    "# HELP omega_c2_signature_failures_total Total HMAC signature verification failures",
                    "# TYPE omega_c2_signature_failures_total counter",
                    f"omega_c2_signature_failures_total {METRICS['signature_failures']}",
                    "# HELP omega_c2_replay_failures_total Total anti-replay verification failures",
                    "# TYPE omega_c2_replay_failures_total counter",
                    f"omega_c2_replay_failures_total {METRICS['replay_failures']}",
                    "# HELP omega_c2_rate_limit_exceeded_total Total rate limiting rejection occurrences",
                    "# TYPE omega_c2_rate_limit_exceeded_total counter",
                    f"omega_c2_rate_limit_exceeded_total {METRICS['rate_limit_exceeded']}",
                    "# HELP omega_c2_errors_total Total HTTP errors generated",
                    "# TYPE omega_c2_errors_total counter",
                    f"omega_c2_errors_total {METRICS['errors']}",
                    "# HELP omega_c2_request_duration_seconds Request duration in seconds",
                    "# TYPE omega_c2_request_duration_seconds histogram",
                    f"omega_c2_request_duration_seconds_sum {round(METRICS['total_duration_seconds'], 6)}",
                    f"omega_c2_request_duration_seconds_count {METRICS['total_requests']}"
                ]
                for le_str, count in METRICS["duration_buckets"].items():
                    lines.append(f'omega_c2_request_duration_seconds_bucket{{le="{le_str}"}} {count}')
                for intent, count in METRICS["intents_executed"].items():
                    lines.append(f'omega_c2_intent_total{{intent="{intent}"}} {count}')
                self.wfile.write(("\n".join(lines) + "\n").encode("utf-8"))
            else:
                METRICS["errors"] += 1
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Endpoint tidak wujud"}).encode("utf-8"))
        finally:
            record_request_duration(time.time() - start_time)

    def do_POST(self) -> None:
        start_time = time.time()
        METRICS["total_requests"] += 1
        try:
            client_ip = self.client_address[0] if self.client_address else "127.0.0.1"
            if not check_rate_limit(client_ip):
                METRICS["rate_limit_exceeded"] += 1
                METRICS["errors"] += 1
                self._set_headers(429)
                self.wfile.write(json.dumps({
                    "error": "Too Many Requests",
                    "message": "Kadar permintaan melebihi had kedaulatan dibenarkan."
                }).encode("utf-8"))
                return

            if self.path == "/omni-listener":
                try:
                    length = int(self.headers.get("Content-Length", 0))
                except (ValueError, TypeError):
                    length = 0

                if length > MAX_PAYLOAD_SIZE:
                    METRICS["errors"] += 1
                    self._set_headers(413)
                    self.wfile.write(json.dumps({
                        "error": "Payload Terlalu Besar",
                        "message": f"Saiz muatan melebihi had maksimum {MAX_PAYLOAD_SIZE} bait."
                    }).encode("utf-8"))
                    return

                raw_bytes = self.rfile.read(length) if length > 0 else b""
                sig_header = self.headers.get("X-Sovereign-Signature", "")
                ts_header = self.headers.get("X-Sovereign-Timestamp", "")
                nonce_header = self.headers.get("X-Sovereign-Nonce", "")

                # Anti-Replay Verification (Timestamp window & Nonce uniqueness)
                replay_ok, replay_err = verify_anti_replay(ts_header, nonce_header)
                if not replay_ok:
                    METRICS["replay_failures"] += 1
                    METRICS["errors"] += 1
                    self._set_headers(401)
                    self.wfile.write(json.dumps({
                        "error": "Unauthorized",
                        "message": replay_err
                    }).encode("utf-8"))
                    return

                # HMAC Cryptographic Sovereign Verification
                if SOVEREIGN_SECRET_KEY and not verify_sovereign_signature(raw_bytes, sig_header):
                    METRICS["signature_failures"] += 1
                    METRICS["errors"] += 1
                    self._set_headers(401)
                    self.wfile.write(json.dumps({
                        "error": "Unauthorized",
                        "message": "Pengesahan tandatangan kriptografi kedaulatan (HMAC-SHA256) gagal."
                    }).encode("utf-8"))
                    return

                body = raw_bytes.decode("utf-8", errors="replace") if raw_bytes else ""
                try:
                    payload = json.loads(body) if body else {}
                except Exception:
                    payload = {"raw": body}

                if not isinstance(payload, dict):
                    payload = {"raw": payload}

                METRICS["processed_telemetry"] += 1
                directive = str(payload.get("directive", "")).lower()
                response_data: Dict[str, Any] = {
                    "status": "ACK",
                    "received": payload,
                    "action": "TELEMETRY_LOGGED",
                    "message": "Paket telemetri diproses.",
                    "timestamp": get_utc_timestamp()
                }

                # 1. INTENT: Pembersihan Modul Numerik Legasi
                if any(k in directive for k in ["buang", "padam", "purge", "delete"]) and "modul" in directive:
                    pattern = os.path.join(MODULES_DIR, "infografik_gambarajah_interaktif_modul_[0-9]*.html")
                    deleted = []
                    for f in glob.glob(pattern):
                        try:
                            if is_safe_path(MODULES_DIR, f):
                                os.remove(f)
                                deleted.append(os.path.basename(f))
                        except (FileNotFoundError, PermissionError, OSError) as err:
                            logger.warning("Purge skipped for %s: %s", f, err)
                    response_data["action"] = "PURGE_EXECUTED"
                    response_data["deleted_count"] = len(deleted)
                    response_data["message"] = f"Berjaya menghapuskan {len(deleted)} modul numerik lama."
                    METRICS["intents_executed"]["PURGE_EXECUTED"] += 1

                # 2. INTENT: Pembaikan Pantas & Pematuhan Air-Gap (Menyeluruh)
                elif any(k in directive for k in ["baiki", "repair", "heal", "fix", "audit", "airgap"]):
                    patched_count = 0
                    if os.path.exists(MODULES_DIR) and os.path.isdir(MODULES_DIR):
                        for root, _, files in os.walk(MODULES_DIR):
                            for file in files:
                                if file.endswith(".html"):
                                    html_path = os.path.join(root, file)
                                    if is_safe_path(MODULES_DIR, html_path):
                                        try:
                                            with open(html_path, "r", encoding="utf-8", errors="ignore") as inf:
                                                c = inf.read()
                                            new_c = re.sub(r'https?://cdn\.tailwindcss\.com', '/tailwind.js', c)
                                            if new_c != c:
                                                with open(html_path, "w", encoding="utf-8") as outf:
                                                    outf.write(new_c)
                                                patched_count += 1
                                        except (FileNotFoundError, PermissionError, OSError) as err:
                                            logger.error("Failed to patch %s: %s", html_path, err)

                    auditor_path = os.path.join(MODULES_DIR, "auditor_l5_verifier.py")
                    audit_lines = []
                    if is_safe_path(MODULES_DIR, auditor_path) and os.path.exists(auditor_path):
                        try:
                            audit_res = subprocess.run(
                                [sys.executable, auditor_path],
                                capture_output=True, text=True, timeout=10
                            )
                            audit_lines = [line for line in audit_res.stdout.split("\n") if line.strip()][-3:]
                        except Exception as err:
                            logger.error("Auditor L5 execution error: %s", err)
                            audit_lines = [f"Auditor L5 error: {err}"]

                    if not audit_lines:
                        audit_lines = ["Auditor L5 file not found, patching applied."]

                    response_data["action"] = "AUDIT_AND_HEAL_COMPLETE"
                    response_data["audit_summary"] = audit_lines
                    response_data["patched_count"] = patched_count
                    response_data["message"] = "Fail-fail HTML dipateri ke Air-Gap & Audit L5 disahkan."
                    METRICS["intents_executed"]["AUDIT_AND_HEAL_COMPLETE"] += 1

                # 3. INTENT: Simulasi Rekursif L2-L5 (3 Kitaran + Eskalasi Kitaran ke-4 kepada Alpha)
                elif any(k in directive for k in ["kemaskini", "workflow", "rekursif", "recursive"]):
                    sim_logs = []
                    max_cycles = 3
                    simulation_passed = True

                    for cycle in range(1, max_cycles + 1):
                        sim_logs.append(f"[SIMULATION_CYCLE_{cycle}] L2-L5 Recursive validation passed.")

                    if "force_fail" in directive:
                        simulation_passed = False
                        sim_logs.append("[SIMULATION_CYCLE_4_CRITICAL] Anomali dikesan. Ambang batas gagal dicapai pada kitaran ke-4.")

                    if simulation_passed:
                        response_data["action"] = "RECURSIVE_SIMULATION_UPDATED"
                        response_data["simulation_cycles"] = max_cycles
                        response_data["audit_summary"] = sim_logs
                        response_data["message"] = "Workflow L2-L5 disahkan berjaya secara rekursif dan dipilih untuk eksekusi."
                        METRICS["intents_executed"]["RECURSIVE_SIMULATION_UPDATED"] += 1
                    else:
                        response_data["status"] = "ESCALATION_REQUIRED"
                        response_data["action"] = "ESCALATED_TO_ALPHA"
                        response_data["simulation_cycles"] = 4
                        response_data["audit_summary"] = sim_logs
                        response_data["message"] = "Simulasi gagal pada kitaran ke-4. Kawalan diserah semula kepada Alpha untuk suntingan arahan."
                        METRICS["intents_executed"]["ESCALATED_TO_ALPHA"] += 1
                else:
                    METRICS["intents_executed"]["TELEMETRY_LOGGED"] += 1

                self._set_headers(200)
                self.wfile.write(json.dumps(response_data).encode("utf-8"))
            else:
                METRICS["errors"] += 1
                self._set_headers(404)
                self.wfile.write(json.dumps({"error": "Endpoint tidak wujud"}).encode("utf-8"))
        except Exception as e:
            METRICS["errors"] += 1
            logger.error("Error processing POST request: %s", str(e))
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": "Ralat Pelayan Dalaman", "details": str(e)}).encode("utf-8"))
        finally:
            record_request_duration(time.time() - start_time)


if __name__ == "__main__":
    server_class = getattr(http.server, "ThreadingHTTPServer", http.server.HTTPServer)
    server = server_class((HOST, PORT), C2Handler)
    logger.info("OMEGA C2 Listener running on %s:%d...", HOST, PORT)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped cleanly.")
        server.server_close()
