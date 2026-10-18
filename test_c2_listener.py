import unittest
import http.server
import threading
import json
import urllib.request
import urllib.error
import c2_listener

class TestC2Listener(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start server in thread
        cls.server = http.server.HTTPServer(("127.0.0.1", 5001), c2_listener.C2Handler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        cls.base_url = "http://127.0.0.1:5001"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def _send_post(self, path, payload):
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(f"{self.base_url}{path}", data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode("utf-8"))

    def test_telemetry_logged_default(self):
        status, data = self._send_post("/omni-listener", {"directive": "hello world"})
        self.assertEqual(status, 200)
        self.assertEqual(data.get("status"), "ACK")
        self.assertEqual(data.get("action"), "TELEMETRY_LOGGED")

    def test_recursive_simulation(self):
        status, data = self._send_post("/omni-listener", {"directive": "[DIRECTIVE: RECURSIVE SIMULATION]"})
        self.assertEqual(status, 200)
        self.assertEqual(data.get("status"), "ACK")
        self.assertEqual(data.get("action"), "RECURSIVE_SIMULATION_UPDATED")
        self.assertEqual(data.get("simulation_cycles"), 3)

    def test_recursive_simulation_force_fail(self):
        status, data = self._send_post("/omni-listener", {"directive": "[DIRECTIVE: RECURSIVE force_fail]"})
        self.assertEqual(status, 200)
        self.assertEqual(data.get("status"), "ESCALATION_REQUIRED")
        self.assertEqual(data.get("action"), "ESCALATED_TO_ALPHA")

    def test_not_found_endpoint(self):
        status, data = self._send_post("/invalid-endpoint", {"directive": "test"})
        self.assertEqual(status, 404)
        self.assertIn("error", data)

if __name__ == "__main__":
    unittest.main()
