import urllib.request
import json
import sys

URL = "http://127.0.0.1:5000/omni-listener"

def send_payload(payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(URL, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

print("[*] Memulakan Pengesahan Mutlak Omega Swarm (C2)...")

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
