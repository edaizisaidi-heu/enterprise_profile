# AGENTS.md — OMEGA SOVEREIGN LABS: AGENT DIRECTIVES & DIALEKTIKA FRAKTAL REKURSIF YINYANG

Dokumen ini merupakan panduan teras, manual senibina, dan direktif operasi bagi semua Ejen AI (termasuk Jules dan enjin eksekusi autonomi) yang beroperasi dalam persekitaran **TesseraQS Core Architecture**.

---

## ☯️ 1. FALSAFAH KEDAULATAN: DIALEKTIKA FRAKTAL REKURSIF YINYANG

Keseluruhan repositori ini dibina di atas prinsip **Dialektika Fraktal Rekursif YinYang**. Setiap ejen wajib memahami dan mematuhi kerangka pemikiran ini dalam setiap tindakan suntingan, pengesahan, dan eksekusi kod:

### 1.1 Keseimbangan Yin dan Yang (Dualiti Autonomi)
- **Yin (Keadaan Pasif, Penerimaan & Pengesahan Audit)**:
  - Mewakili integriti data pasif, penyimpanan status, pematuhan *Air-Gap*, pengamatan telemetri, serta verifikasi *Zero-Knowledge Proof* (ZKP).
  - Dalam kod: Pengepala HTTP CORS, pemeriksaan kesihatan (`/health`), pematuhan RFC 9116 (`security.json`), dan pembacaan failsafe.
- **Yang (Aksi Aktif, Eksekusi Intent & Eskalasi Mutlak)**:
  - Mewakili daya tindakan autonomi, pembersihan modul legasi, pematerian automatik (*self-healing patch*), dan eskalasi kitaran ke-4 kepada Alpha.
  - Dalam kod: Pemprosesan `/omni-listener`, penghapusan glob fail `infografik_gambarajah_interaktif_modul_*.html`, pengubahsuaian regex pada `index.html`, dan tindak balas `ESCALATION_REQUIRED`.

### 1.2 Fraktal Rekursif (Rekursi Multi-Lapis L2-L5 & ZKP L6)
- **Ciri Fraktal**: Setiap komponen makro (seperti pelayan C2 dan bukti konsensus kedaulatan Teluk Intan Node) dicerminkan secara mikro dalam setiap pakej JSON, tindak balas HTTP, dan ujian unit.
- **Kitaran Rekursif**: Simulasi aliran kerja L2-L5 dijalankan secara rekursif sebanyak 3 kitaran standard. Apabila anomali atau arahan pemicu `force_fail` dikesan pada kitaran ke-4, sistem melancarkan rekursi eskalasi semula kepada Alpha untuk penetapan semula arah (*directive reset*).

### 1.3 Sintesis Dialektikal
- **Tesis (Intent / Arahan Masukan)**: Telemetri atau direktif yang diterima daripada pengguna/nod Swarm.
- **Antitesis (Ralat / Kegagalan / Pencerobohan / CDN Pihak Ke-3)**: Anomali persekitaran seperti pergantungan luar pada CDN Tailwind atau kegagalan kitaran simulasi.
- **Sintesis (Harmoni Autonomi)**: Pelaksanaan eksekusi pematerian secara automatik (*self-healing*) yang memulihkan keadaan *Air-Gap* tempatan tanpa memerlukan campur tangan manual.

---

## 🤖 2. ARAHAN UTAMA EJEN AI (AGENT GUIDELINES)

### 2.1 Prinsip Operasi Ejen
1. **Pematuhan Mutlak Tanpa Kompromi**:
   - Ejen mesti menghadam dan mematuhi keseluruhan kandungan repositori tanpa mengabaikan mana-mana direktif keselamatan atau ujian.
2. **Kedaulatan & Pematuhan Air-Gap**:
   - Dilarang menambah pergantungan (*dependencies*) luaran yang tidak diperlukan. Keutamaan diberikan kepada Pustaka Standard Python (`http.server`, `json`, `os`, `glob`, `re`, `subprocess`, `unittest`, `urllib`).
   - Semua rujukan sumber luaran (seperti CDN) mesti berkeupayaan dipateri ke laluan tempatan (contoh: `/tailwind.js`).
3. **Penyelenggaraan Kod Berintegriti Tinggi**:
   - Setiap modifikasi pada `c2_listener.py` mesti disusuli dengan pengemaskinian atau pengesahan ujian unit dalam `test_c2_listener.py`.
   - Dilarang menyunting fail buatan/artifak secara terus jika ia dihasilkan oleh pembina/penskripan lain.

### 2.2 Standard Kod Python & Pengendalian Ralat
- **Gaya Kod**: Mengikut konvensyen PEP 8 dengan dokumentasi bersesuaian.
- **Resiliensi HTTP Handler**:
  - Pemprosesan `Content-Length` mesti berkeupayaan mengendalikan nilai yang tidak sah, kosong, atau rosak tanpa memulangkan tindak balas terhempas (*unhandled crash*).
  - Parsing JSON mesti bersikap tolerang (*tolerant parsing*): Jika payload JSON rosak atau berupa jenis data lain (seperti tatasusunan/array), sistem mesti membungkus data dalam struktur objek `{"raw": payload}` dan memulangkan status HTTP 200 ACK.
