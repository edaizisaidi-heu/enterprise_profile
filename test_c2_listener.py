import unittest
import http.server
import threading
import json
import os
import tempfile
import urllib.request
import urllib.error
import hmac
import hashlib
import c2_listener
import tessera_cli

class TestC2Listener(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory for MODULES_DIR testing
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.old_modules_dir = c2_listener.MODULES_DIR
        cls.old_secret = c2_listener.SOVEREIGN_SECRET_KEY
        c2_listener.MODULES_DIR = cls.temp_dir.name

        server_class = getattr(http.server, "ThreadingHTTPServer", http.server.HTTPServer)
        cls.server = server_class(("127.0.0.1", 5001), c2_listener.C2Handler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        cls.base_url = "http://127.0.0.1:5001"

    @classmethod
    def tearDownClass(cls):
        c2_listener.MODULES_DIR = cls.old_modules_dir
        c2_listener.SOVEREIGN_SECRET_KEY = cls.old_secret
        cls.server.shutdown()
        cls.server.server_close()
        cls.temp_dir.cleanup()

    def _send_post(self, path, payload, headers=None):
        if isinstance(payload, bytes):
            data = payload
        elif isinstance(payload, str):
            data = payload.encode("utf-8")
        else:
            data = json.dumps(payload).encode("utf-8")

        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)

        req = urllib.request.Request(f"{self.base_url}{path}", data=data, headers=req_headers)
        try:
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8")), resp.headers
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8")), e.headers

    def test_telemetry_logged_default(self):
        status, data, _ = self._send_post("/omni-listener", {"directive": "hello world"})
        self.assertEqual(status, 200)
        self.assertEqual(data.get("status"), "ACK")
        self.assertEqual(data.get("action"), "TELEMETRY_LOGGED")

    def test_recursive_simulation(self):
        status, data, _ = self._send_post("/omni-listener", {"directive": "[DIRECTIVE: RECURSIVE SIMULATION]"})
        self.assertEqual(status, 200)
        self.assertEqual(data.get("status"), "ACK")
        self.assertEqual(data.get("action"), "RECURSIVE_SIMULATION_UPDATED")
        self.assertEqual(data.get("simulation_cycles"), 3)

    def test_recursive_simulation_force_fail(self):
        status, data, _ = self._send_post("/omni-listener", {"directive": "[DIRECTIVE: RECURSIVE force_fail]"})
        self.assertEqual(status, 200)
        self.assertEqual(data.get("status"), "ESCALATION_REQUIRED")
        self.assertEqual(data.get("action"), "ESCALATED_TO_ALPHA")

    def test_not_found_endpoint(self):
        status, data, _ = self._send_post("/invalid-endpoint", {"directive": "test"})
        self.assertEqual(status, 404)
        self.assertIn("error", data)

    def test_health_check(self):
        req = urllib.request.Request(f"{self.base_url}/health")
        with urllib.request.urlopen(req, timeout=3) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "ONLINE")
            self.assertEqual(data.get("service"), "OMEGA_C2_LISTENER")
            self.assertEqual(data.get("version"), "3.3.0")
            self.assertEqual(data.get("node"), "TELUK_INTAN_EDGE_01")
            self.assertEqual(data.get("architecture"), "TesseraQS Core")
            self.assertIn("timestamp", data)
            self.assertIn("uptime_seconds", data)

    def test_status_check(self):
        req = urllib.request.Request(f"{self.base_url}/status")
        with urllib.request.urlopen(req, timeout=3) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "ONLINE")

        req_head = urllib.request.Request(f"{self.base_url}/status", method="HEAD")
        with urllib.request.urlopen(req_head, timeout=3) as resp:
            self.assertEqual(resp.status, 200)

    def test_metrics_prometheus_endpoint(self):
        req = urllib.request.Request(f"{self.base_url}/metrics")
        with urllib.request.urlopen(req, timeout=3) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn("text/plain", resp.headers.get("Content-Type", ""))
            content = resp.read().decode("utf-8")
            self.assertIn("omega_c2_uptime_seconds", content)
            self.assertIn("omega_c2_requests_total", content)
            self.assertIn("omega_c2_telemetry_total", content)

    def test_telemetry_stats_endpoint(self):
        req = urllib.request.Request(f"{self.base_url}/telemetry/stats")
        with urllib.request.urlopen(req, timeout=3) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "ONLINE")
            self.assertIn("metrics", data)
            self.assertIn("intents_executed", data["metrics"])

    def test_options_cors(self):
        req = urllib.request.Request(f"{self.base_url}/omni-listener", method="OPTIONS")
        with urllib.request.urlopen(req, timeout=3) as resp:
            self.assertEqual(resp.status, 204)
            self.assertEqual(resp.headers.get("Access-Control-Allow-Origin"), "*")
            self.assertIn("X-Sovereign-Signature", resp.headers.get("Access-Control-Allow-Headers", ""))

    def test_head_request(self):
        req = urllib.request.Request(f"{self.base_url}/health", method="HEAD")
        with urllib.request.urlopen(req, timeout=3) as resp:
            self.assertEqual(resp.status, 200)

        req_metrics = urllib.request.Request(f"{self.base_url}/metrics", method="HEAD")
        with urllib.request.urlopen(req_metrics, timeout=3) as resp:
            self.assertEqual(resp.status, 200)

        req_404 = urllib.request.Request(f"{self.base_url}/notfound", method="HEAD")
        try:
            urllib.request.urlopen(req_404, timeout=3)
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 404)

    def test_unsupported_methods(self):
        for method in ["PUT", "DELETE", "PATCH"]:
            req = urllib.request.Request(f"{self.base_url}/health", method=method)
            try:
                urllib.request.urlopen(req, timeout=3)
            except urllib.error.HTTPError as e:
                self.assertEqual(e.code, 405)
                data = json.loads(e.read().decode("utf-8"))
                self.assertEqual(data.get("error"), "Method Not Allowed")

    def test_purge_intent(self):
        dummy_file = os.path.join(c2_listener.MODULES_DIR, "infografik_gambarajah_interaktif_modul_101.html")
        with open(dummy_file, "w") as f:
            f.write("test content")

        status, data, _ = self._send_post("/omni-listener", {"directive": "purge modul legasi"})
        self.assertEqual(status, 200)
        self.assertEqual(data.get("action"), "PURGE_EXECUTED")
        self.assertFalse(os.path.exists(dummy_file))

    def test_repair_intent(self):
        idx_path = os.path.join(c2_listener.MODULES_DIR, "index.html")
        sub_dir = os.path.join(c2_listener.MODULES_DIR, "sub_module")
        os.makedirs(sub_dir, exist_ok=True)
        sub_html = os.path.join(sub_dir, "page.html")

        with open(idx_path, "w") as f:
            f.write('<script src="https://cdn.tailwindcss.com"></script>')
        with open(sub_html, "w") as f:
            f.write('<script src="http://cdn.tailwindcss.com"></script>')

        status, data, _ = self._send_post("/omni-listener", {"directive": "repair airgap"})
        self.assertEqual(status, 200)
        self.assertEqual(data.get("action"), "AUDIT_AND_HEAL_COMPLETE")
        self.assertGreaterEqual(data.get("patched_count", 0), 2)
        self.assertIn("timestamp", data)

        with open(idx_path, "r") as f:
            self.assertIn('/tailwind.js', f.read())
        with open(sub_html, "r") as f:
            self.assertIn('/tailwind.js', f.read())

    def test_hmac_signature_verification(self):
        secret_key = "sovereign_ultra_secure_key"
        c2_listener.SOVEREIGN_SECRET_KEY = secret_key
        try:
            payload = {"directive": "sovereign signed intent"}
            payload_bytes = json.dumps(payload).encode("utf-8")
            valid_sig = hmac.new(secret_key.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()

            # 1. Valid Signature -> 200 OK
            status, data, _ = self._send_post(
                "/omni-listener",
                payload,
                headers={"X-Sovereign-Signature": valid_sig}
            )
            self.assertEqual(status, 200)
            self.assertEqual(data.get("status"), "ACK")

            # 2. Invalid Signature -> 401 Unauthorized
            status, data, _ = self._send_post(
                "/omni-listener",
                payload,
                headers={"X-Sovereign-Signature": "invalid_hex_signature"}
            )
            self.assertEqual(status, 401)
            self.assertEqual(data.get("error"), "Unauthorized")

            # 3. Missing Signature -> 401 Unauthorized
            status, data, _ = self._send_post("/omni-listener", payload)
            self.assertEqual(status, 401)
        finally:
            c2_listener.SOVEREIGN_SECRET_KEY = ""

    def test_tessera_cli_helper(self):
        test_payload = b'{"hello": "world"}'
        sig = tessera_cli.compute_signature(test_payload, "testkey")
        self.assertTrue(len(sig) > 0)
        self.assertEqual(tessera_cli.compute_signature(test_payload, ""), "")

    def test_tessera_cli_audit_and_version(self):
        # Test CLI audit function directly
        class Args:
            pass
        args = Args()
        # Should complete without error when all sovereign files exist
        tessera_cli.cmd_audit(args)

    def test_tessera_cli_audit_detects_missing_file(self):
        # Verify that cmd_audit detects missing defense artifacts (e.g. ca.crt)
        class Args:
            pass
        args = Args()
        import io
        import sys
        from unittest.mock import patch

        with patch("os.path.exists", side_effect=lambda f: f != "ca.crt"):
            with patch("sys.stderr", new=io.StringIO()):
                with self.assertRaises(SystemExit) as cm:
                    tessera_cli.cmd_audit(args)
                self.assertEqual(cm.exception.code, 1)

    def test_openapi_security_schemes(self):
        with open("openapi.json", "r", encoding="utf-8") as f:
            spec = json.load(f)
        self.assertIn("securitySchemes", spec.get("components", {}))
        self.assertIn("SovereignSignature", spec["components"]["securitySchemes"])
        self.assertEqual(spec["components"]["securitySchemes"]["SovereignSignature"]["name"], "X-Sovereign-Signature")
        omni_post = spec["paths"]["/omni-listener"]["post"]
        self.assertIn("security", omni_post)

    def test_sovereign_ca_certificate(self):
        # Verify ca.crt exists, is non-empty, and contains valid PEM certificate markers
        self.assertTrue(os.path.exists("ca.crt"))
        with open("ca.crt", "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("-----BEGIN CERTIFICATE-----", content)
        self.assertIn("-----END CERTIFICATE-----", content)

    def test_tessera_cli_argument_parsing(self):
        import sys
        old_argv = sys.argv

        try:
            # 1. Global flag placement
            sys.argv = ["tessera_cli.py", "--base-url", "http://127.0.0.1:5001", "audit"]
            tessera_cli.main()

            # 2. Subcommand flag placement
            sys.argv = ["tessera_cli.py", "audit", "--base-url", "http://127.0.0.1:5001"]
            tessera_cli.main()
        finally:
            sys.argv = old_argv

    def test_metrics_head_request(self):
        req_metrics = urllib.request.Request(f"{self.base_url}/metrics", method="HEAD")
        with urllib.request.urlopen(req_metrics, timeout=3) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn("text/plain", resp.headers.get("Content-Type", ""))

        req_stats = urllib.request.Request(f"{self.base_url}/telemetry/stats", method="HEAD")
        with urllib.request.urlopen(req_stats, timeout=3) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn("application/json", resp.headers.get("Content-Type", ""))

    def test_non_dict_json(self):
        status, data, _ = self._send_post("/omni-listener", [1, 2, 3])
        self.assertEqual(status, 200)
        self.assertEqual(data.get("status"), "ACK")

    def test_malformed_json(self):
        status, data, _ = self._send_post("/omni-listener", "{invalid json")
        self.assertEqual(status, 200)
        self.assertEqual(data.get("status"), "ACK")

    def test_invalid_content_length(self):
        status, data, _ = self._send_post("/omni-listener", {"directive": "test"}, headers={"Content-Length": "invalid"})
        self.assertEqual(status, 200)

    def test_payload_too_large(self):
        old_limit = c2_listener.MAX_PAYLOAD_SIZE
        try:
            c2_listener.MAX_PAYLOAD_SIZE = 50  # set small limit for test
            large_payload = {"directive": "x" * 100}
            status, data, _ = self._send_post("/omni-listener", large_payload)
            self.assertEqual(status, 413)
            self.assertEqual(data.get("error"), "Payload Terlalu Besar")
        finally:
            c2_listener.MAX_PAYLOAD_SIZE = old_limit

    def test_concurrent_requests(self):
        results = []

        def make_req():
            status, data, _ = self._send_post("/omni-listener", {"directive": "concurrent request"})
            results.append(status)

        threads = [threading.Thread(target=make_req) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(results), 5)
        self.assertTrue(all(s == 200 for s in results))

    def test_is_safe_path(self):
        self.assertTrue(c2_listener.is_safe_path(c2_listener.MODULES_DIR, os.path.join(c2_listener.MODULES_DIR, "index.html")))
        unsafe_path = os.path.join(c2_listener.MODULES_DIR, "..", "c2_listener.py")
        self.assertFalse(c2_listener.is_safe_path(c2_listener.MODULES_DIR, unsafe_path))

        # Test prefix collision bypass prevention (e.g. /modules vs /modules_extra)
        sibling_prefix_path = c2_listener.MODULES_DIR.rstrip("/\\") + "_extra"
        self.assertFalse(c2_listener.is_safe_path(c2_listener.MODULES_DIR, sibling_prefix_path))

    def test_sitemap_and_page_links_integrity(self):
        # Verify that all URLs listed in sitemap.xml correspond to files present in repo
        self.assertTrue(os.path.exists("sitemap.xml"))
        with open("sitemap.xml", "r", encoding="utf-8") as f:
            sitemap_content = f.read()

        import xml.etree.ElementTree as ET
        root = ET.fromstring(sitemap_content)
        namespace = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [elem.text for elem in root.findall(".//ns:loc", namespace)]
        self.assertGreater(len(locs), 0)

        # Check each loc maps to valid local artifact
        base = "https://tesseraqs.cloud-ip.cc/"
        for loc in locs:
            self.assertTrue(loc.startswith(base))
            rel_path = loc[len(base):]
            if not rel_path or rel_path == "":
                local_file = "index.html"
            else:
                local_file = rel_path
            self.assertTrue(os.path.exists(local_file), f"Sitemap URL missing local artifact: {local_file}")

        # Check that index.html contains footer links
        with open("index.html", "r", encoding="utf-8") as f:
            idx = f.read()
        self.assertIn("security.html", idx)
        self.assertIn("privacy.html", idx)
        self.assertIn("terms.html", idx)
        self.assertIn("openapi.json", idx)
        self.assertIn("portal.html", idx)
        self.assertIn("research.html", idx)

        # Check newly created pages exist and contain cross links
        for page in ["portal.html", "research.html", "security.html", "privacy.html", "terms.html"]:
            self.assertTrue(os.path.exists(page), f"Page {page} does not exist")
            with open(page, "r", encoding="utf-8") as pf:
                content = pf.read()
                self.assertIn("index.html", content)

if __name__ == "__main__":
    unittest.main()
