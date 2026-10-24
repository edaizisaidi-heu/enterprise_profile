# OMEGA SOVEREIGN LABS — C2 TELEMETRY BRIDGE & AUTONOMOUS INTENT EXECUTOR

Sistem jambatan telemetri C2 dan enjin eksekusi niat autonomi bagi **TesseraQS Core Architecture**.

---

## 📌 Ringkasan Senibina & Falsafah

`c2_listener.py` bertindak sebagai pelayan HTTP C2 autonomi yang memproses paket telemetri dan menjalankan arahan (*intents*) autonomi berpandukan direktif yang diterima. Senibina ini berpandukan falsafah **Dialektika Fraktal Rekursif YinYang**:

- **Yin (Pasif & Audit)**: Pengesahan integriti data pasif, status kesihatan pelayan (`/health`), pematuhan *Air-Gap*, cap masa UTC ISO 8601, serta attestation keselamatan RFC 9116.
- **Yang (Aktif & Eksekusi)**: Pemprosesan `/omni-listener`, pembersihan modul legasi, pematerian automatik (*self-healing patch*), dan eskalasi kitaran ke-4 kepada Alpha.

---

## 📊 Endpoints & Intent Matrix

### Endpoint HTTP
| Endpoint | Kaedah HTTP | Fungsi / Tindak Balas | Status HTTP |
| :--- | :--- | :--- | :--- |
| `/health`, `/status` | `GET` / `HEAD` | Memulangkan status kesihatan pelayan (`ONLINE`, v3.2.0, metadata nod Teluk Intan, UTC timestamp). | `200 OK` / `404 Not Found` |
| `/omni-listener` | `POST` | Memproses paket telemetri dan menjalankan intent autonomi berpandukan direktif. | `200 OK` / `413 Payload Too Large` / `500 Error` |
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

## ⚙️ Pembolehubah Persekitaran (Environment Variables)

- `HOST`: Antaramuka pelayan C2 (Default: `127.0.0.1`).
- `PORT`: Port pelayan HTTP C2 (Default: `5000`).
- `MODULES_DIR`: Laluan ke direktori modul kerja (Default: `~/workspace/modules`).
- `C2_BASE_URL`: Tapak URL pelayan C2 bagi skrip pengesahan (Default: `http://127.0.0.1:5000`).
- `C2_URL`: URL penuh endpoint `/omni-listener` (Default: `${C2_BASE_URL}/omni-listener`).
- `MAX_PAYLOAD_SIZE`: Had maksimum saiz muatan JSON (Default: `1048576` / 1MB).

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
# Pastikan c2_listener.py berjalan di latar belakang sebelum memulakan ujian swarm
python3 verify_omega_swarm.py
```

### 4. Pengesahan Kedaulatan Pertahanan (Live Attestation & Forensik)
```bash
./verify_defense.sh
```

---

## 🛡️ Keselamatan & Kedaulatan Digital

- **RFC 9116 Attestation**: Disahkan pada `/.well-known/security.txt` dan `/security.json`.
- **Konsensus ZKP Autonomi**: Bukti konsensus tempatan Teluk Intan Node pada `/attestation/sovereign_consensus.json`.
- **Anti-AI Training Shield**: Sekatan bot pengutip data & latihan AI dikuatkuasakan via `robots.txt`.