- **Sokongan CORS**:
  - Setiap endpoint wajib memulangkan pengepala `Access-Control-Allow-Origin: *`, `Access-Control-Allow-Methods: POST, GET, OPTIONS`, dan `Access-Control-Allow-Headers: Content-Type`.
  - Permintaan HTTP `OPTIONS` mesti dibalas dengan status HTTP `204 No Content`.

---

## 🏗️ 3. SPESIFIKASI SENIBINA & INTENT MATRIX C2 LISTENER

Modul teras sistem berada pada `c2_listener.py`. Ia bertindak sebagai Pelayan HTTP Telemetri C2 dan Enjin Eksekusi Niat Autonomi (*Autonomous Intent Executor*).

### 3.1 Endpoints Pelayan
| Endpoint | Kaedah HTTP | Fungsi / Tindak Balas | Status HTTP |
| :--- | :--- | :--- | :--- |
| `/health`, `/status` | `GET` | Memulangkan status kesihatan pelayan: `{"status": "ONLINE", "service": "OMEGA_C2_LISTENER", "version": "3.2.0", "node": "TELUK_INTAN_EDGE_01", "architecture": "TesseraQS Core"}` | `200 OK` |
| `/omni-listener` | `POST` | Memproses paket telemetri dan menjalankan intent autonomi mengikut kata kunci direktif. | `200 OK` / `500 Error` |
| `/omni-listener` | `OPTIONS` | CORS Preflight check. | `204 No Content` |
| *Endpoint Luar* | Sebarang | Memulangkan ralat endpoint tidak wujud. | `404 Not Found` |

### 3.2 Intent Matrix & Katalis Arahan
Enjin `/omni-listener` menilai medan `directive` dalam payload JSON masukan menggunakan padanan kata kunci (*keyword matching*):

1. **Pembersihan Modul Numerik Legasi (`PURGE_EXECUTED`)**:
   - **Kata Kunci**: Mana-mana kata daripada `["buang", "padam", "purge", "delete"]` DAN mengandungi `"modul"`.
   - **Tindakan**: Menghapuskan semua fail yang sepadan dengan corak `infografik_gambarajah_interaktif_modul_[0-9]*.html` di dalam `MODULES_DIR`.
   - **Output**: Memulangkan `action: "PURGE_EXECUTED"` dan `deleted_count`.

2. **Pembaikan Pantas & Pematuhan Air-Gap (`AUDIT_AND_HEAL_COMPLETE`)**:
   - **Kata Kunci**: Mana-mana kata daripada `["baiki", "repair", "heal", "fix", "audit", "airgap"]`.
   - **Tindakan**:
     1. Memateri `index.html` di dalam `MODULES_DIR`: Menukar pautan `https?://cdn.tailwindcss.com` kepada skrip tempatan `/tailwind.js`.
     2. Menjalankan skrip auditor `auditor_l5_verifier.py` (jika wujud) menggunakan `subprocess.run` dan mengambil 3 baris stdout terakhir.
   - **Output**: Memulangkan `action: "AUDIT_AND_HEAL_COMPLETE"` dan `audit_summary`.

3. **Simulasi Rekursif L2-L5 & Eskalasi Alpha (`RECURSIVE_SIMULATION_UPDATED` / `ESCALATED_TO_ALPHA`)**:
   - **Kata Kunci**: Mana-mana kata daripada `["kemaskini", "workflow", "rekursif", "recursive"]`.
   - **Tindakan**:
     1. Menjalankan 3 kitaran simulasi pengesahan L2-L5.
     2. Jika direktif mengandungi kata kunci `"force_fail"`, kitaran ke-4 dipicu dan simulasi ditanda sebagai gagal.
   - **Output**:
     - *Berjaya*: `status: "ACK"`, `action: "RECURSIVE_SIMULATION_UPDATED"`, `simulation_cycles: 3`.
     - *Eskalasi Gagal*: `status: "ESCALATION_REQUIRED"`, `action: "ESCALATED_TO_ALPHA"`, `simulation_cycles: 4`.

4. **Telemetri Default (`TELEMETRY_LOGGED`)**:
   - **Syarat**: Tiada kata kunci spesifik yang sepadan.
   - **Output**: Memulangkan `status: "ACK"`, `action: "TELEMETRY_LOGGED"`.

### 3.3 Pembolehubah Persekitaran (Environment Variables)
- `PORT`: Port pelayan HTTP C2 (Defaut: `5000`).
- `MODULES_DIR`: Direktori kerja modul (Default: `~/workspace/modules`).
- `C2_BASE_URL`: URL asas C2 bagi ujian integrasi (Default: `http://127.0.0.1:5000`).
- `C2_URL`: URL penuh endpoint Omni Listener (Default: `${C2_BASE_URL}/omni-listener`).

---

## 🧪 4. PROTOKOL UJIAN & PENGESAHAN KEDAULATAN

