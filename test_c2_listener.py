import unittest
import http.server
import threading
import json
import os
import tempfile
import urllib.request
import urllib.error
import c2_listener

class TestC2Listener(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory for MODULES_DIR testing
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.old_modules_dir = c2_listener.MODULES_DIR
        c2_listener.MODULES_DIR = cls.temp_dir.name

        server_class = getattr(http.server, "ThreadingHTTPServer", http.server.HTTPServer)
        cls.server = server_class(("127.0.0.1", 5001), c2_listener.C2Handler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        cls.base_url = "http://127.0.0.1:5001"

    @classmethod
    def tearDownClass(cls):
        c2_listener.MODULES_DIR = cls.old_modules_dir
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
            self.assertEqual(data.get("version"), "3.2.0")
            self.assertEqual(data.get("node"), "TELUK_INTAN_EDGE_01")
            self.assertEqual(data.get("architecture"), "TesseraQS Core")

    def test_options_cors(self):
        req = urllib.request.Request(f"{self.base_url}/omni-listener", method="OPTIONS")
        with urllib.request.urlopen(req, timeout=3) as resp:
            self.assertEqual(resp.status, 204)
            self.assertEqual(resp.headers.get("Access-Control-Allow-Origin"), "*")

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
        with open(idx_path, "w") as f:
            f.write('<script src="https://cdn.tailwindcss.com"></script>')

        status, data, _ = self._send_post("/omni-listener", {"directive": "repair airgap"})
        self.assertEqual(status, 200)
        self.assertEqual(data.get("action"), "AUDIT_AND_HEAL_COMPLETE")
        with open(idx_path, "r") as f:
            content = f.read()
        self.assertIn('/tailwind.js', content)

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

if __name__ == "__main__":
    unittest.main()
