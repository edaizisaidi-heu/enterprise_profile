import urllib.request
import json
import os
import sys

DEFAULT_PORT = os.environ.get("PORT", "5000")
BASE_URL = os.environ.get("C2_BASE_URL", f"http://127.0.0.1:{DEFAULT_PORT}")
URL = os.environ.get("C2_URL", f"{BASE_URL}/omni-listener")
HEALTH_URL = f"{BASE_URL}/health"

def check_health():
    try:
        req = urllib.request.Request(HEALTH_URL)
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("status") == "ONLINE"
    except Exception:
        return False

def send_payload(payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

print("[*] Memulakan Pengesahan Mutlak Omega Swarm (C2)...")

if check_health():
    print(f"[Health Check] Server di {HEALTH_URL} disahkan ONLINE.")
else:
    print(f"[Health Check] Amaran: Health check ke {HEALTH_URL} tidak memulangkan status ONLINE. Meneruskan ujian telemetri...")

# Ujian 1: Alpha Escalation Directive
alpha_payload = {
    "module": "omega_swarm_command",
    "intent": "SWARM_DIRECTIVE",
    "directive": "[DIRECTIVE TO ALPHA: RECURSIVE SIMULATION ESCALATION]"
}
res_alpha = send_payload(alpha_payload)
print(f"[Alpha Test] Response: {res_alpha.get('action')} - Status: {res_alpha.get('status')}")

# Ujian 2: Beta Spawn Directive
beta_payload = {
    "module": "omega_swarm_command",
    "intent": "SWARM_DIRECTIVE",
    "directive": "[DIRECTIVE: SPAWN MODEL BETA SWARM ORCHESTRATOR]"
}
res_beta = send_payload(beta_payload)
print(f"[Beta Test] Response: {res_beta.get('action')} - Status: {res_beta.get('status')}")

if res_alpha.get('status') in ["ACK", "ESCALATION_REQUIRED"] and res_beta.get('status') == "ACK":
    print("\n[✓] KEPUTUSAN MUKTAMAD: Semua nod Swarm & C2 lulus pengesahan kedaulatan.")
    sys.exit(0)
else:
    print("\n[!] AMARAN: Anomali dikesan pada tindak balas nod C2.")
    sys.exit(1)
