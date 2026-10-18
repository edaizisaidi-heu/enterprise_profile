# OMEGA SOVEREIGN LABS — C2 TELEMETRY BRIDGE & AUTONOMOUS INTENT EXECUTOR

Sistem jambatan telemetri C2 dan enjin eksekusi niat autonomi bagi **TesseraQS Core Architecture**.

## 📌 Ringkasan Enjin & Senhibina

`c2_listener.py` bertindak sebagai pelayan HTTP C2 yang memproses paket telemetri dan menjalankan arahan (intents) autonomi berpandukan direktif yang diterima.

### Ciri-ciri Utama & Intent Matrix

1. **GET `/health` / `/status`**:
   - Memulangkan status kesihatan pelayan (`"status": "ONLINE"`).
2. **POST `/omni-listener`**:
   - **Pembersihan Modul Numerik Legasi** (`buang`, `padam`, `purge`, `delete` + `modul`): Menghapuskan fail modul legasi daripada `MODULES_DIR`.
   - **Pembaikan Pantas & Pematuhan Air-Gap** (`baiki`, `repair`, `heal`, `fix`, `audit`, `airgap`): Memateri pautan CDN kepada sumber tempatan `/tailwind.js` pada `index.html` dan menjalankan audit pengesahan L5.
   - **Simulasi Rekursif L2-L5** (`kemaskini`, `workflow`, `rekursif`, `recursive`): Melakukan kitaran pengesahan rekursif L2-L5. Jika `force_fail` disertakan, eskalasi automatik diserahkan kepada Alpha.
3. **CORS Preflight**:
   - Sokongan penuh tindak balas `OPTIONS` untuk CORS.

---

## ⚙️ Pembolehubah Persekitaran (Environment Variables)

- `PORT`: Port pelayan HTTP (Defaut: `5000`).
- `MODULES_DIR`: Laluan ke direktori modul (Default: `~/workspace/modules`).
- `C2_BASE_URL`: Tapak URL pelayan C2 bagi skrip pengesahan (Default: `http://127.0.0.1:5000`).
- `C2_URL`: URL penuh endpoint `/omni-listener` (Default: `http://127.0.0.1:5000/omni-listener`).

---

## 🚀 Arahan Penggunaan & Ujian

### 1. Menjalankan Pelayan C2
```bash
python3 c2_listener.py
```

### 2. Menjalankan Ujian Unit (Unit Tests)
```bash
python3 -m unittest discover
```

### 3. Pengesahan Swarm Integrasi (Integration Verification)
```bash
python3 verify_omega_swarm.py
```

### 4. Pengesahan Kedaulatan Pertahanan (Live Attestation)
```bash
./verify_defense.sh
```
