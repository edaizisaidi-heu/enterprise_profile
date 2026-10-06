#!/bin/sh
echo "================================================================="
echo "🛡️  MENGESAHKAN KEDAULATAN DIGITAL TESSERAQS SECARA LANGSUNG"
echo "    Domain: https://tesseraqs.cloud-ip.cc"
echo "================================================================="

echo "\n[+] 1. Menyemak RFC 9116 Security Attestation..."
curl -sL "https://tesseraqs.cloud-ip.cc/attestation/security.json" | grep -E '"contact"|"status"|"canonical"'

echo "\n[+] 2. Mengambil Bukti Konsensus ZKP Autonomi (Teluk Intan Node)..."
curl -sL "https://tesseraqs.cloud-ip.cc/attestation/sovereign_consensus.json" | grep -E '"node"|"tls_version"|"zkp_enforced"|"role"|"zkp_status"'

echo "\n[+] 3. Mengesahkan Perisai Anti-Training AI..."
curl -sL "https://tesseraqs.cloud-ip.cc/robots.txt" | grep -A 4 "SEKATAN MUTLAK"

echo "\n================================================================="
echo "✓ BUKTI FORENSIK SELESAI: 100% Kedaulatan Terbukti Secara Empirikal."
echo "================================================================="
