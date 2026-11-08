# OMEGA SOVEREIGN LABS — C2 TELEMETRY BRIDGE & AUTONOMOUS INTENT EXECUTOR

Sistem jambatan telemetri C2 dan enjin eksekusi niat autonomi bagi **TesseraQS Core Architecture**.

[![Status](https://img.shields.io/badge/Sovereign_Defense-100%25_ACTIVE-brightgreen)](#-keselamatan--kedaulatan-digital)
[![OpenAPI 3.1](https://img.shields.io/badge/OpenAPI-3.1.0-blue)](/openapi.json)
[![RFC 9116](https://img.shields.io/badge/RFC_9116-VERIFIED-blue)](/.well-known/security.txt)
[![ZKP Consensus](https://img.shields.io/badge/ZKP_Circuit-corporate__auth-purple)](/attestation/sovereign_consensus.json)

---

## 📌 Ringkasan Senibina & Falsafah

`c2_listener.py` bertindak sebagai pelayan HTTP C2 autonomi yang memproses paket telemetri dan menjalankan arahan (*intents*) autonomi berpandukan direktif yang diterima. Senibina ini berpandukan falsafah **Dialektika Fraktal Rekursif YinYang**:

- **Yin (Pasif & Audit)**: Pengesahan integriti data pasif, status kesihatan pelayan (`/health`), pemantauan metrik masa nyata (`/metrics` & `/telemetry/stats`), pematuhan *Air-Gap*, cap masa UTC ISO 8601, serta attestation keselamatan RFC 9116.
- **Yang (Aktif & Eksekusi)**: Pemprosesan `/omni-listener`, verifikasi tandatangan kriptografi kedaulatan (HMAC-SHA256), pembersihan modul legasi, pematerian automatik (*self-healing patch*), dan eskalasi kitaran ke-4 kepada Alpha.

---

## 📊 Endpoints & Intent Matrix

### Endpoint HTTP
| Endpoint | Kaedah HTTP | Fungsi / Tindak Balas | Status HTTP |
| :--- | :--- | :--- | :--- |
| `/health`, `/status` | `GET` / `HEAD` | Memulangkan status kesihatan pelayan (`ONLINE`, v3.3.0, metadata nod Teluk Intan, UTC timestamp, `uptime_seconds`). | `200 OK` / `404 Not Found` |
| `/ready` | `GET` / `HEAD` | Semakan kesiapsiagaan komponen nod (Readiness Probe) bagi artifak keselamatan dan direktori modul. | `200 OK` / `503 Service Unavailable` |
| `/health/detailed` | `GET` / `HEAD` | Diagnostik mendalam nod, integriti 7 artifak keselamatan, konfigurasi rate limiting, dan status anti-replay. | `200 OK` |
| `/metrics` | `GET` / `HEAD` | Memulangkan metrik telemetri & operasi dalam format piawai Prometheus (text/plain) termasuk histogram latensi. | `200 OK` |
| `/telemetry/stats` | `GET` / `HEAD` | Memulangkan statistik terperinci operasi telemetri dan pecahan intent dalam format JSON. | `200 OK` |
| `/omni-listener` | `POST` | Memproses paket telemetri dan menjalankan intent autonomi berpandukan direktif (menyokong tandatangan `X-Sovereign-Signature`, `X-Sovereign-Timestamp`, `X-Sovereign-Nonce`). | `200 OK` / `401 Unauthorized` / `413 Payload Too Large` / `429 Too Many Requests` / `500 Error` |
| `/omni-listener` | `OPTIONS` | CORS Preflight check. | `204 No Content` |
| *Kaedah Tidak Dibenarkan* | `PUT`, `DELETE`, `PATCH` | Memulangkan ralat kaedah tidak dibenarkan. | `405 Method Not Allowed` |

### Intent Matrix (`/omni-listener`)
1. **Pembersihan Modul Numerik Legasi** (`PURGE_EXECUTED`):
   - Kata kunci: `buang`, `padam`, `purge`, `delete` + `modul`.
   - Menghapuskan modul numerik lama (`infografik_gambarajah_interaktif_modul_[0-9]*.html`) di `MODULES_DIR`.
2. **Pembaikan Pantas & Pematuhan Air-Gap** (`AUDIT_AND_HEAL_COMPLETE`):
   - Kata kunci: `baiki`, `repair`, `heal`, `fix`, `audit`, `airgap`.
   - Memateri pautan CDN Tailwind kepada pautan tempatan `/tailwind.js` secara rekursif pada fail `.html` dan melancarkan verifikasi `auditor_l5_verifier.py`.
3. **Simulasi Rekursif L2-L5** (`RECURSIVE_SIMULATION_UPDATED` / `ESCALATED_TO_ALPHA`):
   - Kata kunci: `kemaskini`, `workflow`, `rekursif`, `recursive`.
   - Melakukan 3 kitaran pengesahan rekursif L2-L5. Jika kata kunci `force_fail` dikesan pada kitaran ke-4, eskalasi automatik diserahkan kepada Alpha (`ESCALATION_REQUIRED`).
4. **Telemetri Default** (`TELEMETRY_LOGGED`):
   - Tindak balas lalai apabila tiada kata kunci khusus dikesan.

---

## 🛠️ TesseraQS CLI Kedaulatan Autonomi (`tessera_cli.py`)

Alat CLI mandiri bersepadu untuk pengurusan operasi dan telemetri nod:

```bash
# Semakan kesihatan nod
python3 tessera_cli.py health

# Ambil metrik JSON atau Prometheus
python3 tessera_cli.py metrics --format json
python3 tessera_cli.py metrics --format prometheus

# Hantar telemetri / arahan intent
python3 tessera_cli.py send --directive "[DIRECTIVE: RECURSIVE SIMULATION]"

# Penstriman status telemetri masa nyata
python3 tessera_cli.py live --interval 1.0 --count 5

# Audit forensik tempatan
python3 tessera_cli.py audit

# Verifikasi kedaulatan domain pengeluaran luaran
python3 tessera_cli.py verify-remote --target-url https://tesseraqs.cloud-ip.cc
```

---

## ⚙️ Pembolehubah Persekitaran (Environment Variables)

- `HOST`: Antaramuka pelayan C2 (Default: `127.0.0.1`).
- `PORT`: Port pelayan HTTP C2 (Default: `5000`).
- `MODULES_DIR`: Laluan ke direktori modul kerja (Default: `~/workspace/modules`).
- `C2_BASE_URL`: Tapak URL pelayan C2 bagi skrip pengesahan (Default: `http://127.0.0.1:5000`).
- `C2_URL`: URL penuh endpoint `/omni-listener` (Default: `${C2_BASE_URL}/omni-listener`).
- `MAX_PAYLOAD_SIZE`: Had maksimum saiz muatan JSON (Default: `1048576` / 1MB).
- `SOVEREIGN_SECRET_KEY`: Kunci rahsia HMAC-SHA256 bagi mengesahkan pengepala `X-Sovereign-Signature` (Pilihan).
- `MAX_REPLAY_WINDOW_SECONDS`: Had tetingkap toleransi masa anti-replay (Default: `300` / 5 minit).
- `NONCE_CACHE_TTL`: Jangka hayat cache nonce anti-replay dalam saat (Default: `600` / 10 minit).
- `RATE_LIMIT_ENABLED`: Mengaktifkan had kadar token bucket per IP klien (Default: `0` / ditutup).
- `RATE_LIMIT_RPS`: Token pengisian semula per saat (Default: `50.0`).
- `RATE_LIMIT_BURST`: Kapasiti maksimum burst token per IP (Default: `100.0`).

---

## 🚀 Arahan Penggunaan & Ujian

### 1. Menjalankan Pelayan C2
```bash
python3 c2_listener.py
```

### 2. Menjalankan Ujian Unit Autonomi
```bash
python3 -m unittest test_c2_listener.py
```

### 3. Pengesahan Swarm Integrasi
```bash
python3 verify_omega_swarm.py
```

### 4. Pengesahan Kedaulatan Pertahanan (Live Attestation & Forensik)
```bash
./verify_defense.sh
```

### 5. Verifikasi Holistik Sehenti
```bash
./run_all_verifications.sh
```

---

## 🛡️ Keselamatan & Kedaulatan Digital

- **OpenAPI 3.1 Specification**: Didokumentasikan secara rasmi pada `/openapi.json` lengkap dengan skema `securitySchemes` HMAC-SHA256 (`SovereignSignature`).
- **Sijil Root CA Berdaulat (RSA-4096)**: Sijil X.509 RSA-4096 berdaulat pada `/ca.crt` sebagai punca kepercayaan enkripsi (*root of trust*).
- **RFC 9116 Attestation**: Disahkan pada `/.well-known/security.txt`, `/security.txt`, dan `/security.json`.
- **Konsensus ZKP Autonomi**: Bukti konsensus tempatan Teluk Intan Node pada `/attestation/sovereign_consensus.json` (Peranan: CTO, Legal, Scribe).
- **Anti-AI Training Shield**: Sekatan bot pengutip data & latihan AI dikuatkuasakan via `robots.txt`.
- **Integriti & Kedaulatan Empirikal**: 100% kedaulatan terbukti secara empirikal melalui pengesahan forensik langsung (`verify_defense.sh`).
