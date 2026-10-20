import unittest

from src.extraction import (masquer_secrets, normaliser_log,
                            normaliser_pipeline, normaliser_scan)

LIGNE = "2026-10-05 10:02:11 ERROR backend OOMKilled restarts=14 password=abc123"


class TestExtraction(unittest.TestCase):
    def test_masquer_secrets(self):
        self.assertEqual(masquer_secrets("user=bob password=abc123"),
                         "user=bob password=[SECRET]")

    def test_masquer_casse_et_deux_points(self):
        self.assertEqual(masquer_secrets("API_KEY: xyz&a=1"), "API_KEY: [SECRET]&a=1")

    def test_masquer_plusieurs(self):
        self.assertEqual(masquer_secrets("token=a, secret=b"),
                         "token=[SECRET], secret=[SECRET]")

    def test_normaliser_log(self):
        evt = normaliser_log(LIGNE, 42)
        self.assertEqual(evt.id, "EVT-00042")
        self.assertEqual(evt.timestamp, "2026-10-05T10:02:11Z")
        self.assertEqual(evt.severity, "HIGH")
        self.assertEqual(evt.component, "backend")
        self.assertEqual(evt.event_type, "LOG")
        self.assertNotIn("abc123", evt.message)

    def test_severites_log(self):
        base = "2026-10-05 10:00:00 {} backend msg"
        for niveau, attendu in [("FATAL", "CRITICAL"), ("critical", "CRITICAL"),
                                ("WARN", "MEDIUM"), ("warning", "MEDIUM"),
                                ("INFO", "LOW"), ("DEBUG", "LOW")]:
            self.assertEqual(normaliser_log(base.format(niveau), 1).severity, attendu)

    def test_log_invalide(self):
        with self.assertRaises(ValueError):
            normaliser_log("2026-10-05 10:00:00 ERROR backend", 1)

    def test_normaliser_scan(self):
        evt = normaliser_scan({"cve": "CVE-1", "package": "lib", "severity": "critical",
                               "date": "2026-10-05T10:07:00Z"}, 7)
        self.assertEqual(evt.source, "TRIVY")
        self.assertEqual(evt.severity, "CRITICAL")
        self.assertEqual(evt.event_type, "VULNERABILITY")
        self.assertEqual(evt.message, "Vulnerabilite CVE-1 dans lib")

    def test_scan_severite_inconnue_et_cle_manquante(self):
        evt = normaliser_scan({"cve": "C", "package": "p", "severity": "bizarre",
                               "date": "d"}, 1)
        self.assertEqual(evt.severity, "LOW")
        with self.assertRaises(ValueError):
            normaliser_scan({"cve": "C"}, 1)

    def test_normaliser_pipeline(self):
        evt = normaliser_pipeline({"job": "build", "status": "FAILED", "date": "d"}, 3)
        self.assertEqual(evt.event_type, "PIPELINE_FAILURE")
        self.assertEqual(evt.severity, "HIGH")
        self.assertEqual(evt.message, "Pipeline build : FAILED")
        ok = normaliser_pipeline({"job": "build", "status": "success", "date": "d"}, 4)
        self.assertEqual(ok.event_type, "PIPELINE_OK")
        self.assertEqual(ok.severity, "LOW")

    def test_pipeline_cle_manquante(self):
        with self.assertRaises(ValueError):
            normaliser_pipeline({"job": "x"}, 1)


if __name__ == "__main__":
    unittest.main()