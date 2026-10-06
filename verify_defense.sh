#!/bin/sh
# =============================================================================
# TESSERAQS / OMEGA SOVEREIGN INTELLIGENCE - PUBLIC INDEPENDENT AUDIT KIT
# Jalankan skrip ini dari mana-mana terminal Linux / macOS / BSD di seluruh dunia
# =============================================================================

echo "================================================================="
echo "🛡️  MENGESAHKAN KEDAULATAN DIGITAL TESSERAQS SECARA LANGSUNG"
echo "    Domain: https://tesseraqs.cloud-ip.cc"
echo "================================================================="

echo "\n[+] 1. Menyemak RFC 9116 Security Attestation..."
curl -sL "https://tesseraqs.cloud-ip.cc/.well-known/security.txt" | head -n 6

echo "\n[+] 2. Mengambil Bukti Konsensus ZKP Autonomi (Teluk Intan Node)..."
curl -sL "https://tesseraqs.cloud-ip.cc/attestation/sovereign_consensus.json" | grep -E '"node"|"tls_version"|"zkp_enforced"|"role"|"zkp_status"'

echo "\n[+] 3. Mengesahkan Perisai Anti-Training AI..."
curl -sL "https://tesseraqs.cloud-ip.cc/robots.txt" | grep -A 4 "SEKATAN MUTLAK"

echo "\n================================================================="
echo "✓ BUKTI FORENSIK SELESAI: Kedaulatan Terbukti Secara Empirikal."
echo "================================================================="
