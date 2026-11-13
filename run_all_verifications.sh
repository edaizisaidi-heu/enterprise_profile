#!/bin/bash
set -e

echo "================================================================="
echo "🌟 OMEGA SOVEREIGN LABS: SEHENTI VERIFIKASI HOLISTIK TESSERAQS"
echo "================================================================="

# 1. Jalankan Unit Tests
echo ""
echo "[+] 1. Menjalankan Ujian Unit Autonomi (unittest)..."
python3 -m unittest test_c2_listener.py

# 2. Mulakan Pelayan C2 di latar belakang untuk Ujian Integrasi
echo ""
echo "[+] 2. Memulakan Pelayan C2 untuk Ujian Integrasi & Swarm..."
export PORT=5005
export C2_BASE_URL="http://127.0.0.1:5005"
export C2_URL="http://127.0.0.1:5005/omni-listener"

python3 c2_listener.py > /tmp/c2_test_server.log 2>&1 &
SERVER_PID=$!
trap "kill -9 $SERVER_PID 2>/dev/null || true" EXIT

# Tunggu pelayan sedia
sleep 1

# 3. Ujian Integrasi Swarm
echo ""
echo "[+] 3. Menjalankan Pengesahan Swarm Alpha & Beta..."
python3 verify_omega_swarm.py

# 4. Ujian CLI Kedaulatan Autonomi
echo ""
echo "[+] 4. Menguji Antaramuka CLI Kedaulatan Autonomi (tessera_cli.py)..."
python3 tessera_cli.py --base-url "$C2_BASE_URL" health
python3 tessera_cli.py --base-url "$C2_BASE_URL" health --detailed
python3 tessera_cli.py --base-url "$C2_BASE_URL" ready
python3 tessera_cli.py --base-url "$C2_BASE_URL" metrics --format json
python3 tessera_cli.py --base-url "$C2_BASE_URL" metrics --format prometheus
python3 tessera_cli.py --base-url "$C2_BASE_URL" live --count 1
python3 tessera_cli.py --base-url "$C2_BASE_URL" send --directive "[DIRECTIVE: CLI VERIFICATION TEST]"
python3 tessera_cli.py audit

# 5. Ujian Pertahanan Forensik & RFC 9116
echo ""
echo "[+] 5. Mengesahkan Lapisan Pertahanan Forensik Langsung..."
./verify_defense.sh

# Hentikan pelayan ujian
kill -9 $SERVER_PID 2>/dev/null || true
trap - EXIT

echo ""
echo "================================================================="
echo "🏆 KESEMUA UJIAN & PENGESAHAN KEDAULATAN LULUS 100%!"
echo "   TesseraQS Core Architecture Bersedia Untuk Skala Global."
echo "================================================================="