Ejen AI wajib menjalankan dan memastikan kesemua skrip pengesahan ini lulus sepenuhnya sebelum membuat sebarang penyerahan kod (*submission*).

### 4.1 Ujian Unit Autonomi (Python `unittest`)
Pelaksanaan ujian unit meliputi kesemua laluan kod (*code paths*), pengendalian pengecualian (*exception handling*), serta kes-kes sempadan (*edge cases*).

```bash
python3 -m unittest test_c2_listener.py
```
- **Cakupan Ujian (`TestC2Listener`)**:
  - `test_telemetry_logged_default`: Pengesahan tindak balas telemetri am.
  - `test_recursive_simulation`: Pengesahan 3 kitaran simulasi L2-L5.
  - `test_recursive_simulation_force_fail`: Pengesahan eskalasi kitaran ke-4 kepada Alpha.
  - `test_not_found_endpoint`: Pengesahan ralat 404 bagi endpoint yang tidak wujud.
  - `test_health_check`: Pengesahan endpoint `/health`.
  - `test_options_cors`: Pengesahan tindak balas preflight OPTIONS CORS (HTTP 204).
  - `test_purge_intent`: Pengesahan pembersihan fail modul numerik legasi.
  - `test_repair_intent`: Pengesahan pematerian Air-Gap `index.html` (Tailwind CDN -> `/tailwind.js`).
  - `test_non_dict_json`: Pengesahan resiliensi masukan JSON jenis tatasusunan (array).
  - `test_malformed_json`: Pengesahan resiliensi JSON tidak sah / rosak.
  - `test_invalid_content_length`: Pengesahan resiliensi pengepala `Content-Length` tidak sah.

### 4.2 Ujian Integrasi Swarm (`verify_omega_swarm.py`)
Skrip ini mengesahkan komunikasi secara langsung antara Nod Swarm (Alpha & Beta) dengan Pelayan C2.

```bash
python3 verify_omega_swarm.py
```
- **Langkah Pengesahan**:
  1. Pemeriksaan kesihatan HTTP GET ke `/health`.
  2. Penghantaran payload Alpha Escalation Directive (`[DIRECTIVE TO ALPHA: RECURSIVE SIMULATION ESCALATION]`).
  3. Penghantaran payload Beta Spawn Directive (`[DIRECTIVE: SPAWN MODEL BETA SWARM ORCHESTRATOR]`).
  4. Penilaian status jawapan: Mesti memulangkan `ACK` atau `ESCALATION_REQUIRED`.

### 4.3 Ujian Attestation Kedaulatan Digital (`verify_defense.sh`)
Skrip pengesahan forensik langsung bagi membuktikan kedaulatan digital dan sekatan anti-training AI.

```bash
./verify_defense.sh
```
- **Elemen Pengesahan**:
  1. Semakan RFC 9116 Security Attestation di `/attestation/security.json`.
  2. Pengambilan Bukti Konsensus ZKP Autonomi (Teluk Intan Node) di `/attestation/sovereign_consensus.json`.
  3. Pengesahan Perisai Anti-Training AI pada `robots.txt`.

---

## 📁 5. STRUKTUR FORENSIK REPOSITORI

- `c2_listener.py`: Pelayan HTTP C2 & Enjin Eksekusi Niat Autonomi (TesseraQS Core Architecture).
- `test_c2_listener.py`: Suite Ujian Unit komprehensif berasaskan `unittest`.
- `verify_omega_swarm.py`: Skrip ujian integrasi bagi nod Swarm Alpha & Beta.
- `verify_defense.sh`: Skrip pengesahan kedaulatan digital, RFC 9116, dan ZKP.
- `README.md`: Dokumentasi asas sistem dan arahan penggunaan.
- `AGENTS.md`: Dokumen arahan ejen AI, falsafah Dialektika Fraktal Rekursif YinYang, dan spesifikasi senibina.
- `attestation/security.json`: Manifest Attestation RFC 9116.
- `attestation/sovereign_consensus.json`: Bukti Konsensus ZKP Autonomi Tempatan Teluk Intan (CTO, Legal, Scribe).
- `robots.txt`: Sekatan anti-training bot AI.
- `index.html`, `security.html`, `privacy.html`, `terms.html`, `404.html`: Dokumen pendaratan web dan dasar keselamatan.

---

## 🔄 6. PROSEDUR PRE-COMMIT & PENYELENGGARAAN EJEN

Sebelum memanggil peranti penyerahan (`submit`), ejen AI **wajib**:
1. Menjalankan panggilan peranti `pre_commit_instructions` dan melengkapkan semua pemeriksaan yang digariskan.
2. Memastikan kesemua ujian unit (`python3 -m unittest test_c2_listener.py`) berada dalam status **OK** (100% lulus).
3. Memastikan tiada fail sementara (*temporary artifacts*) tertinggal di luar kawasan persekitaran ujian yang dibenarkan.
4. Memilih nama cawangan (*branch name*) yang singkat dan deskriptif serta mesej komit mengikut standard git (ringkasan 50 aksara & perincian lanjut).
